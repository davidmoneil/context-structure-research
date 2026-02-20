#!/usr/bin/env python3
"""
Context Structure Research - Cost & Token Analyzer

Analyzes API usage, token counts, and costs across test runs.
Generates detailed reports for understanding cost-per-accuracy tradeoffs.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class TokenUsage:
    """Token usage for a single test."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    total_cost_usd: float = 0.0
    duration_ms: int = 0

    @property
    def total_input_tokens(self) -> int:
        return self.input_tokens + self.cache_read_tokens + self.cache_creation_tokens

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.output_tokens

    @property
    def cache_hit_rate(self) -> float:
        total_cache = self.cache_read_tokens + self.cache_creation_tokens
        if total_cache == 0:
            return 0.0
        return self.cache_read_tokens / total_cache


@dataclass
class TestResult:
    """Full test result with usage data."""
    question_id: str
    question_type: str
    structure: str
    loading_method: str
    model: str
    corpus_version: str
    usage: TokenUsage
    success: bool = True
    file_path: str = ""


class CostAnalyzer:
    """Analyzes token usage and costs from test results."""

    def __init__(self, questions_file: Optional[Path] = None):
        self.questions = {}
        if questions_file and questions_file.exists():
            with open(questions_file) as f:
                questions = json.load(f)
                self.questions = {q["id"]: q for q in questions}

    def _extract_corpus_version(self, file_path: Path) -> str:
        """Extract corpus version from file path."""
        path_str = str(file_path)
        for version in ["v6", "v5", "v4", "v3", "v2", "v1"]:
            if f"/{version}/" in path_str or f"results/{version}" in path_str:
                return version
        return "unknown"

    def _parse_result_file(self, file_path: Path) -> Optional[TestResult]:
        """Parse a single result JSON file."""
        try:
            with open(file_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
            return None

        question_id = data.get("question_id", "")
        config = data.get("config", {})

        # Extract usage from response
        usage = TokenUsage()
        response_str = data.get("response", "")

        try:
            response = json.loads(response_str) if isinstance(response_str, str) else response_str

            # Get usage data
            usage_data = response.get("usage", {})
            usage.input_tokens = usage_data.get("input_tokens", 0)
            usage.output_tokens = usage_data.get("output_tokens", 0)
            usage.cache_read_tokens = usage_data.get("cache_read_input_tokens", 0)
            usage.cache_creation_tokens = usage_data.get("cache_creation_input_tokens", 0)
            usage.total_cost_usd = response.get("total_cost_usd", 0.0)
            usage.duration_ms = response.get("duration_ms", 0)

            # Also check modelUsage for more detailed breakdown
            model_usage = response.get("modelUsage", {})
            for model_data in model_usage.values():
                if "cacheReadInputTokens" in model_data:
                    usage.cache_read_tokens = max(usage.cache_read_tokens, model_data.get("cacheReadInputTokens", 0))
                if "cacheCreationInputTokens" in model_data:
                    usage.cache_creation_tokens = max(usage.cache_creation_tokens, model_data.get("cacheCreationInputTokens", 0))

        except (json.JSONDecodeError, TypeError, AttributeError):
            pass

        # Get question type
        question_type = "unknown"
        if question_id in self.questions:
            question_type = self.questions[question_id].get("type", "unknown")
        elif question_id.startswith("NAV"):
            question_type = "navigation"
        elif question_id.startswith("XREF"):
            question_type = "cross-reference"
        elif question_id.startswith("DEPTH"):
            question_type = "depth"

        return TestResult(
            question_id=question_id,
            question_type=question_type,
            structure=config.get("structure", "unknown"),
            loading_method=config.get("loading_method", "unknown"),
            model=config.get("model", "haiku"),
            corpus_version=self._extract_corpus_version(file_path),
            usage=usage,
            success=usage.total_cost_usd > 0,
            file_path=str(file_path),
        )

    def analyze_directory(self, results_dir: Path) -> list[TestResult]:
        """Analyze all results in a directory."""
        results = []
        excluded_zero_cost = 0
        for file_path in results_dir.rglob("*.json"):
            # Skip analysis output files
            if "analysis" in str(file_path) or "report" in file_path.name:
                continue
            result = self._parse_result_file(file_path)
            if result and result.success:
                results.append(result)
            elif result and not result.success:
                excluded_zero_cost += 1
        if excluded_zero_cost:
            print(f"  Note: {excluded_zero_cost} results excluded (zero cost / no usage data)", file=sys.stderr)
        return results


class CostReporter:
    """Generates cost analysis reports."""

    def __init__(self, results: list[TestResult]):
        self.results = results

    def _aggregate_usage(self, results: list[TestResult]) -> dict:
        """Aggregate usage stats for a group of results."""
        if not results:
            return {
                "count": 0,
                "total_cost_usd": 0,
                "avg_cost_usd": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cache_read_tokens": 0,
                "total_cache_creation_tokens": 0,
                "avg_input_tokens": 0,
                "avg_output_tokens": 0,
                "avg_duration_ms": 0,
                "avg_cache_hit_rate": 0,
            }

        total_cost = sum(r.usage.total_cost_usd for r in results)
        total_input = sum(r.usage.total_input_tokens for r in results)
        total_output = sum(r.usage.output_tokens for r in results)
        total_cache_read = sum(r.usage.cache_read_tokens for r in results)
        total_cache_create = sum(r.usage.cache_creation_tokens for r in results)
        total_duration = sum(r.usage.duration_ms for r in results)

        cache_rates = [r.usage.cache_hit_rate for r in results if r.usage.cache_read_tokens + r.usage.cache_creation_tokens > 0]
        avg_cache_rate = sum(cache_rates) / len(cache_rates) if cache_rates else 0

        count = len(results)
        return {
            "count": count,
            "total_cost_usd": round(total_cost, 4),
            "avg_cost_usd": round(total_cost / count, 6),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cache_read_tokens": total_cache_read,
            "total_cache_creation_tokens": total_cache_create,
            "avg_input_tokens": round(total_input / count),
            "avg_output_tokens": round(total_output / count),
            "avg_duration_ms": round(total_duration / count),
            "avg_cache_hit_rate": round(avg_cache_rate, 3),
        }

    def overall_stats(self) -> dict:
        """Calculate overall statistics."""
        return self._aggregate_usage(self.results)

    def by_corpus_version(self) -> dict:
        """Aggregate by corpus version (v4, v5, etc.)."""
        grouped = defaultdict(list)
        for r in self.results:
            grouped[r.corpus_version].append(r)
        return {k: self._aggregate_usage(v) for k, v in sorted(grouped.items())}

    def by_structure(self) -> dict:
        """Aggregate by structure type."""
        grouped = defaultdict(list)
        for r in self.results:
            grouped[r.structure].append(r)
        return {k: self._aggregate_usage(v) for k, v in sorted(grouped.items())}

    def by_loading_method(self) -> dict:
        """Aggregate by loading method."""
        grouped = defaultdict(list)
        for r in self.results:
            grouped[r.loading_method].append(r)
        return {k: self._aggregate_usage(v) for k, v in sorted(grouped.items())}

    def by_question_type(self) -> dict:
        """Aggregate by question type."""
        grouped = defaultdict(list)
        for r in self.results:
            grouped[r.question_type].append(r)
        return {k: self._aggregate_usage(v) for k, v in sorted(grouped.items())}

    def by_structure_and_version(self) -> dict:
        """Cross-tabulation of structure × corpus version."""
        grouped = defaultdict(list)
        for r in self.results:
            key = f"{r.corpus_version}/{r.structure}"
            grouped[key].append(r)
        return {k: self._aggregate_usage(v) for k, v in sorted(grouped.items())}

    def version_comparison(self) -> dict:
        """Compare V4 vs V5 costs for same structure/loading combos."""
        v4_results = defaultdict(list)
        v5_results = defaultdict(list)

        for r in self.results:
            key = (r.structure, r.loading_method)
            if r.corpus_version == "v4":
                v4_results[key].append(r)
            elif r.corpus_version == "v5":
                v5_results[key].append(r)

        comparisons = []
        for key in set(v4_results.keys()) | set(v5_results.keys()):
            v4_stats = self._aggregate_usage(v4_results.get(key, []))
            v5_stats = self._aggregate_usage(v5_results.get(key, []))

            if v4_stats["count"] > 0 and v5_stats["count"] > 0:
                cost_increase = (v5_stats["avg_cost_usd"] - v4_stats["avg_cost_usd"]) / v4_stats["avg_cost_usd"] if v4_stats["avg_cost_usd"] > 0 else 0
                token_increase = (v5_stats["avg_input_tokens"] - v4_stats["avg_input_tokens"]) / v4_stats["avg_input_tokens"] if v4_stats["avg_input_tokens"] > 0 else 0

                comparisons.append({
                    "structure": key[0],
                    "loading_method": key[1],
                    "v4_avg_cost": v4_stats["avg_cost_usd"],
                    "v5_avg_cost": v5_stats["avg_cost_usd"],
                    "cost_increase_pct": round(cost_increase * 100, 1),
                    "v4_avg_tokens": v4_stats["avg_input_tokens"],
                    "v5_avg_tokens": v5_stats["avg_input_tokens"],
                    "token_increase_pct": round(token_increase * 100, 1),
                })

        return {
            "comparisons": comparisons,
            "summary": {
                "avg_cost_increase_pct": round(sum(c["cost_increase_pct"] for c in comparisons) / len(comparisons), 1) if comparisons else 0,
                "avg_token_increase_pct": round(sum(c["token_increase_pct"] for c in comparisons) / len(comparisons), 1) if comparisons else 0,
            }
        }

    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report."""
        overall = self.overall_stats()
        by_version = self.by_corpus_version()
        by_structure = self.by_structure()
        by_loading = self.by_loading_method()
        by_qtype = self.by_question_type()
        version_cmp = self.version_comparison()

        lines = [
            "# Context Structure Research - Cost Analysis Report",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Tests Analyzed**: {overall['count']}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Tests | {overall['count']} |",
            f"| Total Cost | ${overall['total_cost_usd']:.4f} |",
            f"| Avg Cost/Test | ${overall['avg_cost_usd']:.6f} |",
            f"| Total Input Tokens | {overall['total_input_tokens']:,} |",
            f"| Total Output Tokens | {overall['total_output_tokens']:,} |",
            f"| Avg Cache Hit Rate | {overall['avg_cache_hit_rate']:.1%} |",
            f"| Avg Duration | {overall['avg_duration_ms']:,}ms |",
            "",
            "---",
            "",
            "## Cost by Corpus Version",
            "",
            "| Version | Tests | Total Cost | Avg Cost | Avg Tokens | Avg Duration |",
            "|---------|-------|------------|----------|------------|--------------|",
        ]

        for version, stats in by_version.items():
            lines.append(
                f"| {version} | {stats['count']} | ${stats['total_cost_usd']:.4f} | "
                f"${stats['avg_cost_usd']:.6f} | {stats['avg_input_tokens']:,} | {stats['avg_duration_ms']:,}ms |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Cost by Structure Type",
            "",
            "| Structure | Tests | Total Cost | Avg Cost | Avg Input Tokens | Cache Hit Rate |",
            "|-----------|-------|------------|----------|------------------|----------------|",
        ])

        for structure, stats in by_structure.items():
            lines.append(
                f"| {structure} | {stats['count']} | ${stats['total_cost_usd']:.4f} | "
                f"${stats['avg_cost_usd']:.6f} | {stats['avg_input_tokens']:,} | {stats['avg_cache_hit_rate']:.1%} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Cost by Loading Method",
            "",
            "| Method | Tests | Total Cost | Avg Cost | Avg Tokens |",
            "|--------|-------|------------|----------|------------|",
        ])

        for method, stats in by_loading.items():
            lines.append(
                f"| {method} | {stats['count']} | ${stats['total_cost_usd']:.4f} | "
                f"${stats['avg_cost_usd']:.6f} | {stats['avg_input_tokens']:,} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Cost by Question Type",
            "",
            "| Question Type | Tests | Total Cost | Avg Cost | Avg Duration |",
            "|---------------|-------|------------|----------|--------------|",
        ])

        for qtype, stats in by_qtype.items():
            lines.append(
                f"| {qtype} | {stats['count']} | ${stats['total_cost_usd']:.4f} | "
                f"${stats['avg_cost_usd']:.6f} | {stats['avg_duration_ms']:,}ms |"
            )

        if version_cmp["comparisons"]:
            lines.extend([
                "",
                "---",
                "",
                "## V4 vs V5 Comparison",
                "",
                f"**Average Cost Increase**: {version_cmp['summary']['avg_cost_increase_pct']}%",
                f"**Average Token Increase**: {version_cmp['summary']['avg_token_increase_pct']}%",
                "",
                "| Structure | Loading | V4 Avg Cost | V5 Avg Cost | Cost Δ | V4 Tokens | V5 Tokens | Token Δ |",
                "|-----------|---------|-------------|-------------|--------|-----------|-----------|---------|",
            ])

            for cmp in version_cmp["comparisons"]:
                lines.append(
                    f"| {cmp['structure']} | {cmp['loading_method']} | "
                    f"${cmp['v4_avg_cost']:.6f} | ${cmp['v5_avg_cost']:.6f} | "
                    f"+{cmp['cost_increase_pct']}% | "
                    f"{cmp['v4_avg_tokens']:,} | {cmp['v5_avg_tokens']:,} | "
                    f"+{cmp['token_increase_pct']}% |"
                )

        lines.extend([
            "",
            "---",
            "",
            "## Cache Efficiency Analysis",
            "",
            "| Version | Cache Read Tokens | Cache Creation Tokens | Effective Cache Rate |",
            "|---------|-------------------|----------------------|---------------------|",
        ])

        for version, stats in by_version.items():
            total_cache = stats['total_cache_read_tokens'] + stats['total_cache_creation_tokens']
            eff_rate = stats['total_cache_read_tokens'] / total_cache if total_cache > 0 else 0
            lines.append(
                f"| {version} | {stats['total_cache_read_tokens']:,} | "
                f"{stats['total_cache_creation_tokens']:,} | {eff_rate:.1%} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "*Report generated by cost-analyzer.py*",
        ])

        return "\n".join(lines)

    def export_json(self) -> dict:
        """Export full analysis as JSON."""
        return {
            "generated_at": datetime.now().isoformat(),
            "overall": self.overall_stats(),
            "by_corpus_version": self.by_corpus_version(),
            "by_structure": self.by_structure(),
            "by_loading_method": self.by_loading_method(),
            "by_question_type": self.by_question_type(),
            "by_structure_and_version": self.by_structure_and_version(),
            "version_comparison": self.version_comparison(),
            "raw_results": [
                {
                    "question_id": r.question_id,
                    "question_type": r.question_type,
                    "structure": r.structure,
                    "loading_method": r.loading_method,
                    "model": r.model,
                    "corpus_version": r.corpus_version,
                    "cost_usd": r.usage.total_cost_usd,
                    "input_tokens": r.usage.total_input_tokens,
                    "output_tokens": r.usage.output_tokens,
                    "cache_read_tokens": r.usage.cache_read_tokens,
                    "cache_creation_tokens": r.usage.cache_creation_tokens,
                    "duration_ms": r.usage.duration_ms,
                }
                for r in self.results
            ],
        }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze token usage and costs from context structure research"
    )
    parser.add_argument(
        "results_dirs",
        nargs="+",
        type=Path,
        help="One or more directories containing result JSON files",
    )
    parser.add_argument(
        "--questions",
        type=Path,
        default=Path(__file__).parent / "questions.json",
        help="Path to questions.json file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for reports",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="both",
        help="Output format",
    )

    args = parser.parse_args()

    # Collect all results
    analyzer = CostAnalyzer(args.questions)
    all_results = []

    for results_dir in args.results_dirs:
        if not results_dir.exists():
            print(f"Warning: Directory not found: {results_dir}", file=sys.stderr)
            continue
        results = analyzer.analyze_directory(results_dir)
        all_results.extend(results)
        print(f"Loaded {len(results)} results from {results_dir}")

    if not all_results:
        print("No results found to analyze.", file=sys.stderr)
        sys.exit(1)

    print(f"\nTotal: {len(all_results)} test results")

    # Generate reports
    reporter = CostReporter(all_results)

    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)

        if args.format in ("markdown", "both"):
            md_path = args.output / "cost-report.md"
            md_path.write_text(reporter.generate_markdown_report())
            print(f"Markdown report: {md_path}")

        if args.format in ("json", "both"):
            json_path = args.output / "cost-analysis.json"
            json_path.write_text(json.dumps(reporter.export_json(), indent=2))
            print(f"JSON report: {json_path}")
    else:
        # Print to stdout
        if args.format == "json":
            print(json.dumps(reporter.export_json(), indent=2))
        else:
            print(reporter.generate_markdown_report())


if __name__ == "__main__":
    main()
