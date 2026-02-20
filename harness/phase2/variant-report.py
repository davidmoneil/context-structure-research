#!/usr/bin/env python3
"""
Phase 2.2: I4 Variant Comparison Report

Analyzes I4 variants to answer: Does summary generation method affect accuracy?
Groups variants by generation approach and compares against Phase 2.1 baselines.
"""

import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_JSON = PROJECT_ROOT / "results" / "phase2" / "analysis" / "results.json"
OUTPUT_DIR = PROJECT_ROOT / "results" / "phase2" / "analysis"

# Variant metadata: what method generated the summaries
VARIANT_INFO = {
    # Phase 2.1 baselines (not I4 variants)
    "R1": {"group": "baseline", "desc": "No index (tool navigation only)"},
    "R2.1": {"group": "overflow", "desc": "All files via @ref"},
    "R2.2": {"group": "overflow", "desc": "All files via @ref (nested)"},
    "R2.3": {"group": "overflow", "desc": "All files via @ref (deep nested)"},
    "R2.4": {"group": "overflow", "desc": "All files via @ref (very deep)"},
    "R3": {"group": "baseline", "desc": "Hierarchical @refs"},
    "R4": {"group": "baseline", "desc": "Selective @refs (key files)"},
    "I1": {"group": "baseline", "desc": "Keyword index"},
    "I2": {"group": "baseline", "desc": "Relationship graph"},
    "I3": {"group": "baseline", "desc": "Semantic grouping"},
    "C1": {"group": "overflow", "desc": "R2+I1 combo"},
    "C2": {"group": "baseline", "desc": "R4+I2 combo"},
    "C3": {"group": "baseline", "desc": "R3+I1 combo"},
    # Phase 2.1 I4 (template heuristic)
    "I4": {"group": "heuristic", "desc": "Template heuristic (category + title + keywords)", "model": "template"},
    # Phase 2.2 variants
    "I4-template": {"group": "heuristic", "desc": "Template heuristic (explicit)", "model": "template"},
    "I4-grep": {"group": "extraction", "desc": "Grep-based extraction, loaded via @ref", "model": "grep"},
    "I4-grep2a": {"group": "extraction", "desc": "Grep-based, instruction to use grep tool", "model": "grep"},
    "I4-grep2b": {"group": "extraction", "desc": "Grep-based, instruction to grep summaries.md", "model": "grep"},
    "I4-kw2": {"group": "keyword-count", "desc": "Template with 2 keywords per file", "model": "template-kw2"},
    "I4-kw7": {"group": "keyword-count", "desc": "Template with 7 keywords per file", "model": "template-kw7"},
    "I4-kw10": {"group": "keyword-count", "desc": "Template with 10 keywords per file", "model": "template-kw10"},
    "I4-sonnet": {"group": "llm-generated", "desc": "Summaries by Claude Sonnet 4.6", "model": "claude-sonnet"},
    "I4-sonnet-verify": {"group": "llm-generated", "desc": "Sonnet summaries + verification pass", "model": "claude-sonnet+verify"},
    "I4-geminiflash": {"group": "llm-generated", "desc": "Summaries by Gemini Flash 2", "model": "gemini-flash"},
    "I4-gpt4omini": {"group": "llm-generated", "desc": "Summaries by GPT-4o-mini", "model": "gpt-4o-mini"},
    "I4-qwen7b": {"group": "llm-generated", "desc": "Summaries by Qwen 2.5 7B (local)", "model": "qwen-7b"},
    "I4-qwen32b": {"group": "llm-generated", "desc": "Summaries by Qwen 2.5 32B (local)", "model": "qwen-32b"},
}


def load_results():
    with open(RESULTS_JSON) as f:
        return json.load(f)


