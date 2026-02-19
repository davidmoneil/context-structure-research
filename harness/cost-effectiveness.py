#!/usr/bin/env python3
"""
Cost-Effectiveness Analysis

Joins evaluator accuracy scores with raw token/cost data to answer:
"How much does it cost to get a correct answer?"

Metrics per structure/corpus/loading method:
- Cost per correct answer
- Tokens per correct answer
- Cost-effectiveness ratio (accuracy / cost)
- Token efficiency (accuracy / tokens)
"""

import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
QUESTIONS_FILE = PROJECT_ROOT / "harness" / "questions.json"

CORPUS_INFO = {
    "v4": {"words": 120_000, "files": 80},
    "v5": {"words": 302_000, "files": 121},
    "v6": {"words": 622_561, "files": 277},
}


@dataclass
class JoinedResult:
    """A test result with both accuracy and cost data."""
    suite: str
    corpus: str
    structure: str
    loading_method: str
    question_id: str
    question_type: str
    # Accuracy (from evaluator)
    score: float  # 0.0 to 1.0
    exact_match: bool
    # Cost (from raw response)
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    total_cost_usd: float
    duration_ms: int
    has_cost_data: bool


def load_evaluator_scores():
    """Load all evaluator scores keyed by (structure, loading_method, question_id)."""
    suites = [
        ("v4", RESULTS_DIR / "v4" / "analysis" / "results.json", "v4"),
        ("v5", RESULTS_DIR / "v5" / "analysis" / "results.json", "v5"),
        ("v5-enhancements", RESULTS_DIR / "v5-enhancements" / "analysis" / "results.json", "v5"),
        ("v5.5-matrix", RESULTS_DIR / "v5.5-matrix" / "analysis" / "results.json", "v5"),
        ("v6-matrix", RESULTS_DIR / "v6-matrix" / "analysis" / "results.json", "v6"),
        ("v6-extended", RESULTS_DIR / "v6-extended" / "analysis" / "results.json", "v6"),
    ]

    scores = {}
    for suite_name, results_file, corpus in suites:
        if not results_file.exists():
            continue
        with open(results_file) as f:
            data = json.load(f)
        for entry in data.get("scores", []):
            config = entry.get("config", {})
            key = (
                suite_name,
                config.get("structure", ""),
                config.get("loading_method", ""),
                entry.get("question_id", ""),
            )
            scores[key] = {
                "suite": suite_name,
                "corpus": corpus,
                "score": entry.get("points", 0),
                "exact_match": entry.get("exact_match", False),
            }
    return scores


def extract_corpus_version(file_path: Path) -> str:
    """Extract corpus version from file path."""
    path_str = str(file_path)
    for version in ["v6", "v5", "v4", "v3", "v2", "v1"]:
        if f"/{version}" in path_str:
            return version
    return "unknown"


