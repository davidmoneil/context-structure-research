#!/usr/bin/env python3
"""Consolidate all test results into a single dataset."""

import json
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_DIR = RESULTS_DIR / "consolidated"

# Corpus metadata
CORPUS_INFO = {
    "v4": {"words": 120000, "files": 80},
    "v5": {"words": 302000, "files": 121},
    "v6": {"words": 622561, "files": 277},
}

# Structure to nesting depth mapping
NESTING_DEPTH = {
    "flat": 0,
    "shallow": 1,
    "deep": 3,
    "very-deep": 5,
    "monolith": 0,  # Single file, no nesting
}

def get_nesting_depth(structure):
    """Extract nesting depth from structure name."""
    for key, depth in NESTING_DEPTH.items():
        if key in structure.lower():
            return depth
    return -1  # Unknown

def get_corpus_version(structure):
    """Extract corpus version from structure name."""
    if "-v6" in structure:
        return "v6"
    elif "-v5" in structure or structure in ["flat", "shallow", "deep", "very-deep", "monolith"]:
        return "v5"  # Default for base structures
    return "unknown"

def has_enhancement(structure):
    """Check if structure has enhancement (v5.1-v5.5)."""
    for v in ["v5.1", "v5.2", "v5.3", "v5.4", "v5.5"]:
        if v in structure:
            return v
    return None

def parse_result_file(filepath, suite_name):
    """Parse a single result JSON file."""
    with open(filepath) as f:
        data = json.load(f)

    # Extract info from filename: structure_method_100_question.json
    filename = filepath.stem
    parts = filename.rsplit("_", 3)

    if len(parts) >= 4:
        structure = parts[0]
        method = parts[1]
        question_id = parts[3]
    else:
        # Fallback parsing
        structure = data.get("structure", "unknown")
        method = data.get("loading_method", "unknown")
        question_id = data.get("question_id", "unknown")

    # Determine corpus from suite name
    if "v4" in suite_name:
        corpus = "v4"
    elif "v6" in suite_name:
        corpus = "v6"
    else:
        corpus = "v5"

    # Get question type from questions.json
    question_type = data.get("question_type", "unknown")

    return {
        "id": f"{suite_name}_{filename}",
        "suite": suite_name,
        "corpus": corpus,
        "corpus_words": CORPUS_INFO.get(corpus, {}).get("words", 0),
        "corpus_files": CORPUS_INFO.get(corpus, {}).get("files", 0),
        "structure": structure,
        "nesting_depth": get_nesting_depth(structure),
        "enhancement": has_enhancement(structure),
        "loading_method": method,
        "question_id": question_id,
        "question_type": question_type,
        "score": data.get("score", 0),
        "correct": data.get("score", 0) >= 100,
        "partial": 0 < data.get("score", 0) < 100,
        "input_tokens": data.get("input_tokens", 0),
        "output_tokens": data.get("output_tokens", 0),
    }

def find_result_files(base_dir):
    """Find all result JSON files in a directory."""
    results = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".json") and not f.startswith("."):
                results.append(Path(root) / f)
    return results

def main():
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Define test suites to consolidate
    suites = [
        ("v4", RESULTS_DIR / "v4" / "raw" / "haiku"),
        ("v5", RESULTS_DIR / "v5" / "raw" / "haiku"),
        ("v5-enhancements", RESULTS_DIR / "v5-enhancements" / "raw" / "haiku"),
        ("v5.5-matrix", RESULTS_DIR / "v5.5-matrix" / "raw" / "haiku"),
        ("v6-matrix", RESULTS_DIR / "v6-matrix" / "raw" / "haiku"),
        ("v6-extended", RESULTS_DIR / "v6-extended" / "raw" / "haiku" / "haiku"),  # Note: nested haiku
    ]

    all_results = []
    suite_counts = {}

    for suite_name, suite_dir in suites:
        if not suite_dir.exists():
            print(f"Warning: Suite directory not found: {suite_dir}")
            continue

        files = find_result_files(suite_dir)
        suite_counts[suite_name] = len(files)

        for filepath in files:
            try:
                result = parse_result_file(filepath, suite_name)
                all_results.append(result)
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")

    # Load questions.json for type info
    questions_file = PROJECT_ROOT / "harness" / "questions.json"
    if questions_file.exists():
        with open(questions_file) as f:
            questions = {q["id"]: q for q in json.load(f)}

        # Enrich results with question info
        for result in all_results:
            q = questions.get(result["question_id"], {})
            result["question_type"] = q.get("type", result["question_type"])
            result["question_difficulty"] = q.get("difficulty", "unknown")

    # Build consolidated output
    output = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "suites": suite_counts,
            "corpora": list(CORPUS_INFO.keys()),
        },
        "results": all_results,
    }

    # Write JSON
    json_path = OUTPUT_DIR / "all-results.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"JSON output: {json_path} ({len(all_results)} results)")

    # Write CSV
    csv_path = OUTPUT_DIR / "all-results.csv"
    if all_results:
        headers = list(all_results[0].keys())
        with open(csv_path, "w") as f:
            f.write(",".join(headers) + "\n")
            for r in all_results:
                row = [str(r.get(h, "")).replace(",", ";") for h in headers]
                f.write(",".join(row) + "\n")
        print(f"CSV output: {csv_path}")

    # Print summary
    print("\n=== Consolidation Summary ===")
    for suite, count in suite_counts.items():
        print(f"  {suite}: {count} tests")
    print(f"  TOTAL: {len(all_results)} tests")

    # Quick stats
    correct = sum(1 for r in all_results if r["correct"])
    print(f"\n=== Quick Stats ===")
    print(f"  Overall accuracy: {correct}/{len(all_results)} ({100*correct/len(all_results):.1f}%)")

if __name__ == "__main__":
    main()