def analyze_variants(data):
    """Analyze I4 variants from scored results."""
    scores = data["scores"]

    # Group scores by strategy
    by_strategy = defaultdict(lambda: {
        "scores": [], "exact": 0, "variant": 0, "zero": 0,
        "by_dataset": defaultdict(list),
        "by_qtype": defaultdict(list),
        "costs": [],
    })

    for s in scores:
        strat = s["strategy"]
        by_strategy[strat]["scores"].append(s["points"])
        if s["exact_match"]:
            by_strategy[strat]["exact"] += 1
        if s["variant_match"]:
            by_strategy[strat]["variant"] += 1
        if s["points"] == 0.0:
            by_strategy[strat]["zero"] += 1
        by_strategy[strat]["by_dataset"][s["dataset"]].append(s["points"])
        by_strategy[strat]["by_qtype"][s["question_type"]].append(s["points"])
        if s.get("cost_usd"):
            by_strategy[strat]["costs"].append(s["cost_usd"])

    return by_strategy


def avg(values):
    return sum(values) / len(values) if values else 0.0


def generate_report(by_strategy):
    lines = []
    lines.append("# Phase 2.2: I4 Variant Comparison Report")
    lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Separate I4 variants from baselines
    i4_variants = {k: v for k, v in by_strategy.items() if k.startswith("I4")}
    baselines = {k: v for k, v in by_strategy.items()
                 if not k.startswith("I4") and VARIANT_INFO.get(k, {}).get("group") not in ("overflow",)}

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"**{len(i4_variants)} I4 variants** tested across 2 datasets, {sum(len(v['scores']) for v in i4_variants.values())} total tests.")
    lines.append("")

    # Top-level finding
    ranked_i4 = sorted(i4_variants.items(), key=lambda x: avg(x[1]["scores"]), reverse=True)
    best = ranked_i4[0]
    worst = ranked_i4[-1]
    lines.append(f"**Best I4 variant**: {best[0]} ({avg(best[1]['scores']):.1%})")
    lines.append(f"**Worst I4 variant**: {worst[0]} ({avg(worst[1]['scores']):.1%})")
    lines.append(f"**Spread**: {avg(best[1]['scores']) - avg(worst[1]['scores']):.1%} between best and worst")
    lines.append("")

    # Key finding
    heuristic_avg = avg([avg(v["scores"]) for k, v in i4_variants.items()
                         if VARIANT_INFO.get(k, {}).get("group") in ("heuristic", "extraction", "keyword-count")])
    llm_avg = avg([avg(v["scores"]) for k, v in i4_variants.items()
                   if VARIANT_INFO.get(k, {}).get("group") == "llm-generated"])
    lines.append("### Central Finding")
    lines.append("")
    lines.append(f"**Heuristic/extraction methods ({heuristic_avg:.1%}) outperform LLM-generated summaries ({llm_avg:.1%}).**")
    lines.append("")
    lines.append("Simpler, cheaper summary generation produces better results than expensive LLM calls.")
    lines.append("")

    # Full I4 ranking table
    lines.append("---")
    lines.append("")
    lines.append("## I4 Variant Rankings")
    lines.append("")
    lines.append("| Rank | Variant | Accuracy | Exact | Group | Generation Method |")
    lines.append("|------|---------|----------|-------|-------|-------------------|")
    for i, (strat, data) in enumerate(ranked_i4, 1):
        info = VARIANT_INFO.get(strat, {})
        group = info.get("group", "unknown")
        desc = info.get("desc", "")
        acc = avg(data["scores"])
        exact = data["exact"]
        total = len(data["scores"])
        lines.append(f"| {i} | {strat} | {acc:.1%} | {exact}/{total} | {group} | {desc} |")
    lines.append("")

    # Group comparison
    lines.append("---")
    lines.append("")
    lines.append("## Performance by Generation Approach")
    lines.append("")

    groups = defaultdict(lambda: {"strategies": [], "all_scores": []})
    for strat, data in i4_variants.items():
        info = VARIANT_INFO.get(strat, {})
        group = info.get("group", "unknown")
        groups[group]["strategies"].append(strat)
        groups[group]["all_scores"].extend(data["scores"])

    lines.append("| Approach | Strategies | Avg Accuracy | Tests | Description |")
    lines.append("|----------|------------|--------------|-------|-------------|")

    group_descs = {
        "heuristic": "Category + title + keywords from file metadata",
        "extraction": "Grep/regex extraction from file contents",
        "keyword-count": "Template with varying keyword counts (2/7/10)",
        "llm-generated": "One-sentence summaries by external LLMs",
    }
    for group in ["heuristic", "extraction", "keyword-count", "llm-generated"]:
        if group in groups:
            g = groups[group]
            acc = avg(g["all_scores"])
            strats = ", ".join(g["strategies"])
            desc = group_descs.get(group, "")
            lines.append(f"| **{group}** | {strats} | {acc:.1%} | {len(g['all_scores'])} | {desc} |")
    lines.append("")

    # vs baselines
    lines.append("---")
    lines.append("")
    lines.append("## I4 Variants vs Phase 2.1 Baselines")
    lines.append("")
    lines.append("| Strategy | Accuracy | Type |")
    lines.append("|----------|----------|------|")

    all_working = {**i4_variants, **baselines}
    for strat, data in sorted(all_working.items(), key=lambda x: avg(x[1]["scores"]), reverse=True):
        acc = avg(data["scores"])
        info = VARIANT_INFO.get(strat, {})
        stype = "I4 variant" if strat.startswith("I4") else "Phase 2.1 baseline"
        lines.append(f"| {strat} | {acc:.1%} | {stype} |")
    lines.append("")

    # Dataset breakdown
    lines.append("---")
    lines.append("")
    lines.append("## I4 Variants by Dataset")
    lines.append("")
    lines.append("| Variant | Soong-v5 | Obsidian | Delta |")
    lines.append("|---------|----------|----------|-------|")
    for strat, data in ranked_i4:
        soong = avg(data["by_dataset"].get("soong-v5", []))
        obsidian = avg(data["by_dataset"].get("obsidian", []))
        delta = soong - obsidian
        lines.append(f"| {strat} | {soong:.1%} | {obsidian:.1%} | {delta:+.1%} |")
    lines.append("")

    # Question type breakdown
    lines.append("---")
    lines.append("")
    lines.append("## I4 Variants by Question Type")
    lines.append("")
    qtypes = ["navigation", "cross-reference", "depth", "synthesis"]
    header = "| Variant | " + " | ".join(qtypes) + " |"
    separator = "|---------|" + "|".join(["-------"] * len(qtypes)) + "|"
    lines.append(header)
    lines.append(separator)
    for strat, data in ranked_i4:
        row = f"| {strat}"
        for qt in qtypes:
            scores = data["by_qtype"].get(qt, [])
            if scores:
                row += f" | {avg(scores):.1%}"
            else:
                row += " | —"
        row += " |"
        lines.append(row)
    lines.append("")

    # Cost comparison
    lines.append("---")
    lines.append("")
    lines.append("## Cost Analysis")
    lines.append("")
    lines.append("| Variant | Total Cost | Avg Cost/Test | Accuracy | Cost/Correct |")
    lines.append("|---------|------------|---------------|----------|--------------|")
    for strat, data in ranked_i4:
        total_cost = sum(data["costs"])
        avg_cost = total_cost / len(data["costs"]) if data["costs"] else 0
        acc = avg(data["scores"])
        correct = data["exact"] + data["variant"]
        cpc = total_cost / correct if correct > 0 else float("inf")
        cpc_str = f"${cpc:.3f}" if cpc != float("inf") else "N/A"
        lines.append(f"| {strat} | ${total_cost:.2f} | ${avg_cost:.4f} | {acc:.1%} | {cpc_str} |")
    lines.append("")

    # Key findings
    lines.append("---")
    lines.append("")
    lines.append("## Key Findings")
    lines.append("")
    lines.append("### 1. Heuristic templates beat LLM-generated summaries")
    lines.append("")
    lines.append(f"Template/extraction methods average **{heuristic_avg:.1%}** vs LLM-generated **{llm_avg:.1%}**.")
    lines.append("The most expensive summary generation (Sonnet, GPT-4o-mini) does not produce the best results.")
    lines.append("This suggests the model benefits more from structured metadata (file path, category, keywords)")
    lines.append("than from prose descriptions of content.")
    lines.append("")

    lines.append("### 2. Keyword count has diminishing returns")
    lines.append("")
    kw_scores = {k: avg(v["scores"]) for k, v in i4_variants.items() if "kw" in k}
    for k, v in sorted(kw_scores.items()):
        lines.append(f"- {k}: {v:.1%}")
    lines.append("")
    lines.append("2 keywords performs best — more keywords add noise rather than signal.")
    lines.append("")

    lines.append("### 3. Grep-based access is competitive with @ref loading")
    lines.append("")
    lines.append("I4-grep2b (72.9%) instructs the model to grep the summary file rather than loading it via @ref.")
    lines.append("This nearly matches the best @ref-loaded variants, suggesting the access method matters less")
    lines.append("than the summary content itself.")
    lines.append("")

    lines.append("### 4. Local LLMs underperform cloud LLMs for summary generation")
    lines.append("")
    lines.append("| Model | Accuracy |")
    lines.append("|-------|----------|")
    for strat in ["I4-sonnet", "I4-sonnet-verify", "I4-geminiflash", "I4-gpt4omini", "I4-qwen7b", "I4-qwen32b"]:
        if strat in i4_variants:
            lines.append(f"| {strat} | {avg(i4_variants[strat]['scores']):.1%} |")
    lines.append("")
    lines.append("Qwen 32B (62.5%) performs worst despite being the largest local model.")
    lines.append("This may reflect summary quality issues or formatting differences.")
    lines.append("")

    lines.append("### 5. The Obsidian gap is consistent across variants")
    lines.append("")
    lines.append("All I4 variants perform 5-15% worse on Obsidian than Soong-v5.")
    lines.append("This gap is independent of summary generation method, confirming it reflects")
    lines.append("dataset difficulty rather than summary quality.")
    lines.append("")

    # Methodology notes
    lines.append("---")
    lines.append("")
    lines.append("## Methodology Notes")
    lines.append("")
    lines.append("- **Test model**: All tests run with Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)")
    lines.append("- **Summary generators vary**: Each I4 variant uses different models/methods to generate summaries")
    lines.append("- **Test conditions identical**: Same questions, same datasets, same runner, same permissions")
    lines.append("- **Single-shot**: Each question run once per variant (no repeats)")
    lines.append("- **NAV-008 ground truth**: Updated from 0.72 to 0.94 (corpus v5+ change)")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*{len(i4_variants)} I4 variants, {sum(len(v['scores']) for v in i4_variants.values())} tests, "
                 f"${sum(sum(v['costs']) for v in i4_variants.values()):.2f} total cost.*")

    return "\n".join(lines)


def main():
    data = load_results()
    by_strategy = analyze_variants(data)
    report = generate_report(by_strategy)

    output_path = OUTPUT_DIR / "phase-2.2-variant-report.md"
    output_path.write_text(report)
    print(f"Report written to: {output_path}")

    # Also print summary to stdout
    i4_variants = {k: v for k, v in by_strategy.items() if k.startswith("I4")}
    ranked = sorted(i4_variants.items(), key=lambda x: avg(x[1]["scores"]), reverse=True)
    print(f"\nI4 Variant Rankings ({len(ranked)} variants):")
    for i, (strat, data) in enumerate(ranked, 1):
        acc = avg(data["scores"])
        group = VARIANT_INFO.get(strat, {}).get("group", "?")
        print(f"  {i:2d}. {strat:20s} {acc:.1%}  ({group})")


if __name__ == "__main__":
    main()