def load_raw_cost_data():
    """Load cost/token data from raw result files."""
    suite_dirs = [
        ("v4", RESULTS_DIR / "v4" / "raw" / "haiku"),
        ("v5", RESULTS_DIR / "v5" / "raw" / "haiku"),
        ("v5-enhancements", RESULTS_DIR / "v5-enhancements" / "raw" / "haiku"),
        ("v5.5-matrix", RESULTS_DIR / "v5.5-matrix" / "raw" / "haiku"),
        ("v6-matrix", RESULTS_DIR / "v6-matrix" / "raw" / "haiku"),
        ("v6-extended", RESULTS_DIR / "v6-extended" / "raw" / "haiku" / "haiku"),
    ]

    costs = {}
    for suite_name, suite_dir in suite_dirs:
        if not suite_dir.exists():
            continue
        for filepath in suite_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)

                config = data.get("config", {})
                question_id = data.get("question_id", "")
                key = (
                    suite_name,
                    config.get("structure", ""),
                    config.get("loading_method", ""),
                    question_id,
                )

                # Parse response for usage data
                response_str = data.get("response", "")
                usage = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_read_tokens": 0,
                    "cache_creation_tokens": 0,
                    "total_cost_usd": 0.0,
                    "duration_ms": 0,
                    "question_type": data.get("question_type", "unknown"),
                }

                try:
                    response = json.loads(response_str) if isinstance(response_str, str) else response_str
                    usage_data = response.get("usage", {})
                    usage["input_tokens"] = usage_data.get("input_tokens", 0)
                    usage["output_tokens"] = usage_data.get("output_tokens", 0)
                    usage["cache_read_tokens"] = usage_data.get("cache_read_input_tokens", 0)
                    usage["cache_creation_tokens"] = usage_data.get("cache_creation_input_tokens", 0)
                    usage["total_cost_usd"] = response.get("total_cost_usd", 0.0)
                    usage["duration_ms"] = response.get("duration_ms", 0)

                    # Check modelUsage for detailed breakdown
                    for model_data in response.get("modelUsage", {}).values():
                        if "cacheReadInputTokens" in model_data:
                            usage["cache_read_tokens"] = max(
                                usage["cache_read_tokens"],
                                model_data.get("cacheReadInputTokens", 0),
                            )
                        if "cacheCreationInputTokens" in model_data:
                            usage["cache_creation_tokens"] = max(
                                usage["cache_creation_tokens"],
                                model_data.get("cacheCreationInputTokens", 0),
                            )
                except (json.JSONDecodeError, TypeError, AttributeError):
                    pass

                costs[key] = usage
            except Exception as e:
                print(f"Warning: {filepath}: {e}", file=sys.stderr)

    return costs


def join_data():
    """Join evaluator scores with cost data."""
    scores = load_evaluator_scores()
    costs = load_raw_cost_data()

    # Load questions for type info
    questions = {}
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE) as f:
            questions = {q["id"]: q for q in json.load(f)}

    results = []
    matched = 0
    unmatched_cost = 0

    for key, score_data in scores.items():
        suite, structure, method, question_id = key
        cost_data = costs.get(key)

        q_type = questions.get(question_id, {}).get("type", "unknown")

        has_cost = cost_data is not None and cost_data.get("total_cost_usd", 0) > 0

        results.append(JoinedResult(
            suite=suite,
            corpus=score_data["corpus"],
            structure=structure,
            loading_method=method,
            question_id=question_id,
            question_type=q_type,
            score=score_data["score"],
            exact_match=score_data["exact_match"],
            input_tokens=cost_data["input_tokens"] if cost_data else 0,
            output_tokens=cost_data["output_tokens"] if cost_data else 0,
            cache_read_tokens=cost_data["cache_read_tokens"] if cost_data else 0,
            cache_creation_tokens=cost_data["cache_creation_tokens"] if cost_data else 0,
            total_cost_usd=cost_data["total_cost_usd"] if cost_data else 0,
            duration_ms=cost_data["duration_ms"] if cost_data else 0,
            has_cost_data=has_cost,
        ))

        if has_cost:
            matched += 1
        else:
            unmatched_cost += 1

    print(f"Joined: {len(results)} total, {matched} with cost data, {unmatched_cost} without")
    return results


