#!/usr/bin/env python3
"""
Comprehensive Phase 1 Analysis

Consolidates all results, evaluates, and generates analysis reports.
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_DIR = RESULTS_DIR / "analysis"
QUESTIONS_FILE = PROJECT_ROOT / "harness" / "questions.json"

# Corpus metadata
CORPUS_INFO = {
    "v4": {"words": 120000, "files": 80},
    "v5": {"words": 302000, "files": 121},
    "v6": {"words": 622561, "files": 277},
}

NESTING_DEPTH = {
    "flat": 0,
    "monolith": 0,
    "shallow": 1,
    "deep": 3,
    "very-deep": 5,
}

def load_questions():
    """Load ground truth questions."""
    with open(QUESTIONS_FILE) as f:
        return {q["id"]: q for q in json.load(f)}

def normalize(text):
    """Normalize text for comparison."""
    return re.sub(r'\s+', ' ', str(text).lower().strip())

def extract_answer(response_text):
    """Extract answer from Claude's response."""
    if not response_text:
        return ""

    # Try to find JSON answer field
    try:
        # Parse the outer response JSON
        if isinstance(response_text, str):
            # Look for answer in the result field
            answer_match = re.search(r'"answer"\s*:\s*"([^"]*)"', response_text)
            if answer_match:
                return answer_match.group(1)

            # Look for result field and extract from there
            result_match = re.search(r'"result"\s*:\s*"(.*?)"(?=\s*,\s*"session_id")', response_text, re.DOTALL)
            if result_match:
                result_text = result_match.group(1)
                # Unescape the JSON string
                result_text = result_text.replace('\\"', '"').replace('\\n', '\n')
                # Try to find answer in unescaped text
                answer_match = re.search(r'"answer"\s*:\s*"([^"]*)"', result_text)
                if answer_match:
                    return answer_match.group(1)
    except Exception:
        pass

    return response_text[:500] if response_text else ""

def score_result(result, questions):
    """Score a single result against ground truth."""
    question_id = result.get("question_id", "")
    if question_id not in questions:
        return 0, False, False

    q = questions[question_id]
    gt = q.get("ground_truth", {})
    exact_answer = gt.get("exact_answer", "")
    variants = gt.get("acceptable_variants", [])
    keywords = gt.get("partial_credit_keywords", [])

    # Extract answer from response
    response = result.get("response", "")
    answer = extract_answer(response)
    answer_norm = normalize(answer)

    # Check exact match
    if normalize(exact_answer) in answer_norm:
        return 100, True, False

    # Check variants
    for variant in variants:
        if normalize(variant) in answer_norm:
            return 100, False, True

    # Check partial credit keywords
    if keywords:
        matches = sum(1 for kw in keywords if normalize(kw) in answer_norm)
        if matches >= len(keywords) * 0.5:
            return 50 + (50 * matches / len(keywords)), False, False

    return 0, False, False

def get_structure_info(structure):
    """Extract structure metadata."""
    # Get base structure (without version suffixes)
    base = structure.lower()

    # Determine nesting depth
    depth = -1
    for key, d in NESTING_DEPTH.items():
        if key in base:
            depth = d
            break

    # Check for enhancement
    enhancement = None
    for v in ["v5.5", "v5.4", "v5.3", "v5.2", "v5.1"]:
        if v in structure:
            enhancement = v
            break

    return depth, enhancement

def process_results():
    """Process all result files."""
    questions = load_questions()

    # Define test suites
    suites = [
        ("v4", RESULTS_DIR / "v4" / "raw" / "haiku", "v4"),
        ("v5", RESULTS_DIR / "v5" / "raw" / "haiku", "v5"),
        ("v5-enhancements", RESULTS_DIR / "v5-enhancements" / "raw" / "haiku", "v5"),
        ("v5.5-matrix", RESULTS_DIR / "v5.5-matrix" / "raw" / "haiku", "v5"),
        ("v6-matrix", RESULTS_DIR / "v6-matrix" / "raw" / "haiku", "v6"),
        ("v6-extended", RESULTS_DIR / "v6-extended" / "raw" / "haiku" / "haiku", "v6"),
    ]

    all_results = []

    for suite_name, suite_dir, corpus in suites:
        if not suite_dir.exists():
            print(f"Warning: {suite_dir} not found")
            continue

        for filepath in suite_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)

                # Parse filename: structure_method_100_question.json
                parts = filepath.stem.rsplit("_", 3)
                structure = parts[0] if len(parts) >= 4 else data.get("config", {}).get("structure", "unknown")
                method = parts[1] if len(parts) >= 4 else data.get("config", {}).get("loading_method", "unknown")
                question_id = parts[3] if len(parts) >= 4 else data.get("question_id", "unknown")

                # Score the result
                score, exact, variant = score_result(data, questions)

                # Get structure info
                depth, enhancement = get_structure_info(structure)

                # Get question type
                q_type = questions.get(question_id, {}).get("type", "unknown")

                all_results.append({
                    "suite": suite_name,
                    "corpus": corpus,
                    "corpus_words": CORPUS_INFO.get(corpus, {}).get("words", 0),
                    "structure": structure,
                    "nesting_depth": depth,
                    "enhancement": enhancement,
                    "loading_method": method,
                    "question_id": question_id,
                    "question_type": q_type,
                    "score": score,
                    "exact_match": exact,
                    "variant_match": variant,
                })
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

    return all_results

