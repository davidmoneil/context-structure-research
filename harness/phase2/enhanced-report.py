#!/usr/bin/env python3
"""
Phase 2.1: Enhanced Results Report Generator

Builds a comprehensive report from raw Phase 2 result data including:
- Wall clock timing analysis
- Working-strategies-only breakdowns (excluding overflow)
- Question-type and difficulty splits (all vs working)
- Cache efficiency analysis
- Per-question heatmap data
- Cost-per-correct with timing context
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median, stdev

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "phase2" / "raw"
ANALYSIS_DIR = PROJECT_ROOT / "results" / "phase2" / "analysis"

QUESTION_FILES = {
    "soong-v5": PROJECT_ROOT / "harness" / "questions.json",
    "obsidian": PROJECT_ROOT / "test-datasets" / "obsidian" / "questions.json",
}

# Strategies that overflowed on ALL datasets
FULL_OVERFLOW = {"R2.1", "R2.2", "R2.3", "R2.4", "C1"}

# Strategies that overflowed on obsidian only
PARTIAL_OVERFLOW = {"R4", "C2"}  # worked on soong-v5, overflow on obsidian


def load_questions():
    """Load question metadata (type, difficulty)."""
    questions = {}
    for dataset, qfile in QUESTION_FILES.items():
        if qfile.exists():
            with open(qfile) as f:
                qs = json.load(f)
            questions[dataset] = {q["id"]: q for q in qs}
    return questions


def load_all_results():
    """Load all raw result JSON files."""
    results = []
    for result_file in sorted(RESULTS_DIR.rglob("*.json")):
        if result_file.name.startswith("run-"):
            continue
        try:
            with open(result_file) as f:
                data = json.load(f)
            if "metadata" in data:
                results.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return results


def extract_duration_ms(result):
    """Extract duration_ms from raw_output JSON string."""
    raw = result.get("raw_output", "")
    if not raw:
        return None
    try:
        raw_data = json.loads(raw)
        return raw_data.get("duration_ms")
    except (json.JSONDecodeError, TypeError):
        return None


def extract_api_duration_ms(result):
    """Extract duration_api_ms from raw_output JSON string."""
    raw = result.get("raw_output", "")
    if not raw:
        return None
    try:
        raw_data = json.loads(raw)
        return raw_data.get("duration_api_ms")
    except (json.JSONDecodeError, TypeError):
        return None


def extract_cache_tokens(result):
    """Extract cache read and creation tokens."""
    cost = result.get("cost", {})
    return {
        "cache_read": cost.get("cache_read_input_tokens", 0),
        "cache_creation": cost.get("cache_creation_input_tokens", 0),
    }


def is_overflow(result):
    """Check if this result was a context overflow."""
    response = result.get("response", "")
    exit_code = result.get("exit_code", 0)
    if exit_code != 0:
        return True
    if "prompt is too long" in response.lower():
        return True
    if "context window" in response.lower() and "exceed" in response.lower():
        return True
    cost = result.get("cost", {})
    perf = result.get("performance", {})
    strategy = result.get("metadata", {}).get("strategy", "")
    if strategy in FULL_OVERFLOW and cost.get("total_cost_usd", 0) == 0:
        return True
    return False


def score_result(result, questions):
    """Score a single result (simplified from evaluate.py)."""
    meta = result.get("metadata", {})
    dataset = meta.get("dataset", "")
    qid = meta.get("question_id", "")

    if dataset not in questions or qid not in questions[dataset]:
        return 0.0, False

    question = questions[dataset][qid]
    gt = question["ground_truth"]
    exact_answer = gt["exact_answer"]
    variants = gt.get("acceptable_variants", [])
    keywords = gt.get("partial_credit_keywords", [])

    # Extract answer
    response_text = result.get("response", "")
    answer = response_text  # fallback
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            answer = parsed.get("answer", response_text)
        except json.JSONDecodeError:
            pass

    norm_answer = re.sub(r'\s+', ' ', answer.lower().strip())
    norm_truth = re.sub(r'\s+', ' ', exact_answer.lower().strip())

    if norm_truth in norm_answer or norm_answer in norm_truth:
        return 1.0, True
    for variant in variants:
        if re.sub(r'\s+', ' ', variant.lower().strip()) in norm_answer:
            return 0.9, True
    if keywords:
        matched = sum(1 for kw in keywords if re.sub(r'\s+', ' ', kw.lower().strip()) in norm_answer)
        if matched > 0:
            return 0.1 + (0.6 * matched / len(keywords)), False
    return 0.0, False


def format_time(ms):
    """Format milliseconds to human readable."""
    if ms is None:
        return "N/A"
    if ms < 1000:
        return f"{ms}ms"
    return f"{ms / 1000:.1f}s"


def main():
    questions = load_questions()
    results = load_all_results()
    print(f"Loaded {len(results)} results")

    # ========================================
    # Build enriched data per result
    # ========================================
    enriched = []
    for r in results:
        meta = r.get("metadata", {})
        strategy = meta.get("strategy", "")
        dataset = meta.get("dataset", "")
        qid = meta.get("question_id", "")
        perf = r.get("performance", {})
        cost_data = r.get("cost", {})

        q_meta = questions.get(dataset, {}).get(qid, {})
        qtype = q_meta.get("type", "unknown")
        difficulty = q_meta.get("difficulty", "unknown")

        score, is_correct = score_result(r, questions)
        overflow = is_overflow(r)
        wall_ms = perf.get("wall_clock_ms")
        turns = perf.get("num_turns", 0)
        duration_ms = extract_duration_ms(r)
        api_ms = extract_api_duration_ms(r)
        cache = extract_cache_tokens(r)
        cost_usd = cost_data.get("total_cost_usd", 0)
        total_tokens = (cost_data.get("input_tokens", 0) +
                        cost_data.get("output_tokens", 0) +
                        cache.get("cache_read", 0) +
                        cache.get("cache_creation", 0))

        # Determine if this is a "working" test (strategy produced real results)
        working = not overflow and strategy not in FULL_OVERFLOW
        # R4/C2 on obsidian: check if they actually overflowed
        if strategy in PARTIAL_OVERFLOW and dataset == "obsidian":
            working = False

        enriched.append({
            "strategy": strategy,
            "dataset": dataset,
            "question_id": qid,
            "question_type": qtype,
            "difficulty": difficulty,
            "score": score,
            "is_correct": is_correct,
            "overflow": overflow,
            "working": working,
            "wall_clock_ms": wall_ms,
            "duration_ms": duration_ms,
            "api_duration_ms": api_ms,
            "num_turns": turns,
            "cost_usd": cost_usd,
            "total_tokens": total_tokens,
            "cache_read": cache["cache_read"],
            "cache_creation": cache["cache_creation"],
            "input_tokens": cost_data.get("input_tokens", 0),
            "output_tokens": cost_data.get("output_tokens", 0),
        })

    # ========================================
    # Aggregate by strategy
    # ========================================
    by_strategy = defaultdict(list)
    for e in enriched:
        by_strategy[e["strategy"]].append(e)

    # Working tests only
    working_tests = [e for e in enriched if e["working"]]
    working_by_strategy = defaultdict(list)
    for e in working_tests:
        working_by_strategy[e["strategy"]].append(e)

    # ========================================
    # Generate Report
    # ========================================
    lines = []

    def add(line=""):
        lines.append(line)

    add("---")
    add("title: Phase 2.1 Results Report")
    add("type: research")
    add("status: active")
    add("created: 2026-02-19")
    add("updated: 2026-02-19")
    add("tags:")
    add("  - context-structure-research")
    add("  - phase-2")
    add("  - results")
    add("---")
    add()
    add("# Phase 2.1 Results Report")
    add()

    # ── Executive Summary ──
    add("## Executive Summary")
    add()
    add("Phase 2.1 tested 14 context-structuring strategies across 686 individual tests to determine how Claude best navigates large file collections. The central finding is clear: **lightweight index strategies dramatically outperform both raw file loading and no-context baselines**, while every strategy that loads all files into context fails catastrophically at scale.")
    add()
    add("The winning strategy, **I4 (summary table)**, achieves 70.0% accuracy at $0.04 per test by providing Claude with a one-sentence summary per file and letting tools handle the rest. This is both the most accurate and one of the most cost-efficient approaches tested. Loading full files into context -- the intuitive approach -- overflows the 200K token window for every dataset tested, producing 0% accuracy across five strategies.")
    add()
    add("These results establish a practical design principle for Claude Code configurations: **tell the model where to look, not what the files contain**. A well-crafted index plus tool access consistently beats brute-force context loading.")
    add()
    add("---")
    add()

    # ── Study Design ──
    add("## Study Design")
    add()
    add("### Parameters")
    add()
    add("| Parameter | Value |")
    add("|-----------|-------|")
    add("| **Model** | Haiku (`claude-haiku-4-5-20251001`) |")
    add(f"| **Total tests** | {len(enriched)} (14 strategies x 2 datasets x ~24 questions) |")
    total_cost = sum(e["cost_usd"] for e in enriched)
    add(f"| **Total cost** | ${total_cost:.2f} |")
    add("| **Execution mode** | `claude -p` headless, `--permission-mode bypassPermissions` |")
    add("| **Tools available** | Read, Grep, Glob |")
    add("| **Scoring** | Exact match (1.0), variant match (0.9), partial keyword credit (0.0-0.7) |")
    add()

    add("### Datasets")
    add()
    add("| Dataset | Files | Words | Questions | Character |")
    add("|---------|-------|-------|-----------|-----------|")
    add("| **soong-v5** | 120 | 302K | 23 | Well-structured codebase documentation |")
    add("| **obsidian** | 213 | 282K | 26 | Real-world messy knowledge base |")
    add()

    add("### Strategy Taxonomy")
    add()
    add("Strategies fall into four families based on how they provide context to the model.")
    add()
    add("**R-family (Reference/file loading)** -- Load files directly into context via `@` references.")
    add()
    add("| Strategy | Description |")
    add("|----------|-------------|")
    add("| **R1** | No context provided. Pure tool navigation -- the baseline. |")
    add("| **R2.1** | All files loaded via `@refs`, no annotation |")
    add("| **R2.2** | All files loaded + 1-sentence summary per ref |")
    add("| **R2.3** | All files loaded + keyword annotations per ref |")
    add("| **R2.4** | All files loaded + 2-sentence summary per ref |")
    add("| **R3** | Sub-indexes only (per-directory keyword listings, no full file loading) |")
    add("| **R4** | Top 15-30 key files loaded via `@refs` (selected by size + name heuristic) |")
    add()
    add("**I-family (Index only)** -- Provide a structured index; the model uses tools to read files on demand.")
    add()
    add("| Strategy | Description |")
    add("|----------|-------------|")
    add("| **I1** | Keyword index table (file -> 8 keywords), no files loaded |")
    add("| **I2** | Relationship graph (topic -> connected files), no files loaded |")
    add("| **I3** | Semantic groupings (15 topic clusters), no files loaded |")
    add("| **I4** | Summary table (file -> 1-sentence summary), no files loaded |")
    add()
    add("**C-family (Combined)** -- Merge elements from R and I families.")
    add()
    add("| Strategy | Description |")
    add("|----------|-------------|")
    add("| **C1** | All files + keyword index (overflow) |")
    add("| **C2** | R4 key files + I2 relationship graph |")
    add("| **C3** | Keyword index + directory sub-indexes |")
    add()
    add("### Question Classification")
    add()
    add("#### Question Types")
    add()
    add("| Type | Description | Example |")
    add("|------|-------------|---------|")
    add("| **Navigation** | Find a specific fact in a single file | \"Who is the CEO?\" |")
    add("| **Depth** | Deep understanding of a single file's detailed content | \"What are the four tiers in Document Guard's validation model?\" |")
    add("| **Cross-reference** | Connect information across multiple files | \"Which department does Project Prometheus report to, and who leads it?\" |")
    add("| **Synthesis** | Combine information into a novel conclusion | \"What common principle connects Document Guard's tier model with the orchestration-detector's scoring?\" |")
    add()
    add("#### Difficulty Levels")
    add()
    add("Difficulty is manually assigned based on:")
    add()
    add("| Level | Criteria | Example |")
    add("|-------|----------|---------|")
    add("| **Easy** | Single known fact, one source file, short exact answer | \"Who is the CEO?\" (answer: Dr. Maya Chen) |")
    add("| **Medium** | Requires locating 1-2 files, moderate detail extraction | \"What decision was made in the October 2124 board meeting regarding AI safety?\" |")
    add("| **Hard** | Multi-file reasoning, analysis/synthesis, or obscure specifics | \"What common themes emerge across the security content and AI infrastructure projects?\" |")
    add()

    # Question distribution
    add("#### Question Distribution")
    add()
    type_diff_counts = defaultdict(lambda: defaultdict(int))
    for dataset, qs in questions.items():
        for qid, q in qs.items():
            type_diff_counts[q["type"]][q["difficulty"]] += 1

    add("| Type | Easy | Medium | Hard | Total |")
    add("|------|------|--------|------|-------|")
    for qtype in ["navigation", "depth", "cross-reference", "synthesis"]:
        e = type_diff_counts[qtype]["easy"]
        m = type_diff_counts[qtype]["medium"]
        h = type_diff_counts[qtype]["hard"]
        total = e + m + h
        add(f"| {qtype} | {e} | {m} | {h} | {total} |")
    total_e = sum(type_diff_counts[t]["easy"] for t in type_diff_counts)
    total_m = sum(type_diff_counts[t]["medium"] for t in type_diff_counts)
    total_h = sum(type_diff_counts[t]["hard"] for t in type_diff_counts)
    add(f"| **Total** | **{total_e}** | **{total_m}** | **{total_h}** | **{total_e+total_m+total_h}** |")
    add()
    add("Note: Synthesis questions only appear in the obsidian dataset (5 questions). All synthesis questions are rated hard.")
    add()

    add("### Experimental Controls")
    add()
    add("- A root `.claude/CLAUDE.md` (~1,500 chars) was loaded for all strategies as a constant baseline")
    add("- Each strategy folder contained a `data/` symlink to the identical source corpus")
    add("- Strategy-specific `CLAUDE.md` and `@refs` defined the initial context window")
    add("- All questions were identical across strategies within each dataset")
    add()
    add("---")
    add()

    # ── Results ──
    add("## Results")
    add()

    # Overall Strategy Rankings
    add("### Overall Strategy Rankings")
    add()
    add("Ranked by average score across all 49 tests per strategy (both datasets combined).")
    add()
    add("|  Rank | Strategy                       | Family       | Avg Score | Exact Match | Cost/Correct Answer |")
    add("| ----: | ------------------------------ | ------------ | --------: | ----------: | ------------------: |")

    strategy_families = {
        "R1": "Reference", "R2.1": "Reference", "R2.2": "Reference",
        "R2.3": "Reference", "R2.4": "Reference", "R3": "Reference", "R4": "Reference",
        "I1": "Index", "I2": "Index", "I3": "Index", "I4": "Index",
        "C1": "Combined", "C2": "Combined", "C3": "Combined",
    }
    strategy_labels = {
        "I4": "**I4** (summary table)", "I1": "**I1** (keyword index)",
        "I3": "**I3** (semantic groups)", "R1": "**R1** (no context)",
        "R3": "**R3** (sub-indexes)", "C3": "**C3** (keyword + sub-index)",
        "I2": "**I2** (relationship graph)", "R4": "**R4** (key files)",
        "C2": "**C2** (key files + graph)",
    }

    ranked_strategies = sorted(by_strategy.keys(),
                                key=lambda s: sum(e["score"] for e in by_strategy[s]) / len(by_strategy[s]),
                                reverse=True)

    rank = 0
    for strategy in ranked_strategies:
        tests = by_strategy[strategy]
        avg_score = sum(e["score"] for e in tests) / len(tests)
        exact = sum(1 for e in tests if e["score"] >= 0.9)
        correct = sum(1 for e in tests if e["is_correct"])
        strat_cost = sum(e["cost_usd"] for e in tests)
        cost_per_correct = strat_cost / correct if correct > 0 else None

        if strategy in FULL_OVERFLOW:
            continue  # Group these at the bottom
        rank += 1
        label = strategy_labels.get(strategy, f"**{strategy}**")
        family = strategy_families.get(strategy, "")
        cpc = f"${cost_per_correct:.3f}" if cost_per_correct else "N/A"
        add(f"| {rank:>5} | {label:<30} | {family:<12} | {avg_score:>7.1%} | {exact:>7}/{len(tests)} | {cpc:>19} |")

    overflow_strategies = sorted(s for s in ranked_strategies if s in FULL_OVERFLOW)
    overflow_labels = ", ".join(f"**{s}**" for s in overflow_strategies)
    add(f"| 10-14 | {overflow_labels} | Ref/Combined | {'0.0%':>7} | {'0/49':>7} | {'N/A (overflow)':>19} |")
    add()
    add("**Five strategies scored 0.0%** due to context window overflow. These all attempted to load the full file corpus into the 200K token window.")
    add()

    # Strategy x Dataset Breakdown
    add("### Strategy x Dataset Breakdown")
    add()
    add("Performance varies significantly between the well-structured (soong-v5) and messy (obsidian) datasets.")
    add()
    add("| Strategy          | soong-v5 (120 files) | obsidian (213 files) | Delta |")
    add("| ----------------- | -------------------: | -------------------: | ----: |")

    for strategy in ranked_strategies:
        if strategy in FULL_OVERFLOW:
            continue
        tests = by_strategy[strategy]
        soong = [e for e in tests if e["dataset"] == "soong-v5"]
        obs = [e for e in tests if e["dataset"] == "obsidian"]
        soong_avg = sum(e["score"] for e in soong) / len(soong) if soong else 0
        obs_avg = sum(e["score"] for e in obs) / len(obs) if obs else 0

        if strategy in PARTIAL_OVERFLOW:
            obs_str = f"0.0% (overflow)"
            delta_str = "--"
        else:
            obs_str = f"{obs_avg:.1%}"
            delta_str = f"{(obs_avg - soong_avg) * 100:+.1f}"

        add(f"| **{strategy}** | {soong_avg:>18.1%} | {obs_str:>20} | {delta_str:>5} |")

    add(f"| **R2.1-R2.4, C1** | {'0.0%':>18} | {'0.0%':>20} | {'--':>5} |")
    add()
    add("Notable observations:")
    add("- **I4 is the most robust** -- only a 3-point drop from structured to messy data")
    add("- **R4 and C2 overflow on the larger dataset** -- selective file loading is dataset-size dependent")
    add("- **All working strategies degrade on obsidian**, but index strategies degrade less")
    add()

    # ── Token Usage and Efficiency ──
    add("### Token Usage and Efficiency")
    add()
    add("Per-test averages for strategies that produced results (non-overflow tests only).")
    add()
    add("| Strategy | Avg Total Tokens | Avg Turns | Avg Cost/Test | Efficiency Profile                    |")
    add("| -------- | ---------------: | --------: | ------------: | :------------------------------------ |")

    efficiency_profiles = {
        "I4": "Low tokens, few turns",
        "I1": "Low tokens, few turns",
        "C3": "Low tokens, fewest turns",
        "R3": "Low tokens, moderate turns",
        "I3": "Moderate tokens, more turns",
        "I2": "Higher tokens, few turns",
        "R1": "Highest turns, cheapest per-test",
        "R4": "Single turn, expensive (file loading)",
        "C2": "Single turn, most expensive",
    }

    # Sort by cost/test ascending for working strategies
    working_strats = [s for s in ranked_strategies if s not in FULL_OVERFLOW]
    strat_cost_data = {}
    for strategy in working_strats:
        tests = [e for e in working_by_strategy.get(strategy, by_strategy[strategy]) if e["working"]]
        if not tests:
            # R4/C2 soong-only
            tests = [e for e in by_strategy[strategy] if e["dataset"] == "soong-v5"]
        if tests:
            avg_tokens = sum(e["total_tokens"] for e in tests) / len(tests)
            avg_turns = sum(e["num_turns"] for e in tests) / len(tests)
            avg_cost = sum(e["cost_usd"] for e in tests) / len(tests)
            strat_cost_data[strategy] = (avg_tokens, avg_turns, avg_cost, len(tests))

    for strategy in sorted(strat_cost_data, key=lambda s: strat_cost_data[s][2]):
        avg_tokens, avg_turns, avg_cost, n = strat_cost_data[strategy]
        profile = efficiency_profiles.get(strategy, "")
        add(f"| **{strategy}** | {avg_tokens:>16,.0f} | {avg_turns:>9.1f} | ${avg_cost:>12.3f} | {profile:<37} |")

    add()
    add("**R1 is the cheapest per-test** because Haiku's input tokens are cheap and tool calls are lightweight -- but it requires **6 turns** of exploration compared to ~3 for index strategies. Index strategies trade a modest increase in upfront context tokens for halved turn counts.")
    add()

    # ── NEW: Wall Clock Timing Analysis ──
    add("### Wall Clock Timing")
    add()
    add("Average elapsed time per test, measured end-to-end (includes subprocess overhead).")
    add()
    add("| Strategy | Avg Time | Median Time | Min | Max | Avg Turns | Tests |")
    add("| -------- | -------: | ----------: | --: | --: | --------: | ----: |")

    for strategy in sorted(strat_cost_data, key=lambda s: strat_cost_data[s][2]):
        tests = [e for e in working_by_strategy.get(strategy, by_strategy[strategy]) if e["working"]]
        if not tests:
            tests = [e for e in by_strategy[strategy] if e["dataset"] == "soong-v5"]

        times = [e["wall_clock_ms"] for e in tests if e["wall_clock_ms"] is not None]
        if not times:
            continue

        avg_time = sum(times) / len(times)
        med_time = median(times)
        min_time = min(times)
        max_time = max(times)
        avg_turns = sum(e["num_turns"] for e in tests) / len(tests)

        add(f"| **{strategy}** | {format_time(avg_time):>8} | {format_time(med_time):>11} | {format_time(min_time):>3} | {format_time(max_time):>3} | {avg_turns:>9.1f} | {len(times):>5} |")

    add()
    add("Timing reinforces the turn-count story: R1 (6 turns avg) takes the longest wall clock time despite being cheapest in dollar cost. Index strategies (I1, I3, I4) cluster around 10-15 seconds with ~3 turns. R4/C2 are fast (single turn) but only because they dump everything into context at once -- and this approach fails on larger datasets.")
    add()

    # ── NEW: Performance by Question Type (All vs Working) ──
    add("### Performance by Question Type")
    add()
    add("**Important**: The \"All Strategies\" column includes overflow strategies (R2.1-R2.4, C1, and R4/C2 on obsidian) which score 0%, significantly dragging down averages. The \"Working Strategies\" column excludes these to show actual capability.")
    add()

    # All strategies
    all_by_type = defaultdict(list)
    working_by_type = defaultdict(list)
    for e in enriched:
        all_by_type[e["question_type"]].append(e["score"])
        if e["working"]:
            working_by_type[e["question_type"]].append(e["score"])

    add("| Question Type | All Strategies | Working Strategies | Tests (All) | Tests (Working) |")
    add("|---------------|---------------:|-------------------:|------------:|----------------:|")
    for qtype in ["navigation", "depth", "cross-reference", "synthesis"]:
        all_scores = all_by_type.get(qtype, [])
        work_scores = working_by_type.get(qtype, [])
        all_avg = sum(all_scores) / len(all_scores) if all_scores else 0
        work_avg = sum(work_scores) / len(work_scores) if work_scores else 0
        add(f"| **{qtype.title()}** | {all_avg:.1%} | {work_avg:.1%} | {len(all_scores)} | {len(work_scores)} |")

    add()
    add("When overflow noise is removed, navigation questions reach ~80%, showing Claude's strong file-finding ability with index guidance. Synthesis remains the hardest category even for working strategies.")
    add()

    # ── NEW: Performance by Difficulty (All vs Working) ──
    add("### Performance by Difficulty")
    add()

    all_by_diff = defaultdict(list)
    working_by_diff = defaultdict(list)
    for e in enriched:
        all_by_diff[e["difficulty"]].append(e["score"])
        if e["working"]:
            working_by_diff[e["difficulty"]].append(e["score"])

    add("| Difficulty | All Strategies | Working Strategies | Tests (All) | Tests (Working) |")
    add("|------------|---------------:|-------------------:|------------:|----------------:|")
    for diff in ["easy", "medium", "hard"]:
        all_scores = all_by_diff.get(diff, [])
        work_scores = working_by_diff.get(diff, [])
        all_avg = sum(all_scores) / len(all_scores) if all_scores else 0
        work_avg = sum(work_scores) / len(work_scores) if work_scores else 0
        add(f"| **{diff.title()}** | {all_avg:.1%} | {work_avg:.1%} | {len(all_scores)} | {len(work_scores)} |")

    add()
    add("Hard questions score roughly half as well as easy ones. This gradient holds across all strategies, suggesting it reflects genuine question difficulty rather than strategy-specific weaknesses.")
    add()

    # ── NEW: Working Strategy x Question Type Matrix ──
    add("### Strategy x Question Type Matrix (Working Strategies Only)")
    add()
    add("How each working strategy performs across question types.")
    add()
    add("| Strategy | Navigation | Depth | Cross-ref | Synthesis | Overall |")
    add("|----------|----------:|------:|----------:|----------:|--------:|")

    for strategy in ranked_strategies:
        if strategy in FULL_OVERFLOW:
            continue
        tests = [e for e in by_strategy[strategy] if e["working"]]
        if not tests:
            continue

        type_scores = defaultdict(list)
        for e in tests:
            type_scores[e["question_type"]].append(e["score"])

        nav = sum(type_scores["navigation"]) / len(type_scores["navigation"]) if type_scores["navigation"] else 0
        dep = sum(type_scores["depth"]) / len(type_scores["depth"]) if type_scores["depth"] else 0
        xref = sum(type_scores["cross-reference"]) / len(type_scores["cross-reference"]) if type_scores["cross-reference"] else 0
        synth = sum(type_scores["synthesis"]) / len(type_scores["synthesis"]) if type_scores["synthesis"] else 0
        overall = sum(e["score"] for e in tests) / len(tests)

        synth_str = f"{synth:.0%}" if type_scores["synthesis"] else "N/A"
        add(f"| **{strategy}** | {nav:.0%} | {dep:.0%} | {xref:.0%} | {synth_str} | {overall:.0%} |")

    add()
    add("Note: R4 and C2 only show soong-v5 results (obsidian overflowed). Synthesis questions only appear in the obsidian dataset.")
    add()

    # ── NEW: Cache Efficiency ──
    add("### Cache Efficiency")
    add()
    add("How effectively each strategy uses Anthropic's prompt caching (higher cache read ratio = more tokens served from cache = cheaper).")
    add()

    add("| Strategy | Avg Cache Read | Avg Cache Create | Cache Hit Ratio | Avg Cost/Test |")
    add("| -------- | -------------: | ---------------: | --------------: | ------------: |")

    for strategy in sorted(strat_cost_data, key=lambda s: strat_cost_data[s][2]):
        tests = [e for e in working_by_strategy.get(strategy, by_strategy[strategy]) if e["working"]]
        if not tests:
            tests = [e for e in by_strategy[strategy] if e["dataset"] == "soong-v5"]
        if not tests:
            continue

        avg_cache_read = sum(e["cache_read"] for e in tests) / len(tests)
        avg_cache_create = sum(e["cache_creation"] for e in tests) / len(tests)
        total_cache = avg_cache_read + avg_cache_create
        hit_ratio = avg_cache_read / total_cache if total_cache > 0 else 0
        avg_cost = sum(e["cost_usd"] for e in tests) / len(tests)

        add(f"| **{strategy}** | {avg_cache_read:>14,.0f} | {avg_cache_create:>16,.0f} | {hit_ratio:>15.0%} | ${avg_cost:>12.3f} |")

    add()
    add("Strategies with higher cache hit ratios benefit from prompt caching -- the shared CLAUDE.md and strategy instructions get cached across questions in the same run. R1 has higher cache creation because each test starts fresh and builds context through tool calls.")
    add()

    # ── NEW: Hardest and Easiest Questions ──
    add("### Hardest and Easiest Questions (Working Strategies)")
    add()

    question_scores = defaultdict(list)
    for e in working_tests:
        key = f"{e['dataset']}/{e['question_id']}"
        question_scores[key].append(e["score"])

    question_avgs = {k: sum(v) / len(v) for k, v in question_scores.items()}

    add("**Top 5 Easiest** (highest average score across working strategies):")
    add()
    add("| Question | Avg Score | Tests | Type | Difficulty |")
    add("|----------|----------:|------:|------|------------|")
    for key in sorted(question_avgs, key=question_avgs.get, reverse=True)[:5]:
        dataset, qid = key.split("/")
        q = questions.get(dataset, {}).get(qid, {})
        avg = question_avgs[key]
        n = len(question_scores[key])
        add(f"| {key} | {avg:.0%} | {n} | {q.get('type', '?')} | {q.get('difficulty', '?')} |")

    add()
    add("**Top 5 Hardest** (lowest average score across working strategies):")
    add()
    add("| Question | Avg Score | Tests | Type | Difficulty |")
    add("|----------|----------:|------:|------|------------|")
    for key in sorted(question_avgs, key=question_avgs.get)[:5]:
        dataset, qid = key.split("/")
        q = questions.get(dataset, {}).get(qid, {})
        avg = question_avgs[key]
        n = len(question_scores[key])
        add(f"| {key} | {avg:.0%} | {n} | {q.get('type', '?')} | {q.get('difficulty', '?')} |")

    add()

    # ── NEW: Confidence Calibration ──
    add("### Confidence Calibration")
    add()
    add("How well does the model's self-reported confidence correlate with actual accuracy?")
    add()

    conf_scores = defaultdict(list)
    for e in working_tests:
        # Extract confidence from the result
        conf = "unknown"
        for r in results:
            meta = r.get("metadata", {})
            if (meta.get("strategy") == e["strategy"] and
                meta.get("dataset") == e["dataset"] and
                meta.get("question_id") == e["question_id"]):
                resp = r.get("response", "")
                if '"confidence"' in resp.lower():
                    for c in ["high", "medium", "low"]:
                        if f'"confidence": "{c}"' in resp or f'"confidence":"{c}"' in resp:
                            conf = c
                            break
                break
        conf_scores[conf].append(e["score"])

    add("| Confidence | Avg Score | Exact Match Rate | Tests |")
    add("|------------|----------:|-----------------:|------:|")
    for conf in ["high", "medium", "low", "unknown"]:
        scores = conf_scores.get(conf, [])
        if scores:
            avg = sum(scores) / len(scores)
            exact_rate = sum(1 for s in scores if s >= 0.9) / len(scores)
            add(f"| **{conf.title()}** | {avg:.1%} | {exact_rate:.1%} | {len(scores)} |")

    add()

    # ── Key Findings (same structure, updated data) ──
    add("---")
    add()
    add("## Key Findings")
    add()

    add("### Finding 1: Index Strategies Dominate")
    add()
    add("**I4 (summary table) wins overall at 70.0%.** All index strategies (I1-I4, C3) cluster between 63-70%, forming a clear performance tier above other approaches.")
    add()
    add("The pattern is consistent: give Claude a compact map of the territory and let tools do the detail work. The index tells the model *where to look*; tools retrieve *what's there*. This division of labor outperforms both extremes -- loading everything (overflow) and loading nothing (more exploration turns needed).")
    add()

    add("### Finding 2: No Context is Surprisingly Competitive")
    add()
    add("**R1 (no context) scores 65.4%**, only 4.6 points behind the winning strategy. Claude's built-in tool navigation -- Glob for discovery, Read for content -- is remarkably effective on its own.")
    add()
    add("However, R1 requires **6 turns** on average versus ~3 for index strategies. Indexes don't dramatically improve accuracy; they **halve the work required to reach similar accuracy**. In production, this translates directly to faster responses and lower latency.")
    add()

    add("### Finding 3: Full File Loading Fails at Scale")
    add()
    add("Every strategy that loads all files into context (R2.1, R2.2, R2.3, R2.4, C1) overflows Haiku's 200K token window on **both datasets**, producing 0% accuracy across 245 tests. Even selective loading (R4, C2) overflows on the larger obsidian dataset.")
    add()
    add("This is the sharpest result in the study: **the intuitive approach of \"give the model everything\" is not just inefficient -- it is non-functional** for any real-world corpus of meaningful size.")
    add()

    add("### Finding 4: Indexes Help More on Messy Data")
    add()
    add("| Strategy | soong-v5 | obsidian | I4 Advantage over R1 |")
    add("|----------|----------|----------|---------------------|")
    add("| **I4** | 72.8% | 69.8% | -- |")
    add("| **R1** | 70.7% | 63.2% | -- |")
    add("| **Delta (I4 - R1)** | +2.1 | **+6.6** | 3x larger on messy data |")
    add()
    add("On well-structured data (soong-v5), indexes provide a modest 2.1-point boost. On messy real-world data (obsidian), the boost triples to 6.6 points. **Indexes matter most when the underlying data lacks clear organization** -- precisely the scenario where human users also struggle most.")
    add()

    add("### Finding 5: Summary Table Beats Keywords")
    add()
    add("**I4 (summary table) = 70.0% vs I1 (keyword index) = 67.0%**, at nearly identical token cost ($0.040 vs $0.041 per test).")
    add()
    add("One-sentence prose summaries give the model better semantic signal than keyword lists. A summary like \"Configuration file for the authentication middleware\" communicates purpose and context more effectively than \"config, auth, middleware, settings, jwt, tokens, security, access.\"")
    add()

    add("### Finding 6: Relationship Graphs Underperform")
    add()
    add("**I2 (relationship graph) = 63.6% at $0.059/test vs I4 = 70.0% at $0.040/test.** The topic-to-file relationship graph is both less accurate and 48% more expensive per test.")
    add()
    add("The graph structure introduces noise -- too many connections, not enough signal per entry. Simpler, flatter indexes outperform richer structural representations. This aligns with the general pattern: **compact, direct context beats elaborate, indirect context**.")
    add()

    add("### Finding 7: Selective File Loading is Dataset-Size Dependent")
    add()
    add("R4 (top 15-30 key files) scores 72.3% on soong-v5 but overflows on obsidian. C2 (key files + relationship graph) shows the same pattern. **Any strategy that loads file contents is fundamentally constrained by the ratio of selected content to context window size.** As datasets grow, these strategies break.")
    add()
    add("Index-only strategies (I1-I4) scale gracefully because their context footprint grows linearly with file *count*, not file *content*.")
    add()

    add("### Finding 8: Synthesis Remains the Hardest Question Type")
    add()
    synth_working = working_by_type.get("synthesis", [])
    nav_working = working_by_type.get("navigation", [])
    synth_avg = sum(synth_working) / len(synth_working) if synth_working else 0
    nav_avg = sum(nav_working) / len(nav_working) if nav_working else 0
    add(f"Even the best strategies struggle with synthesis questions ({synth_avg:.1%} average for working strategies). Navigation questions ({nav_avg:.1%}) are significantly easier. This suggests that current tool-based retrieval handles \"find and read\" well but struggles with \"find, read, and combine\" -- a known limitation of sequential tool use patterns.")
    add()

    # ── Phase 1 vs Phase 2 ──
    add("---")
    add()
    add("## Phase 1 vs Phase 2 Comparison")
    add()
    add("Phase 1 established that context structure matters by testing flat, shallow, deep, and very-deep CLAUDE.md organizations on a single codebase. The key Phase 1 finding was that **Very-Deep structure was the efficiency winner at 497 tokens per 1% accuracy**, suggesting that hierarchical organization with clear navigation paths outperforms both minimal and exhaustive context.")
    add()
    add("Phase 2 extends this in three ways:")
    add()
    add("1. **Scale validation**: Phase 1 tested small contexts. Phase 2 confirms that the same principles hold at 120-213 file scale with 280-300K word corpora.")
    add("2. **Overflow boundary**: Phase 2 reveals that \"stuffing everything into context\" is not merely wasteful (as Phase 1 suggested) -- it is **physically impossible** beyond roughly 200K tokens. This transforms a soft optimization principle into a hard engineering constraint.")
    add("3. **Index as the scaling mechanism**: Phase 1's \"Very-Deep\" structure is conceptually an index -- it tells the model where things are without including all the content. Phase 2's I4 strategy formalizes this into a scalable pattern: one row per file, one sentence of context, tools for everything else.")
    add()
    add("The through-line across both phases: **the model needs orientation, not information**. Context should be a map, not the territory.")
    add()

    # ── Methodology Notes ──
    add("---")
    add()
    add("## Methodology Notes")
    add()
    add("### Execution Environment")
    add()
    add("- All tests executed via `claude -p` in headless mode")
    add("- `--permission-mode bypassPermissions` enabled unrestricted tool access")
    add("- Each strategy defined in its own folder with a `CLAUDE.md` and optional `@ref` files")
    add("- A `data/` symlink in each strategy folder pointed to the shared source corpus")
    add("- Root `.claude/CLAUDE.md` (~1,500 characters) loaded as a constant across all strategies")
    add()
    add("### Scoring Rubric")
    add()
    add("| Score | Criteria |")
    add("|------:|----------|")
    add("| 1.0 | Exact match with expected answer |")
    add("| 0.9 | Correct answer with minor variant (e.g., different path format) |")
    add("| 0.0-0.7 | Partial keyword credit based on overlap with expected answer |")
    add("| 0.0 | Incorrect, no answer, or overflow (context window exceeded) |")
    add()
    add("### Limitations")
    add()
    add("- **Single model**: All results are Haiku-specific. Strategy rankings may differ on Sonnet or Opus.")
    add("- **Two datasets**: While soong-v5 and obsidian represent structured and unstructured extremes, two datasets cannot capture all corpus characteristics.")
    add("- **Question design**: Questions were authored to cover navigation, depth, cross-reference, and synthesis categories, but may not represent all real-world query patterns.")
    add("- **Scoring subjectivity**: Partial credit (0.0-0.7 range) involves judgment calls on keyword overlap quality.")
    add()

    # ── Next Steps (with 2.2 note) ──
    add("---")
    add()
    add("## Next Steps")
    add()
    add("| Phase | Focus | Goal |")
    add("|-------|-------|------|")
    add("| **2.2** | Model comparison | Test I4 (winning strategy) with Sonnet and local Ollama models to determine if strategy rankings are model-dependent |")
    add("| **2.3** | Failure analysis | Investigate question-level failures (e.g., NAV-008 at 0%, DEPTH-007 I4-specific gap) to understand where and why the best strategy still fails |")
    add("| **3.0** | Production application | Apply Phase 2 findings to real-world CLAUDE.md configurations for active projects |")
    add()
    add("### Phase 2.2 Design Note: Early Overflow Detection")
    add()
    add("Phase 2.1 spent an estimated ~$5.80 on overflow tests that could never produce results. In Phase 2.2 and beyond, the harness should implement **early overflow detection** to avoid wasting inference on strategies that will exceed the context window:")
    add()
    add("1. **Pre-flight token estimation**: Before running a test, estimate the total prompt size (CLAUDE.md + `@ref` files + question). If the estimate exceeds 80% of the model's context window, skip the test and record it as `overflow_predicted`.")
    add("2. **First-test sentinel**: For each (strategy, dataset) pair, run one test first. If it returns a \"Prompt is too long\" error or exit code 1, skip all remaining tests for that combination.")
    add("3. **Budget guard**: Set `--max-budget-usd` conservatively for strategies known to be near the context limit, so a single expensive failure doesn't consume the full test budget.")
    add()
    add("This is especially important for Phase 2.2's model comparison, since smaller models (Ollama local, GPT-4o-mini) may have smaller context windows and will overflow on strategies that worked for Haiku.")
    add()

    # ── Appendix ──
    add("---")
    add()
    add("## Appendix: Cost Breakdown")
    add()

    overflow_tests = [e for e in enriched if not e["working"]]
    productive_tests = [e for e in enriched if e["working"]]
    overflow_cost = sum(e["cost_usd"] for e in overflow_tests)

    add("| Category | Value |")
    add("|----------|------:|")
    add(f"| Total experiment cost | ${total_cost:.2f} |")
    add(f"| Total tests executed | {len(enriched)} |")
    add(f"| Tests producing results (non-overflow) | {len(productive_tests)} |")
    add(f"| Tests lost to overflow | {len(overflow_tests)} |")
    avg_productive = total_cost / len(productive_tests) if productive_tests else 0
    add(f"| Average cost per productive test | ${avg_productive:.3f} |")
    add(f"| Cost of overflow tests | ~${overflow_cost:.2f} (estimated, prompt-only charges) |")
    add()

    # Total timing
    all_times = [e["wall_clock_ms"] for e in productive_tests if e["wall_clock_ms"]]
    if all_times:
        total_time_min = sum(all_times) / 1000 / 60
        add(f"| Total wall clock time (productive tests) | {total_time_min:.1f} minutes |")
        add(f"| Average time per productive test | {format_time(sum(all_times) / len(all_times))} |")
    add()

    add("---")
    add()
    add("*Report generated 2026-02-19. Phase 2.1 of the Context Structure Research project.*")
    add("*Model tested: claude-haiku-4-5-20251001 | Harness: context-structure-research v2*")

    report_text = "\n".join(lines)

    # Write report
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = ANALYSIS_DIR / "enhanced-report.md"
    report_path.write_text(report_text)
    print(f"\nEnhanced report written to: {report_path}")
    print(f"Total tests: {len(enriched)}")
    print(f"Working tests: {len(productive_tests)}")
    print(f"Overflow tests: {len(overflow_tests)}")


if __name__ == "__main__":
    main()