def compute_group_metrics(results: list[JoinedResult]) -> dict:
    """Compute cost-effectiveness metrics for a group of results."""
    with_cost = [r for r in results if r.has_cost_data]
    total = len(results)
    correct = sum(1 for r in results if r.score >= 1.0)
    accuracy = correct / total if total > 0 else 0

    if not with_cost:
        return {
            "total_tests": total,
            "correct": correct,
            "accuracy": round(accuracy * 100, 2),
            "tests_with_cost": 0,
            "total_cost": 0,
            "avg_cost_per_test": 0,
            "avg_cost_per_correct": 0,
            "total_tokens": 0,
            "avg_tokens_per_test": 0,
            "avg_tokens_per_correct": 0,
            "avg_duration_ms": 0,
            "cost_effectiveness": 0,
        }

    total_cost = sum(r.total_cost_usd for r in with_cost)
    total_tokens = sum(
        r.input_tokens + r.output_tokens + r.cache_read_tokens + r.cache_creation_tokens
        for r in with_cost
    )
    correct_with_cost = sum(1 for r in with_cost if r.score >= 1.0)
    total_duration = sum(r.duration_ms for r in with_cost)

    avg_cost = total_cost / len(with_cost) if with_cost else 0
    avg_tokens = total_tokens / len(with_cost) if with_cost else 0
    cost_per_correct = total_cost / correct_with_cost if correct_with_cost > 0 else float("inf")
    tokens_per_correct = total_tokens / correct_with_cost if correct_with_cost > 0 else float("inf")

    # Cost-effectiveness: accuracy per dollar (higher = better)
    cost_effectiveness = (accuracy * 100) / total_cost if total_cost > 0 else 0

    return {
        "total_tests": total,
        "correct": correct,
        "accuracy": round(accuracy * 100, 2),
        "tests_with_cost": len(with_cost),
        "total_cost": round(total_cost, 4),
        "avg_cost_per_test": round(avg_cost, 6),
        "avg_cost_per_correct": round(cost_per_correct, 6),
        "total_tokens": total_tokens,
        "avg_tokens_per_test": round(avg_tokens),
        "avg_tokens_per_correct": round(tokens_per_correct),
        "avg_duration_ms": round(total_duration / len(with_cost)),
        "cost_effectiveness": round(cost_effectiveness, 1),
    }