def analyze_structure(results):
    """Analyze performance by structure."""
    by_structure = defaultdict(lambda: {"scores": [], "count": 0})

    for r in results:
        key = r["structure"]
        by_structure[key]["scores"].append(r["score"])
        by_structure[key]["count"] += 1
        by_structure[key]["corpus"] = r["corpus"]
        by_structure[key]["depth"] = r["nesting_depth"]

    analysis = []
    for structure, data in sorted(by_structure.items()):
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        analysis.append({
            "structure": structure,
            "corpus": data["corpus"],
            "depth": data["depth"],
            "count": data["count"],
            "avg_score": round(avg, 2),
            "perfect": sum(1 for s in data["scores"] if s >= 100),
        })

    return sorted(analysis, key=lambda x: (-CORPUS_INFO.get(x["corpus"], {}).get("words", 0), -x["avg_score"]))

def analyze_scale(results):
    """Analyze performance by corpus size."""
    by_corpus = defaultdict(lambda: {"scores": [], "structures": set()})

    for r in results:
        corpus = r["corpus"]
        by_corpus[corpus]["scores"].append(r["score"])
        by_corpus[corpus]["structures"].add(r["structure"])

    analysis = []
    for corpus in ["v4", "v5", "v6"]:
        if corpus not in by_corpus:
            continue
        data = by_corpus[corpus]
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        analysis.append({
            "corpus": corpus,
            "words": CORPUS_INFO[corpus]["words"],
            "tests": len(data["scores"]),
            "structures": len(data["structures"]),
            "avg_score": round(avg, 2),
            "perfect_rate": round(100 * sum(1 for s in data["scores"] if s >= 100) / len(data["scores"]), 1),
        })

    return analysis

def analyze_nesting(results):
    """Analyze performance by nesting depth."""
    by_depth = defaultdict(lambda: {"scores": [], "by_corpus": defaultdict(list)})

    for r in results:
        depth = r["nesting_depth"]
        if depth < 0:
            continue
        by_depth[depth]["scores"].append(r["score"])
        by_depth[depth]["by_corpus"][r["corpus"]].append(r["score"])

    analysis = []
    for depth in sorted(by_depth.keys()):
        data = by_depth[depth]
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0

        # Per-corpus breakdown
        corpus_avgs = {}
        for corpus, scores in data["by_corpus"].items():
            corpus_avgs[corpus] = round(sum(scores) / len(scores), 2) if scores else 0

        analysis.append({
            "depth": depth,
            "tests": len(data["scores"]),
            "avg_score": round(avg, 2),
            "v4_avg": corpus_avgs.get("v4", "n/a"),
            "v5_avg": corpus_avgs.get("v5", "n/a"),
            "v6_avg": corpus_avgs.get("v6", "n/a"),
        })

    return analysis

def analyze_question_types(results):
    """Analyze performance by question type."""
    by_type = defaultdict(lambda: {"scores": [], "by_corpus": defaultdict(list)})

    for r in results:
        q_type = r["question_type"]
        by_type[q_type]["scores"].append(r["score"])
        by_type[q_type]["by_corpus"][r["corpus"]].append(r["score"])

    analysis = []
    for q_type, data in sorted(by_type.items()):
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0

        corpus_avgs = {}
        for corpus, scores in data["by_corpus"].items():
            corpus_avgs[corpus] = round(sum(scores) / len(scores), 2) if scores else 0

        analysis.append({
            "type": q_type,
            "tests": len(data["scores"]),
            "avg_score": round(avg, 2),
            "v4_avg": corpus_avgs.get("v4", "n/a"),
            "v5_avg": corpus_avgs.get("v5", "n/a"),
            "v6_avg": corpus_avgs.get("v6", "n/a"),
        })

    return analysis

