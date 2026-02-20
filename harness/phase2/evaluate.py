#!/usr/bin/env python3
"""
Phase 2: Result Evaluator

Scores Phase 2 results against ground truth and generates analysis reports.
Reuses Phase 1 scoring logic (exact → variant → keyword partial credit)
but with Phase 2 result schema and multi-dataset support.

Usage:
    python3 evaluate.py                               # Evaluate all results
    python3 evaluate.py --dataset soong-v5             # One dataset
    python3 evaluate.py --strategy R2.1                # One strategy
    python3 evaluate.py --output results/phase2/report # Write reports
    python3 evaluate.py --verbose                      # Show per-test scores
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "phase2" / "raw"

QUESTION_FILES = {
    "soong-v5": PROJECT_ROOT / "harness" / "questions.json",
    "obsidian": PROJECT_ROOT / "test-datasets" / "obsidian" / "questions.json",
}


@dataclass
class Score:
    """Scoring result for a single test."""
    test_id: str
    strategy: str
    dataset: str
    question_id: str
    question_type: str
    difficulty: str
    points: float          # 0.0 to 1.0
    exact_match: bool
    variant_match: bool
    keyword_matches: list[str]
    confidence: str
    sources_cited: list[str]
    reasoning: str
    cost_usd: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    wall_clock_ms: Optional[int] = None


class Evaluator:
    """Scores responses against ground truth."""

    def __init__(self):
        self.questions: dict[str, dict[str, dict]] = {}  # {dataset: {qid: question}}
        for dataset, qfile in QUESTION_FILES.items():
            if qfile.exists():
                with open(qfile) as f:
                    qs = json.load(f)
                self.questions[dataset] = {q["id"]: q for q in qs}

    def _normalize(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text.lower().strip())

    def _extract_answer(self, response_text: str) -> dict:
        """Extract structured answer from Claude's response."""
        # Try JSON in code block
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try direct JSON
        try:
            return json.loads(response_text)
        except (json.JSONDecodeError, TypeError):
            pass

        # Try to find JSON-like object in the text
        obj_match = re.search(r'\{[^{}]*"answer"\s*:\s*"[^"]*"[^{}]*\}', response_text)
        if obj_match:
            try:
                return json.loads(obj_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback: use entire response as the answer
        return {
            "answer": response_text or "",
            "confidence": "unknown",
            "sources_used": [],
        }

    def score_result(self, result: dict) -> Optional[Score]:
        """Score a single result against ground truth."""
        meta = result.get("metadata", {})
        dataset = meta.get("dataset", "")
        qid = meta.get("question_id", "")
        strategy = meta.get("strategy", "")

        if dataset not in self.questions:
            return None
        if qid not in self.questions[dataset]:
            print(f"Warning: Unknown question {qid} in {dataset}", file=sys.stderr)
            return None

        question = self.questions[dataset][qid]
        gt = question["ground_truth"]
        exact_answer = gt["exact_answer"]
        variants = gt.get("acceptable_variants", [])
        keywords = gt.get("partial_credit_keywords", [])

        # Extract answer from response
        response_data = self._extract_answer(result.get("response", ""))
        answer = response_data.get("answer", "")
        confidence = response_data.get("confidence", "unknown")
        sources = response_data.get("sources_used", [])

        # Scoring (same as Phase 1)
        points = 0.0
        exact_match = False
        variant_match = False
        keyword_matches = []
        reasoning_parts = []

        norm_answer = self._normalize(answer)
        norm_truth = self._normalize(exact_answer)

        # Exact match (1.0)
        if norm_truth in norm_answer or norm_answer in norm_truth:
            exact_match = True
            points = 1.0
            reasoning_parts.append("Exact match")
        else:
            # Variant match (0.9)
            for variant in variants:
                if self._normalize(variant) in norm_answer:
                    variant_match = True
                    points = 0.9
                    reasoning_parts.append(f"Variant: {variant}")
                    break

            # Keyword partial credit (0.1-0.7)
            if not variant_match and keywords:
                for kw in keywords:
                    if self._normalize(kw) in norm_answer:
                        keyword_matches.append(kw)
                if keyword_matches:
                    coverage = len(keyword_matches) / len(keywords)
                    points = 0.1 + (0.6 * coverage)
                    reasoning_parts.append(f"Keywords: {len(keyword_matches)}/{len(keywords)}")

        if points == 0.0:
            reasoning_parts.append("No match")

        # Extract cost data
        cost = result.get("cost", {})

        return Score(
            test_id=result.get("test_id", f"{strategy}-{dataset}-{qid}"),
            strategy=strategy,
            dataset=dataset,
            question_id=qid,
            question_type=question.get("type", "unknown"),
            difficulty=question.get("difficulty", "unknown"),
            points=points,
            exact_match=exact_match,
            variant_match=variant_match,
            keyword_matches=keyword_matches,
            confidence=confidence,
            sources_cited=sources,
            reasoning="; ".join(reasoning_parts),
            cost_usd=cost.get("total_cost_usd"),
            input_tokens=cost.get("input_tokens"),
            output_tokens=cost.get("output_tokens"),
            wall_clock_ms=result.get("performance", {}).get("wall_clock_ms"),
        )

    def evaluate_directory(self, results_dir: Path,
                           filter_dataset: str = "",
                           filter_strategy: str = "") -> list[Score]:
        """Evaluate all result files."""
        scores = []
        for result_file in sorted(results_dir.rglob("*.json")):
            # Skip run manifests
            if result_file.name.startswith("run-"):
                continue

            try:
                with open(result_file) as f:
                    result = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not read {result_file}: {e}", file=sys.stderr)
                continue

            # Must have metadata
            if "metadata" not in result:
                continue

            meta = result["metadata"]

            # Apply filters
            if filter_dataset and meta.get("dataset") != filter_dataset:
                continue
            if filter_strategy and meta.get("strategy") != filter_strategy:
                continue

            score = self.score_result(result)
            if score:
                scores.append(score)

        return scores


class Reporter:
    """Generates analysis from scored results."""

    def __init__(self, scores: list[Score]):
        self.scores = scores

    def _avg(self, values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def summary(self) -> dict:
        """Aggregate statistics."""
        if not self.scores:
            return {"error": "No scores"}

        by_strategy = defaultdict(list)
        by_dataset = defaultdict(list)
        by_strategy_dataset = defaultdict(list)
        by_question_type = defaultdict(list)
        by_difficulty = defaultdict(list)

        total_cost = 0.0
        total_tokens = 0

        for s in self.scores:
            by_strategy[s.strategy].append(s.points)
            by_dataset[s.dataset].append(s.points)
            by_strategy_dataset[(s.strategy, s.dataset)].append(s.points)
            by_question_type[s.question_type].append(s.points)
            by_difficulty[s.difficulty].append(s.points)
            if s.cost_usd:
                total_cost += s.cost_usd
            if s.input_tokens and s.output_tokens:
                total_tokens += s.input_tokens + s.output_tokens

        return {
            "overall": {
                "total_tests": len(self.scores),
                "average_score": self._avg([s.points for s in self.scores]),
                "exact_matches": sum(1 for s in self.scores if s.exact_match),
                "variant_matches": sum(1 for s in self.scores if s.variant_match),
                "zero_scores": sum(1 for s in self.scores if s.points == 0.0),
                "total_cost_usd": round(total_cost, 4),
                "total_tokens": total_tokens,
            },
            "by_strategy": {
                k: {"avg": self._avg(v), "count": len(v),
                     "exact": sum(1 for p in v if p == 1.0)}
                for k, v in sorted(by_strategy.items())
            },
            "by_dataset": {
                k: {"avg": self._avg(v), "count": len(v)}
                for k, v in sorted(by_dataset.items())
            },
            "by_strategy_dataset": {
                f"{s}/{d}": {"avg": self._avg(v), "count": len(v),
                              "exact": sum(1 for p in v if p == 1.0)}
                for (s, d), v in sorted(by_strategy_dataset.items())
            },
            "by_question_type": {
                k: {"avg": self._avg(v), "count": len(v)}
                for k, v in sorted(by_question_type.items())
            },
            "by_difficulty": {
                k: {"avg": self._avg(v), "count": len(v)}
                for k, v in sorted(by_difficulty.items())
            },
        }

    def cost_effectiveness(self) -> dict:
        """Cost per correct answer by strategy."""
        strategy_costs = defaultdict(lambda: {"cost": 0.0, "correct": 0, "tests": 0})

        for s in self.scores:
            key = s.strategy
            strategy_costs[key]["tests"] += 1
            if s.cost_usd:
                strategy_costs[key]["cost"] += s.cost_usd
            if s.exact_match or s.variant_match:
                strategy_costs[key]["correct"] += 1

        result = {}
        for strategy, data in sorted(strategy_costs.items()):
            cost_per_correct = (
                data["cost"] / data["correct"] if data["correct"] > 0 else float("inf")
            )
            result[strategy] = {
                "total_cost": round(data["cost"], 4),
                "correct_answers": data["correct"],
                "total_tests": data["tests"],
                "accuracy": data["correct"] / data["tests"] if data["tests"] > 0 else 0,
                "cost_per_correct": round(cost_per_correct, 4) if cost_per_correct != float("inf") else None,
            }
        return result

    def strategy_comparison(self) -> dict:
        """Head-to-head strategy comparison on same questions."""
        # Group scores by (dataset, question_id) → {strategy: points}
        question_scores = defaultdict(dict)
        for s in self.scores:
            key = (s.dataset, s.question_id)
            question_scores[key][s.strategy] = s.points

        # Count wins for each strategy pair
        strategies = sorted(set(s.strategy for s in self.scores))
        wins = {s: defaultdict(int) for s in strategies}

        for key, strat_scores in question_scores.items():
            for i, s1 in enumerate(strategies):
                for s2 in strategies[i+1:]:
                    if s1 in strat_scores and s2 in strat_scores:
                        if strat_scores[s1] > strat_scores[s2]:
                            wins[s1][s2] += 1
                        elif strat_scores[s2] > strat_scores[s1]:
                            wins[s2][s1] += 1

        return {"strategies": strategies, "wins": {k: dict(v) for k, v in wins.items()}}

    def markdown_report(self) -> str:
        """Generate full markdown report."""
        stats = self.summary()
        cost_eff = self.cost_effectiveness()

        lines = [
            "# Phase 2: Context Strategy Test Results",
            "",
            f"**{stats['overall']['total_tests']} tests** evaluated.",
            f"**Total cost**: ${stats['overall']['total_cost_usd']:.2f}",
            "",
            "## Overall Performance",
            "",
            f"- Average Score: **{stats['overall']['average_score']:.1%}**",
            f"- Exact Matches: {stats['overall']['exact_matches']}",
            f"- Variant Matches: {stats['overall']['variant_matches']}",
            f"- Zero Scores: {stats['overall']['zero_scores']}",
            "",
            "## Strategy Rankings",
            "",
            "| Strategy | Avg Score | Exact | Tests | Cost/Correct |",
            "|----------|-----------|-------|-------|--------------|",
        ]

        # Sort strategies by average score descending
        ranked = sorted(
            stats["by_strategy"].items(),
            key=lambda x: x[1]["avg"],
            reverse=True,
        )
        for strategy, data in ranked:
            cpc = cost_eff.get(strategy, {}).get("cost_per_correct")
            cpc_str = f"${cpc:.3f}" if cpc else "N/A"
            lines.append(
                f"| {strategy} | {data['avg']:.1%} | "
                f"{data['exact']}/{data['count']} | {data['count']} | {cpc_str} |"
            )

        # By dataset
        lines.extend([
            "",
            "## By Dataset",
            "",
            "| Dataset | Avg Score | Tests |",
            "|---------|-----------|-------|",
        ])
        for dataset, data in stats["by_dataset"].items():
            lines.append(f"| {dataset} | {data['avg']:.1%} | {data['count']} |")

        # Strategy × Dataset matrix
        lines.extend([
            "",
            "## Strategy × Dataset Matrix",
            "",
            "| Strategy × Dataset | Avg Score | Exact | Tests |",
            "|---------------------|-----------|-------|-------|",
        ])
        for key, data in stats["by_strategy_dataset"].items():
            lines.append(f"| {key} | {data['avg']:.1%} | {data['exact']}/{data['count']} | {data['count']} |")

        # By question type
        lines.extend([
            "",
            "## By Question Type",
            "",
            "| Type | Avg Score | Tests |",
            "|------|-----------|-------|",
        ])
        for qtype, data in stats["by_question_type"].items():
            lines.append(f"| {qtype} | {data['avg']:.1%} | {data['count']} |")

        # By difficulty
        lines.extend([
            "",
            "## By Difficulty",
            "",
            "| Difficulty | Avg Score | Tests |",
            "|------------|-----------|-------|",
        ])
        for diff, data in stats["by_difficulty"].items():
            lines.append(f"| {diff} | {data['avg']:.1%} | {data['count']} |")

        lines.extend(["", f"*Generated: {__import__('datetime').datetime.now().isoformat()}*"])
        return "\n".join(lines)

    def export_json(self) -> dict:
        """Full JSON export."""
        return {
            "summary": self.summary(),
            "cost_effectiveness": self.cost_effectiveness(),
            "strategy_comparison": self.strategy_comparison(),
            "scores": [
                {
                    "test_id": s.test_id,
                    "strategy": s.strategy,
                    "dataset": s.dataset,
                    "question_id": s.question_id,
                    "question_type": s.question_type,
                    "difficulty": s.difficulty,
                    "points": s.points,
                    "exact_match": s.exact_match,
                    "variant_match": s.variant_match,
                    "keyword_matches": s.keyword_matches,
                    "confidence": s.confidence,
                    "sources_cited": s.sources_cited,
                    "reasoning": s.reasoning,
                    "cost_usd": s.cost_usd,
                    "input_tokens": s.input_tokens,
                    "output_tokens": s.output_tokens,
                    "wall_clock_ms": s.wall_clock_ms,
                }
                for s in self.scores
            ],
        }


def main():
    parser = argparse.ArgumentParser(description="Phase 2 Result Evaluator")
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR,
                        help="Results directory")
    parser.add_argument("--dataset", default="", help="Filter by dataset")
    parser.add_argument("--strategy", default="", help="Filter by strategy")
    parser.add_argument("--output", type=Path, help="Output directory for reports")
    parser.add_argument("--format", choices=["markdown", "json", "both"],
                        default="both", help="Output format")
    parser.add_argument("--verbose", action="store_true",
                        help="Show per-test scores")

    args = parser.parse_args()

    if not args.results_dir.exists():
        print(f"Error: Results directory not found: {args.results_dir}", file=sys.stderr)
        sys.exit(1)

    evaluator = Evaluator()
    scores = evaluator.evaluate_directory(
        args.results_dir,
        filter_dataset=args.dataset,
        filter_strategy=args.strategy,
    )

    if not scores:
        print("No results found to evaluate.", file=sys.stderr)
        sys.exit(1)

    print(f"Evaluated {len(scores)} results.")

    if args.verbose:
        print("\nDetailed Scores:")
        for s in scores:
            status = "✓" if s.exact_match else "~" if s.variant_match else "✗"
            print(f"  {status} {s.strategy}/{s.dataset}/{s.question_id}: "
                  f"{s.points:.2f} — {s.reasoning}")

    reporter = Reporter(scores)

    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)

        if args.format in ("markdown", "both"):
            md_path = args.output / "report.md"
            md_path.write_text(reporter.markdown_report())
            print(f"Markdown report: {md_path}")

        if args.format in ("json", "both"):
            json_path = args.output / "results.json"
            json_path.write_text(json.dumps(reporter.export_json(), indent=2))
            print(f"JSON report: {json_path}")
    else:
        if args.format == "json":
            print(json.dumps(reporter.export_json(), indent=2))
        else:
            print(reporter.markdown_report())


if __name__ == "__main__":
    main()
