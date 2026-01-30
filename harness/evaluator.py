#!/usr/bin/env python3
"""
Context Structure Research - Response Evaluator

Scores Claude's responses against ground truth and generates analysis reports.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class GroundTruth:
    """Ground truth for a question."""
    exact_answer: str
    acceptable_variants: list[str] = field(default_factory=list)
    partial_credit_keywords: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)


@dataclass
class Score:
    """Scoring result for a single response."""
    question_id: str
    config: dict
    points: float  # 0.0 to 1.0
    exact_match: bool
    variant_match: bool
    keyword_matches: list[str]
    confidence: str
    sources_cited: list[str]
    reasoning: str


class Evaluator:
    """Evaluates Claude responses against ground truth."""

    def __init__(self, questions_file: Path):
        self.questions = self._load_questions(questions_file)

    def _load_questions(self, path: Path) -> dict:
        """Load questions and ground truth."""
        with open(path) as f:
            questions = json.load(f)
        return {q["id"]: q for q in questions}

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        return re.sub(r'\s+', ' ', text.lower().strip())

    def _extract_response_data(self, response_text: str) -> dict:
        """Extract structured data from Claude's response."""
        # Try to parse as JSON
        try:
            # Response might be wrapped in markdown code block
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Try to extract key fields from text
        data = {
            "answer": response_text,
            "confidence": "unknown",
            "sources_used": []
        }

        # Look for answer pattern
        answer_match = re.search(r'"answer"\s*:\s*"([^"]+)"', response_text)
        if answer_match:
            data["answer"] = answer_match.group(1)

        # Look for confidence
        conf_match = re.search(r'"confidence"\s*:\s*"(high|medium|low)"', response_text, re.I)
        if conf_match:
            data["confidence"] = conf_match.group(1).lower()

        return data

    def score_response(self, result_file: Path) -> Optional[Score]:
        """Score a single response file."""
        with open(result_file) as f:
            result = json.load(f)

        question_id = result["question_id"]
        if question_id not in self.questions:
            print(f"Warning: Unknown question ID: {question_id}", file=sys.stderr)
            return None

        question = self.questions[question_id]
        ground_truth = GroundTruth(
            exact_answer=question["ground_truth"]["exact_answer"],
            acceptable_variants=question["ground_truth"].get("acceptable_variants", []),
            partial_credit_keywords=question["ground_truth"].get("partial_credit_keywords", []),
            source_files=question["ground_truth"].get("source_files", []),
        )

        # Extract response data
        response_data = self._extract_response_data(result["response"])
        answer = response_data.get("answer", "")
        confidence = response_data.get("confidence", "unknown")
        sources_cited = response_data.get("sources_used", [])

        # Scoring
        points = 0.0
        exact_match = False
        variant_match = False
        keyword_matches = []
        reasoning_parts = []

        normalized_answer = self._normalize(answer)
        normalized_truth = self._normalize(ground_truth.exact_answer)

        # Check exact match (1.0 points)
        if normalized_truth in normalized_answer or normalized_answer in normalized_truth:
            exact_match = True
            points = 1.0
            reasoning_parts.append("Exact match found")
        else:
            # Check acceptable variants (0.9 points)
            for variant in ground_truth.acceptable_variants:
                if self._normalize(variant) in normalized_answer:
                    variant_match = True
                    points = 0.9
                    reasoning_parts.append(f"Variant match: {variant}")
                    break

            # Check partial credit keywords
            if not variant_match and ground_truth.partial_credit_keywords:
                for keyword in ground_truth.partial_credit_keywords:
                    if self._normalize(keyword) in normalized_answer:
                        keyword_matches.append(keyword)

                if keyword_matches:
                    # Partial credit: 0.1-0.7 based on keyword coverage
                    coverage = len(keyword_matches) / len(ground_truth.partial_credit_keywords)
                    points = 0.1 + (0.6 * coverage)
                    reasoning_parts.append(f"Keyword matches: {keyword_matches}")

        if points == 0.0:
            reasoning_parts.append("No match found")

        return Score(
            question_id=question_id,
            config=result["config"],
            points=points,
            exact_match=exact_match,
            variant_match=variant_match,
            keyword_matches=keyword_matches,
            confidence=confidence,
            sources_cited=sources_cited,
            reasoning="; ".join(reasoning_parts),
        )

    def evaluate_directory(self, results_dir: Path) -> list[Score]:
        """Evaluate all results in a directory."""
        scores = []
        for result_file in results_dir.rglob("*.json"):
            score = self.score_response(result_file)
            if score:
                scores.append(score)
        return scores