def analyze_enhancements(results):
    """Analyze enhancement strategy performance."""
    # Filter to enhanced structures only
    enhanced = [r for r in results if r["enhancement"]]
    baseline = [r for r in results if not r["enhancement"] and "deep" in r["structure"].lower()]

    by_enhancement = defaultdict(lambda: {"scores": [], "by_corpus": defaultdict(list)})

    # Add baseline
    for r in baseline:
        by_enhancement["baseline"]["scores"].append(r["score"])
        by_enhancement["baseline"]["by_corpus"][r["corpus"]].append(r["score"])

    for r in enhanced:
        enh = r["enhancement"]
        by_enhancement[enh]["scores"].append(r["score"])
        by_enhancement[enh]["by_corpus"][r["corpus"]].append(r["score"])

    analysis = []
    for enh, data in sorted(by_enhancement.items()):
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0

        corpus_avgs = {}
        for corpus, scores in data["by_corpus"].items():
            corpus_avgs[corpus] = round(sum(scores) / len(scores), 2) if scores else 0

        analysis.append({
            "enhancement": enh,
            "tests": len(data["scores"]),
            "avg_score": round(avg, 2),
            "v5_avg": corpus_avgs.get("v5", "n/a"),
            "v6_avg": corpus_avgs.get("v6", "n/a"),
        })

    return analysis

def analyze_loading_methods(results):
    """Analyze classic vs adddir loading."""
    by_method = defaultdict(lambda: {"scores": [], "by_structure": defaultdict(list)})

    for r in results:
        method = r["loading_method"]
        by_method[method]["scores"].append(r["score"])
        by_method[method]["by_structure"][r["structure"]].append(r["score"])

    # Compare wins/losses
    pairs = defaultdict(lambda: {"classic": [], "adddir": []})
    for r in results:
        key = (r["structure"], r["question_id"])
        pairs[key][r["loading_method"]].append(r["score"])

    classic_wins = adddir_wins = ties = 0
    for key, scores in pairs.items():
        c = scores["classic"][0] if scores["classic"] else 0
        a = scores["adddir"][0] if scores["adddir"] else 0
        if c > a:
            classic_wins += 1
        elif a > c:
            adddir_wins += 1
        else:
            ties += 1

    analysis = {
        "classic_wins": classic_wins,
        "adddir_wins": adddir_wins,
        "ties": ties,
        "methods": {}
    }

    for method, data in by_method.items():
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        analysis["methods"][method] = {
            "tests": len(data["scores"]),
            "avg_score": round(avg, 2),
        }

    return analysis

