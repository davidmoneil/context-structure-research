#!/usr/bin/env python3
"""
Phase 2: Statistical Significance Analysis

Computes bootstrap confidence intervals, pairwise permutation tests, and
tier groupings to determine which strategy ranking differences are real.

Input:  results/phase2/analysis/results.json (1323 scored tests)
Output: results/phase2/analysis/significance-report.md
"""

import json
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_JSON = PROJECT_ROOT / "results" / "phase2" / "analysis" / "results.json"
OUTPUT_DIR = PROJECT_ROOT / "results" / "phase2" / "analysis"

SEED = 42
N_BOOTSTRAP = 10_000
N_PERMUTATIONS = 10_000
ALPHA = 0.05

OVERFLOW_STRATEGIES = {"C1", "R2.1", "R2.2", "R2.3", "R2.4"}


def load_results():
    with open(RESULTS_JSON) as f:
        return json.load(f)


def group_scores(data):
    """Group scores by strategy, keyed by (dataset, question_id) for pairing."""
    by_strategy = defaultdict(dict)
    for s in data["scores"]:
        key = (s["dataset"], s["question_id"])
        by_strategy[s["strategy"]][key] = s["points"]
    return by_strategy


def bootstrap_ci(scores, n_boot=N_BOOTSTRAP, seed=SEED):
    """Compute 95% bootstrap confidence interval for the mean."""
    rng = random.Random(seed)
    n = len(scores)
    means = []
    for _ in range(n_boot):
        sample = [scores[rng.randint(0, n - 1)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(n_boot * 0.025)]
    hi = means[int(n_boot * 0.975)]
    return lo, hi


def paired_permutation_test(scores_a, scores_b, keys, n_perm=N_PERMUTATIONS, seed=SEED):
    """Two-sided paired permutation test. Returns p-value."""
    rng = random.Random(seed)
    paired = [(scores_a[k], scores_b[k]) for k in keys]
    diffs = [a - b for a, b in paired]
    observed = abs(sum(diffs) / len(diffs))

    count = 0
    for _ in range(n_perm):
        perm_mean = 0.0
        for d in diffs:
            if rng.random() < 0.5:
                perm_mean += d
            else:
                perm_mean -= d
        perm_mean = abs(perm_mean / len(diffs))
        if perm_mean >= observed:
            count += 1

    return count / n_perm


def compute_tiers(ranked, cis, pairwise_pvals):
    """Group strategies into tiers of statistically indistinguishable performance.

    Two strategies are in the same tier if their CIs overlap AND the
    pairwise permutation test between them is not significant (p > ALPHA).
    We walk down the ranking: each new strategy joins the current tier
    if it's indistinguishable from the tier's top member.
    """
    tiers = []
    current_tier = [ranked[0][0]]
    tier_top = ranked[0][0]  # best in current tier

    for i in range(1, len(ranked)):
        strat = ranked[i][0]
        top_ci = cis[tier_top]
        strat_ci = cis[strat]
        ci_overlap = strat_ci[1] >= top_ci[0] and top_ci[1] >= strat_ci[0]

        # Check pairwise test between this strategy and tier top
        pair_key = (tier_top, strat)
        reverse_key = (strat, tier_top)
        p = pairwise_pvals.get(pair_key) or pairwise_pvals.get(reverse_key)

        if ci_overlap and p is not None and p > ALPHA:
            current_tier.append(strat)
        else:
            tiers.append(current_tier)
            current_tier = [strat]
            tier_top = strat

    tiers.append(current_tier)
    return tiers


def generate_report(by_strategy):
    """Generate the full significance report."""
    # Separate overflow from working strategies
    working = {k: v for k, v in by_strategy.items() if k not in OVERFLOW_STRATEGIES}
    overflow = {k: v for k, v in by_strategy.items() if k in OVERFLOW_STRATEGIES}

    # Compute means
    means = {}
    for strat, scores_dict in working.items():
        vals = list(scores_dict.values())
        means[strat] = sum(vals) / len(vals)

    # Rank by mean accuracy (descending)
    ranked = sorted(means.items(), key=lambda x: x[1], reverse=True)

    # Bootstrap CIs for all working strategies
    cis = {}
    for strat, scores_dict in working.items():
        vals = list(scores_dict.values())
        cis[strat] = bootstrap_ci(vals)

    # Per-dataset CIs
    dataset_cis = defaultdict(dict)
    for strat, scores_dict in working.items():
        by_ds = defaultdict(list)
        for (ds, _qid), pts in scores_dict.items():
            by_ds[ds].append(pts)
        for ds, vals in by_ds.items():
            ds_mean = sum(vals) / len(vals)
            ds_ci = bootstrap_ci(vals)
            dataset_cis[strat][ds] = (ds_mean, ds_ci)

    # Common keys for pairing
    ref_keys = set(list(working.values())[0].keys())

    # Pairwise permutation tests — adjacent ranks AND all pairs needed for tiers
    # First do adjacent pairs
    adjacent_pvals = {}
    for i in range(len(ranked) - 1):
        s1 = ranked[i][0]
        s2 = ranked[i + 1][0]
        p = paired_permutation_test(working[s1], working[s2], ref_keys)
        adjacent_pvals[(s1, s2)] = p

    # For tier computation, we need pairwise tests between tier-top and each
    # subsequent strategy. We'll compute these on-demand during tier building.
    # Pre-compute all pairwise tests between any strategy pairs that might
    # share a tier. We do this greedily: walk down ranks, test against tier top.
    all_pvals = dict(adjacent_pvals)
    # Build tiers with on-demand computation
    tiers = []
    current_tier = [ranked[0][0]]
    tier_top = ranked[0][0]

    for i in range(1, len(ranked)):
        strat = ranked[i][0]
        top_ci = cis[tier_top]
        strat_ci = cis[strat]
        ci_overlap = strat_ci[1] >= top_ci[0] and top_ci[1] >= strat_ci[0]

        pair_key = (tier_top, strat)
        if ci_overlap:
            if pair_key not in all_pvals:
                p = paired_permutation_test(working[tier_top], working[strat], ref_keys)
                all_pvals[pair_key] = p
            p = all_pvals[pair_key]
            if p > ALPHA:
                current_tier.append(strat)
            else:
                tiers.append(current_tier)
                current_tier = [strat]
                tier_top = strat
        else:
            tiers.append(current_tier)
            current_tier = [strat]
            tier_top = strat

    tiers.append(current_tier)

    # Build report
    lines = []
    lines.append("# Phase 2: Statistical Significance Report")
    lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Method**: Bootstrap CIs ({N_BOOTSTRAP:,} resamples) + paired permutation tests ({N_PERMUTATIONS:,} permutations)")
    lines.append(f"**Seed**: {SEED} (reproducible)")
    lines.append(f"**Significance level**: {ALPHA}")
    lines.append("")

    # Section 1: Rankings with CIs
    lines.append("## 1. Strategy Rankings with 95% Confidence Intervals")
    lines.append("")
    lines.append("| Rank | Strategy | Accuracy | CI Lower | CI Upper | CI Width |")
    lines.append("|------|----------|----------|----------|----------|----------|")
    for i, (strat, mean) in enumerate(ranked, 1):
        lo, hi = cis[strat]
        width = hi - lo
        lines.append(f"| {i} | {strat} | {mean:.1%} | {lo:.1%} | {hi:.1%} | {width:.1%} |")
    lines.append("")

    # Section 2: Tier groupings
    lines.append("## 2. Statistical Tier Groupings")
    lines.append("")
    lines.append("Strategies within a tier are **statistically indistinguishable** (overlapping 95% CIs")
    lines.append("and pairwise permutation test p > 0.05 against tier leader).")
    lines.append("")
    for t_idx, tier in enumerate(tiers, 1):
        tier_means = [means[s] for s in tier]
        lo = min(tier_means)
        hi = max(tier_means)
        strat_list = ", ".join(tier)
        lines.append(f"**Tier {t_idx}** ({lo:.1%}–{hi:.1%}): {strat_list}")
        lines.append("")

    # Overflow tier
    if overflow:
        overflow_list = ", ".join(sorted(overflow.keys()))
        lines.append(f"**Overflow Tier** (0.0%): {overflow_list}")
        lines.append("*(Excluded from pairwise tests — context window overflow caused 0% accuracy)*")
        lines.append("")

    # Section 3: Adjacent pairwise tests
    lines.append("## 3. Pairwise Significance Between Adjacent Ranks")
    lines.append("")
    lines.append("| Rank | Strategy A | Strategy B | Delta | p-value | Significant? |")
    lines.append("|------|------------|------------|-------|---------|--------------|")
    for i in range(len(ranked) - 1):
        s1 = ranked[i][0]
        s2 = ranked[i + 1][0]
        delta = means[s1] - means[s2]
        p = adjacent_pvals[(s1, s2)]
        sig = "Yes" if p < ALPHA else "No"
        lines.append(f"| {i + 1}→{i + 2} | {s1} | {s2} | {delta:.1%} | {p:.4f} | {sig} |")
    lines.append("")

    sig_count = sum(1 for p in adjacent_pvals.values() if p < ALPHA)
    lines.append(f"**{sig_count}/{len(adjacent_pvals)}** adjacent pairs show statistically significant differences.")
    lines.append("")

    # Section 4: Per-dataset CIs
    lines.append("## 4. Per-Dataset Confidence Intervals")
    lines.append("")
    for ds in ["soong-v5", "obsidian"]:
        lines.append(f"### {ds}")
        lines.append("")
        lines.append("| Rank | Strategy | Accuracy | CI Lower | CI Upper |")
        lines.append("|------|----------|----------|----------|----------|")
        ds_ranked = sorted(
            [(s, dataset_cis[s][ds]) for s in working if ds in dataset_cis[s]],
            key=lambda x: x[1][0], reverse=True
        )
        for i, (strat, (mean, (lo, hi))) in enumerate(ds_ranked, 1):
            lines.append(f"| {i} | {strat} | {mean:.1%} | {lo:.1%} | {hi:.1%} |")
        lines.append("")

    # Section 5: Methodology
    lines.append("## 5. Methodology")
    lines.append("")
    lines.append(f"- **Bootstrap confidence intervals**: {N_BOOTSTRAP:,} resamples with replacement, percentile method (2.5th–97.5th)")
    lines.append(f"- **Paired permutation test**: {N_PERMUTATIONS:,} permutations, two-sided, paired by (dataset, question_id)")
    lines.append(f"- **Sample size**: {len(ref_keys)} paired observations per strategy")
    lines.append(f"- **Random seed**: {SEED} (all results reproducible)")
    lines.append(f"- **Tier formation**: Walk down rankings; a strategy joins the current tier if its CI overlaps the tier leader's CI AND their permutation test p > {ALPHA}")
    lines.append(f"- **Overflow strategies excluded**: {', '.join(sorted(OVERFLOW_STRATEGIES))} (0% accuracy due to context overflow)")
    lines.append(f"- **Total strategies analyzed**: {len(working)} working + {len(overflow)} overflow")
    lines.append("")

    return "\n".join(lines), tiers, ranked, cis, means


def main():
    data = load_results()
    by_strategy = group_scores(data)
    report, tiers, ranked, cis, means = generate_report(by_strategy)

    output_path = OUTPUT_DIR / "significance-report.md"
    output_path.write_text(report)
    print(f"Report written to: {output_path}")

    # Summary to stdout
    print(f"\nStrategy Rankings ({len(ranked)} working strategies):")
    for i, (strat, mean) in enumerate(ranked, 1):
        lo, hi = cis[strat]
        print(f"  {i:2d}. {strat:20s} {mean:.1%}  [{lo:.1%} – {hi:.1%}]")

    print(f"\nTier Groupings:")
    for t_idx, tier in enumerate(tiers, 1):
        tier_strats = ", ".join(tier)
        tier_range = f"{min(means[s] for s in tier):.1%}–{max(means[s] for s in tier):.1%}"
        print(f"  Tier {t_idx} ({tier_range}): {tier_strats}")


if __name__ == "__main__":
    main()