def generate_report(results: list[JoinedResult]) -> str:
    """Generate cost-effectiveness markdown report."""
    lines = [
        "# Cost-Effectiveness Analysis",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total Tests**: {len(results)} ({sum(1 for r in results if r.has_cost_data)} with cost data)",
        "",
        "---",
        "",
        "## Methodology",
        "",
        "### Data Sources",
        "",
        "This report joins two independent data sources for each test:",
        "",
        "1. **Accuracy scores** from `evaluator.py` (per-suite `results/*/analysis/results.json`)",
        "   - Each test is scored against ground truth from `harness/questions.json` (23 questions)",
        "   - Scoring: exact match (100%), acceptable variant match (100%), partial keyword credit (50-99%), or miss (0%)",
        "   - Evaluator was run independently per suite, then scores are loaded by this script",
        "",
        "2. **Cost/token data** from raw API responses (per-suite `results/*/raw/haiku/*.json`)",
        "   - Each raw result contains the full Claude Code API response including `usage` block",
        "   - Extracted fields: `input_tokens`, `output_tokens`, `cache_read_input_tokens`,",
        "     `cache_creation_input_tokens`, `total_cost_usd`, `duration_ms`",
        "   - 604/849 tests have cost data; early v4 runs (flat, monolith, shallow) used a format",
        "     that didn't capture usage info",
        "",
        "### Join Logic",
        "",
        "Records are matched by composite key: `(suite, structure, loading_method, question_id)`.",
        "The same key appears in both the evaluator output and the raw response filename.",
        "For example, `v6-extended / shallow-v6 / adddir / NAV-001` links the evaluator's",
        "accuracy score with the API response's token usage for that exact test run.",
        "",
        "### Metrics",
        "",
        "- **Accuracy (strict)**: Percentage of tests scoring exactly 100% (exact or variant match).",
        "  Partial credit does NOT count as correct. This is stricter than the full analysis report",
        "  which averages all scores including partial credit.",
        "- **Cost/Correct Answer**: `total_cost / number_of_correct_answers` for the group",
        "- **Tokens/Correct Answer**: `total_tokens / number_of_correct_answers` — includes",
        "  input, output, cache read, and cache creation tokens",
        "- **Cost-Effectiveness**: `accuracy_percentage / total_cost` (higher = more accuracy per dollar)",
        "",
        "### Caveats",
        "",
        "- Structures with < 20 cost-data points are excluded from the Key Insights rankings",
        "- Token counts include cache tokens; effective cost depends on cache hit rates (74% average)",
        "- All tests used Claude 3.5 Haiku pricing; costs would differ for Sonnet/Opus",
        "- The v4 flat/monolith/shallow structures show $0 cost because those early runs",
        "  didn't capture usage data — their accuracy is real but cost-effectiveness can't be computed",
        "",
        "---",
    ]

    # Overall
    overall = compute_group_metrics(results)
    lines.extend([
        "",
        "## Overall",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Accuracy | {overall['accuracy']}% |",
        f"| Total Cost | ${overall['total_cost']:.2f} |",
        f"| Avg Cost/Test | ${overall['avg_cost_per_test']:.4f} |",
        f"| **Avg Cost/Correct Answer** | **${overall['avg_cost_per_correct']:.4f}** |",
        f"| Avg Tokens/Test | {overall['avg_tokens_per_test']:,} |",
        f"| **Avg Tokens/Correct Answer** | **{overall['avg_tokens_per_correct']:,}** |",
        f"| Cost-Effectiveness | {overall['cost_effectiveness']} accuracy%/$ |",
        "",
        "---",
    ])

    # By structure
    by_structure = defaultdict(list)
    for r in results:
        by_structure[r.structure].append(r)

    structure_metrics = []
    for structure, group in sorted(by_structure.items()):
        m = compute_group_metrics(group)
        m["structure"] = structure
        # Determine corpus
        corpora = set(r.corpus for r in group)
        m["corpus"] = "/".join(sorted(corpora))
        structure_metrics.append(m)

    # Sort by cost per correct answer (lowest first, excluding structures with no cost data)
    def sort_key(x):
        if x["tests_with_cost"] == 0:
            return (1, 999)  # No cost data → sort to bottom
        return (0, x["avg_cost_per_correct"] if x["avg_cost_per_correct"] < 999 else 999)
    structure_metrics.sort(key=sort_key)

    lines.extend([
        "",
        "## By Structure (sorted by cost per correct answer)",
        "",
        "| Structure | Corpus | Accuracy | Cost/Correct | Tokens/Correct | Cost-Eff |",
        "|-----------|--------|----------|-------------|----------------|----------|",
    ])
    for m in structure_metrics:
        cost_correct = f"${m['avg_cost_per_correct']:.4f}" if m['avg_cost_per_correct'] < 999 else "n/a"
        tok_correct = f"{m['avg_tokens_per_correct']:,}" if m['avg_tokens_per_correct'] < 999999999 else "n/a"
        lines.append(
            f"| {m['structure']} | {m['corpus']} | {m['accuracy']}% | "
            f"{cost_correct} | {tok_correct} | {m['cost_effectiveness']} |"
        )

    # By corpus
    by_corpus = defaultdict(list)
    for r in results:
        by_corpus[r.corpus].append(r)

    lines.extend([
        "",
        "---",
        "",
        "## By Corpus Size",
        "",
        "| Corpus | Words | Accuracy | Avg Cost/Test | Cost/Correct | Tokens/Correct |",
        "|--------|-------|----------|---------------|-------------|----------------|",
    ])
    for corpus in ["v4", "v5", "v6"]:
        if corpus not in by_corpus:
            continue
        m = compute_group_metrics(by_corpus[corpus])
        words = CORPUS_INFO.get(corpus, {}).get("words", 0)
        cost_correct = f"${m['avg_cost_per_correct']:.4f}" if m['avg_cost_per_correct'] < 999 else "n/a"
        tok_correct = f"{m['avg_tokens_per_correct']:,}" if m['avg_tokens_per_correct'] < 999999999 else "n/a"
        lines.append(
            f"| {corpus} | {words:,} | {m['accuracy']}% | "
            f"${m['avg_cost_per_test']:.4f} | {cost_correct} | {tok_correct} |"
        )

    # By question type
    by_qtype = defaultdict(list)
    for r in results:
        by_qtype[r.question_type].append(r)

    lines.extend([
        "",
        "---",
        "",
        "## By Question Type",
        "",
        "| Type | Accuracy | Avg Cost/Test | Cost/Correct | Duration/Test |",
        "|------|----------|---------------|-------------|---------------|",
    ])
    for qtype in ["navigation", "cross-reference", "depth"]:
        if qtype not in by_qtype:
            continue
        m = compute_group_metrics(by_qtype[qtype])
        cost_correct = f"${m['avg_cost_per_correct']:.4f}" if m['avg_cost_per_correct'] < 999 else "n/a"
        lines.append(
            f"| {qtype} | {m['accuracy']}% | ${m['avg_cost_per_test']:.4f} | "
            f"{cost_correct} | {m['avg_duration_ms']:,}ms |"
        )

    # By loading method
    by_method = defaultdict(list)
    for r in results:
        by_method[r.loading_method].append(r)

    lines.extend([
        "",
        "---",
        "",
        "## By Loading Method",
        "",
        "| Method | Accuracy | Avg Cost/Test | Cost/Correct | Tokens/Correct |",
        "|--------|----------|---------------|-------------|----------------|",
    ])
    for method in sorted(by_method.keys()):
        m = compute_group_metrics(by_method[method])
        cost_correct = f"${m['avg_cost_per_correct']:.4f}" if m['avg_cost_per_correct'] < 999 else "n/a"
        tok_correct = f"{m['avg_tokens_per_correct']:,}" if m['avg_tokens_per_correct'] < 999999999 else "n/a"
        lines.append(
            f"| {method} | {m['accuracy']}% | ${m['avg_cost_per_test']:.4f} | "
            f"{cost_correct} | {tok_correct} |"
        )

    # Best/worst cost-effectiveness structures
    lines.extend([
        "",
        "---",
        "",
        "## Key Insights",
        "",
    ])

    # Ranked by cost/correct (require >= 20 tests with cost data)
    ranked = [m for m in structure_metrics if m["tests_with_cost"] >= 20]
    ranked_best = sorted(ranked, key=lambda x: x["avg_cost_per_correct"])
    ranked_worst = sorted(ranked, key=lambda x: -x["avg_cost_per_correct"])

    if ranked_best:
        lines.append("### Cheapest per Correct Answer (min 20 tests with cost data)")
        lines.append("")
        for i, m in enumerate(ranked_best[:5], 1):
            lines.append(
                f"{i}. **{m['structure']}** ({m['corpus']}): "
                f"${m['avg_cost_per_correct']:.4f}/correct answer "
                f"({m['accuracy']}% accuracy, {m['avg_tokens_per_correct']:,} tokens/correct)"
            )

        lines.append("")
        lines.append("### Most Expensive per Correct Answer")
        lines.append("")
        for i, m in enumerate(ranked_worst[:3], 1):
            lines.append(
                f"{i}. **{m['structure']}** ({m['corpus']}): "
                f"${m['avg_cost_per_correct']:.4f}/correct answer "
                f"({m['accuracy']}% accuracy, {m['avg_tokens_per_correct']:,} tokens/correct)"
            )

    lines.extend([
        "",
        "---",
        "",
        "*Report generated by cost-effectiveness.py*",
    ])

    return "\n".join(lines)


def main():
    print("Joining evaluator scores with cost data...")
    results = join_data()

    print("Computing cost-effectiveness metrics...")
    report = generate_report(results)

    # Write report
    output_dir = RESULTS_DIR / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / "cost-effectiveness.md"
    md_path.write_text(report)
    print(f"\nReport: {md_path}")

    # Write JSON data
    json_path = output_dir / "cost-effectiveness.json"

    # Group metrics for JSON
    by_structure = defaultdict(list)
    for r in results:
        by_structure[r.structure].append(r)

    json_data = {
        "generated": datetime.now().isoformat(),
        "overall": compute_group_metrics(results),
        "by_structure": {
            s: compute_group_metrics(group)
            for s, group in sorted(by_structure.items())
        },
    }
    json_path.write_text(json.dumps(json_data, indent=2))
    print(f"JSON: {json_path}")


if __name__ == "__main__":
    main()