class Reporter:
    """Generates analysis reports from scores."""

    def __init__(self, scores: list[Score], questions: dict):
        self.scores = scores
        self.questions = questions

    def summary_stats(self) -> dict:
        """Calculate summary statistics."""
        if not self.scores:
            return {"error": "No scores to analyze"}

        total_points = sum(s.points for s in self.scores)
        count = len(self.scores)

        # Group by dimensions
        by_structure = defaultdict(list)
        by_model = defaultdict(list)
        by_loading = defaultdict(list)
        by_question_type = defaultdict(list)

        for score in self.scores:
            by_structure[score.config["structure"]].append(score.points)
            by_model[score.config["model"]].append(score.points)
            by_loading[score.config["loading_method"]].append(score.points)

            q_type = self.questions[score.question_id]["type"]
            by_question_type[q_type].append(score.points)

        def avg(lst):
            return sum(lst) / len(lst) if lst else 0

        return {
            "overall": {
                "total_tests": count,
                "average_score": total_points / count,
                "exact_matches": sum(1 for s in self.scores if s.exact_match),
                "variant_matches": sum(1 for s in self.scores if s.variant_match),
            },
            "by_structure": {k: avg(v) for k, v in sorted(by_structure.items())},
            "by_model": {k: avg(v) for k, v in sorted(by_model.items())},
            "by_loading_method": {k: avg(v) for k, v in sorted(by_loading.items())},
            "by_question_type": {k: avg(v) for k, v in sorted(by_question_type.items())},
        }

    def loading_comparison(self) -> dict:
        """Compare classic vs adddir loading methods."""
        classic_scores = defaultdict(list)
        adddir_scores = defaultdict(list)

        for score in self.scores:
            key = (score.config["structure"], score.config["model"], score.question_id)
            if score.config["loading_method"] == "classic":
                classic_scores[key].append(score.points)
            else:
                adddir_scores[key].append(score.points)

        comparisons = []
        for key in set(classic_scores.keys()) & set(adddir_scores.keys()):
            c_avg = sum(classic_scores[key]) / len(classic_scores[key])
            a_avg = sum(adddir_scores[key]) / len(adddir_scores[key])
            comparisons.append({
                "structure": key[0],
                "model": key[1],
                "question": key[2],
                "classic_score": c_avg,
                "adddir_score": a_avg,
                "difference": a_avg - c_avg,
                "winner": "adddir" if a_avg > c_avg else "classic" if c_avg > a_avg else "tie",
            })

        # Summary
        adddir_wins = sum(1 for c in comparisons if c["winner"] == "adddir")
        classic_wins = sum(1 for c in comparisons if c["winner"] == "classic")
        ties = sum(1 for c in comparisons if c["winner"] == "tie")

        return {
            "comparisons": comparisons,
            "summary": {
                "adddir_wins": adddir_wins,
                "classic_wins": classic_wins,
                "ties": ties,
                "total_comparisons": len(comparisons),
            }
        }

    def generate_markdown_report(self) -> str:
        """Generate a markdown analysis report."""
        stats = self.summary_stats()
        loading_cmp = self.loading_comparison()

        lines = [
            "# Context Structure Research - Analysis Report",
            "",
            f"Generated from {stats['overall']['total_tests']} test runs.",
            "",
            "## Overall Performance",
            "",
            f"- **Average Score**: {stats['overall']['average_score']:.2%}",
            f"- **Exact Matches**: {stats['overall']['exact_matches']}",
            f"- **Variant Matches**: {stats['overall']['variant_matches']}",
            "",
            "## Performance by Structure",
            "",
            "| Structure | Average Score |",
            "|-----------|---------------|",
        ]

        for struct, score in stats["by_structure"].items():
            lines.append(f"| {struct} | {score:.2%} |")

        lines.extend([
            "",
            "## Performance by Model",
            "",
            "| Model | Average Score |",
            "|-------|---------------|",
        ])

        for model, score in stats["by_model"].items():
            lines.append(f"| {model} | {score:.2%} |")

        lines.extend([
            "",
            "## Loading Method Comparison",
            "",
            f"- **Classic wins**: {loading_cmp['summary']['classic_wins']}",
            f"- **Add-dir wins**: {loading_cmp['summary']['adddir_wins']}",
            f"- **Ties**: {loading_cmp['summary']['ties']}",
            "",
            "## Performance by Question Type",
            "",
            "| Type | Average Score |",
            "|------|---------------|",
        ])

        for qtype, score in stats["by_question_type"].items():
            lines.append(f"| {qtype} | {score:.2%} |")

        lines.extend([
            "",
            "## Detailed Comparisons",
            "",
            "### Classic vs Add-dir by Structure",
            "",
        ])

        # Aggregate by structure
        struct_comparison = defaultdict(lambda: {"classic": [], "adddir": []})
        for cmp in loading_cmp["comparisons"]:
            struct_comparison[cmp["structure"]]["classic"].append(cmp["classic_score"])
            struct_comparison[cmp["structure"]]["adddir"].append(cmp["adddir_score"])

        lines.extend([
            "| Structure | Classic | Add-dir | Difference |",
            "|-----------|---------|---------|------------|",
        ])

        for struct, scores in sorted(struct_comparison.items()):
            c_avg = sum(scores["classic"]) / len(scores["classic"]) if scores["classic"] else 0
            a_avg = sum(scores["adddir"]) / len(scores["adddir"]) if scores["adddir"] else 0
            diff = a_avg - c_avg
            diff_str = f"+{diff:.2%}" if diff > 0 else f"{diff:.2%}"
            lines.append(f"| {struct} | {c_avg:.2%} | {a_avg:.2%} | {diff_str} |")

        return "\n".join(lines)

    def export_json(self) -> dict:
        """Export full results as JSON."""
        return {
            "summary": self.summary_stats(),
            "loading_comparison": self.loading_comparison(),
            "scores": [
                {
                    "question_id": s.question_id,
                    "config": s.config,
                    "points": s.points,
                    "exact_match": s.exact_match,
                    "variant_match": s.variant_match,
                    "keyword_matches": s.keyword_matches,
                    "confidence": s.confidence,
                    "sources_cited": s.sources_cited,
                    "reasoning": s.reasoning,
                }
                for s in self.scores
            ],
        }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Claude responses for context structure research"
    )
    parser.add_argument(
        "results_dir",
        type=Path,
        help="Directory containing result JSON files",
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed scoring for each response",
    )

    args = parser.parse_args()

    if not args.results_dir.exists():
        print(f"Error: Results directory not found: {args.results_dir}", file=sys.stderr)
        sys.exit(1)

    if not args.questions.exists():
        print(f"Error: Questions file not found: {args.questions}", file=sys.stderr)
        sys.exit(1)

    # Load and evaluate
    evaluator = Evaluator(args.questions)
    scores = evaluator.evaluate_directory(args.results_dir)

    if not scores:
        print("No results found to evaluate.", file=sys.stderr)
        sys.exit(1)

    print(f"Evaluated {len(scores)} results.")

    if args.verbose:
        print("\nDetailed Scores:")
        for score in scores:
            print(f"  {score.question_id}: {score.points:.2f} - {score.reasoning}")

    # Generate reports
    reporter = Reporter(scores, evaluator.questions)

    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)

        if args.format in ("markdown", "both"):
            md_path = args.output / "report.md"
            md_path.write_text(reporter.generate_markdown_report())
            print(f"Markdown report: {md_path}")

        if args.format in ("json", "both"):
            json_path = args.output / "results.json"
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