def generate_report(results, structure_analysis, scale_analysis, nesting_analysis,
                   question_analysis, enhancement_analysis, loading_analysis):
    """Generate comprehensive markdown report."""

    report = []
    report.append("# Phase 1 Complete Analysis")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Total Tests**: {len(results)}")
    report.append("")

    # Overall stats
    avg_score = sum(r["score"] for r in results) / len(results) if results else 0
    perfect = sum(1 for r in results if r["score"] >= 100)
    report.append("## Overall Performance")
    report.append(f"\n- **Average Score**: {avg_score:.1f}%")
    report.append(f"- **Perfect Scores**: {perfect}/{len(results)} ({100*perfect/len(results):.1f}%)")
    report.append("")

    # Structure comparison
    report.append("## Structure Performance")
    report.append("\n| Structure | Corpus | Depth | Tests | Avg Score | Perfect |")
    report.append("|-----------|--------|-------|-------|-----------|---------|")
    for s in structure_analysis:
        report.append(f"| {s['structure']} | {s['corpus']} | {s['depth']} | {s['count']} | {s['avg_score']}% | {s['perfect']} |")
    report.append("")

    # Scale analysis
    report.append("## Scale Effects")
    report.append("\n| Corpus | Words | Tests | Avg Score | Perfect Rate |")
    report.append("|--------|-------|-------|-----------|--------------|")
    for s in scale_analysis:
        report.append(f"| {s['corpus']} | {s['words']:,} | {s['tests']} | {s['avg_score']}% | {s['perfect_rate']}% |")
    report.append("")

    # Nesting depth analysis
    report.append("## Nesting Depth Analysis")
    report.append("\n**Research Question**: Is there too much nesting?")
    report.append("\n| Depth | Tests | Avg Score | V4 | V5 | V6 |")
    report.append("|-------|-------|-----------|-----|-----|-----|")
    for n in nesting_analysis:
        report.append(f"| {n['depth']} | {n['tests']} | {n['avg_score']}% | {n['v4_avg']} | {n['v5_avg']} | {n['v6_avg']} |")
    report.append("")

    # Question type analysis
    report.append("## Question Type Performance")
    report.append("\n| Type | Tests | Avg Score | V4 | V5 | V6 |")
    report.append("|------|-------|-----------|-----|-----|-----|")
    for q in question_analysis:
        report.append(f"| {q['type']} | {q['tests']} | {q['avg_score']}% | {q['v4_avg']} | {q['v5_avg']} | {q['v6_avg']} |")
    report.append("")

    # Enhancement analysis
    report.append("## Enhancement Strategy Performance")
    report.append("\n| Enhancement | Tests | Avg Score | V5 | V6 |")
    report.append("|-------------|-------|-----------|-----|-----|")
    for e in enhancement_analysis:
        report.append(f"| {e['enhancement']} | {e['tests']} | {e['avg_score']}% | {e['v5_avg']} | {e['v6_avg']} |")
    report.append("")

    # Loading method analysis
    report.append("## Loading Method Comparison")
    report.append(f"\n- **Classic wins**: {loading_analysis['classic_wins']}")
    report.append(f"- **Adddir wins**: {loading_analysis['adddir_wins']}")
    report.append(f"- **Ties**: {loading_analysis['ties']}")
    for method, data in loading_analysis["methods"].items():
        report.append(f"- **{method}**: {data['avg_score']}% avg ({data['tests']} tests)")
    report.append("")

    # Key findings
    report.append("## Key Findings")
    report.append("")

    # Find best structure per corpus
    best_by_corpus = {}
    for s in structure_analysis:
        corpus = s["corpus"]
        if corpus not in best_by_corpus or s["avg_score"] > best_by_corpus[corpus]["avg_score"]:
            best_by_corpus[corpus] = s

    report.append("### Best Structure by Corpus Size")
    for corpus in ["v4", "v5", "v6"]:
        if corpus in best_by_corpus:
            s = best_by_corpus[corpus]
            words = CORPUS_INFO[corpus]["words"]
            report.append(f"- **{words:,} words ({corpus})**: {s['structure']} ({s['avg_score']}%)")
    report.append("")

    # Nesting depth recommendation
    report.append("### Optimal Nesting Depth")
    best_depth = max(nesting_analysis, key=lambda x: x["avg_score"])
    report.append(f"- **Best overall**: Depth {best_depth['depth']} ({best_depth['avg_score']}%)")
    report.append("")

    # Enhancement recommendation
    report.append("### Enhancement Strategy Recommendation")
    if enhancement_analysis:
        best_enh = max(enhancement_analysis, key=lambda x: x["avg_score"])
        report.append(f"- **Best enhancement**: {best_enh['enhancement']} ({best_enh['avg_score']}%)")
    report.append("")

    return "\n".join(report)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Processing all results...")
    results = process_results()
    print(f"Processed {len(results)} results")

    print("\nRunning analyses...")
    structure_analysis = analyze_structure(results)
    scale_analysis = analyze_scale(results)
    nesting_analysis = analyze_nesting(results)
    question_analysis = analyze_question_types(results)
    enhancement_analysis = analyze_enhancements(results)
    loading_analysis = analyze_loading_methods(results)

    print("\nGenerating report...")
    report = generate_report(
        results,
        structure_analysis,
        scale_analysis,
        nesting_analysis,
        question_analysis,
        enhancement_analysis,
        loading_analysis
    )

    # Write report
    report_path = OUTPUT_DIR / "phase-1-complete-analysis.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport written to: {report_path}")

    # Also write raw data
    data_path = OUTPUT_DIR / "phase-1-data.json"
    with open(data_path, "w") as f:
        json.dump({
            "results": results,
            "structure_analysis": structure_analysis,
            "scale_analysis": scale_analysis,
            "nesting_analysis": nesting_analysis,
            "question_analysis": question_analysis,
            "enhancement_analysis": enhancement_analysis,
            "loading_analysis": loading_analysis,
        }, f, indent=2)
    print(f"Data written to: {data_path}")

    # Print summary
    print("\n" + "="*60)
    print("PHASE 1 ANALYSIS COMPLETE")
    print("="*60)
    avg = sum(r["score"] for r in results) / len(results) if results else 0
    print(f"Total tests: {len(results)}")
    print(f"Overall accuracy: {avg:.1f}%")
    print(f"\nBest structures by corpus:")
    for s in sorted(structure_analysis, key=lambda x: -x["avg_score"])[:5]:
        print(f"  {s['structure']}: {s['avg_score']}%")

if __name__ == "__main__":
    main()
