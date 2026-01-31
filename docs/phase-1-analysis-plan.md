# Phase 1 Analysis Plan

**Status**: Ready to Execute
**Created**: 2026-01-30

---

## Data Inventory

### Test Results Available

| Test Suite | Tests | Corpus | Structures Tested |
|------------|-------|--------|-------------------|
| V4 Haiku Matrix | 230 | 120K words | flat, shallow, deep, very-deep, monolith |
| V5 Haiku Matrix | 191 | 302K words | flat, shallow, deep, very-deep, monolith |
| V5 Enhancements | 60 | 302K words | V5.1-V5.5 (targeted questions) |
| V5.5 Full Matrix | 92 | 302K words | flat-v5.5, deep-v5.5 |
| V6 Matrix | 184 | 622K words | flat-v6, deep-v6, flat-v6-v5.5, deep-v6-v5.5 |
| V6 Extended | 92 | 622K words | shallow-v6, very-deep-v6 |

**Total**: 849 tests

### Results Locations

```
results/
├── v4/raw/haiku/           # 230 JSON files
├── v4/analysis/            # Existing analysis
├── v5/raw/haiku/           # 191 JSON files
├── v5/analysis/            # Existing analysis
├── v5-enhancements/raw/haiku/  # 60 JSON files
├── v5-enhancements/analysis/   # Existing analysis
├── v5.5-matrix/raw/haiku/      # 92 JSON files
├── v5.5-matrix/analysis/       # Existing analysis
├── v6-matrix/raw/haiku/        # 184 JSON files
├── v6-matrix/analysis/         # Existing analysis (flat, deep, +v5.5)
├── v6-extended/raw/haiku/haiku/  # 92 JSON files (shallow, very-deep)
└── v6-extended/analysis/         # NEW analysis
```

---

## Analysis Tasks

### 1. Data Consolidation

**Task**: Merge all results into unified dataset

**Deliverable**: `results/consolidated/all-results.json`

```json
{
  "metadata": {
    "total_tests": 849,
    "generated": "2026-01-30",
    "corpora": ["v4", "v5", "v6"]
  },
  "results": [
    {
      "id": "v4_flat_classic_NAV-001",
      "corpus": "v4",
      "corpus_words": 120000,
      "structure": "flat",
      "loading": "classic",
      "question_id": "NAV-001",
      "question_type": "navigation",
      "score": 100,
      "correct": true
    }
  ]
}
```

---

### 2. Structure Analysis

**Research Question**: How does file structure affect accuracy?

**Comparisons**:

| Comparison | Data Source |
|------------|-------------|
| Flat vs Deep vs Shallow vs Very-Deep | V4, V5, V6 |
| Monolith viability | V4, V5 only (V6 exceeds limits) |
| Nesting depth gradient | All structures across scales |

**Deliverable**: `results/analysis/structure-comparison.md`

**Visualizations**:
- Bar chart: Accuracy by structure (grouped by corpus size)
- Line chart: Accuracy vs nesting depth
- Heatmap: Structure × Corpus Size → Accuracy

---

### 3. Scale Analysis

**Research Question**: How does corpus size affect accuracy?

**Comparisons**:

| Metric | V4 (120K) | V5 (302K) | V6 (622K) |
|--------|-----------|-----------|-----------|
| Best structure accuracy | | | |
| Worst structure accuracy | | | |
| Average accuracy | | | |
| Degradation rate | - | V4→V5 | V5→V6 |

**Deliverable**: `results/analysis/scale-effects.md`

**Key Questions**:
- At what size does accuracy meaningfully degrade?
- Which structures are most resilient to scale?
- Is degradation linear or exponential?

---

### 4. Enhancement Strategy Analysis

**Research Question**: Do summaries/keywords improve accuracy?

**Data Sources**:
- V5 Enhancements (targeted: 5 questions × 6 variants × 2 methods)
- V5.5 Full Matrix (flat-v5.5, deep-v5.5 × 23 questions × 2 methods)
- V6 with V5.5 (flat-v6-v5.5, deep-v6-v5.5)

**Comparisons**:

| Enhancement | V5 (302K) | V6 (622K) | Delta |
|-------------|-----------|-----------|-------|
| None (baseline) | | | - |
| V5.1 (2-sentence) | | n/a | |
| V5.2 (5-sentence) | | n/a | |
| V5.3 (10 keywords) | | n/a | |
| V5.4 (5-sentence + keywords) | | n/a | |
| V5.5 (2-sentence + keywords) | | | |

**Deliverable**: `results/analysis/enhancement-comparison.md`

**Key Questions**:
- Do enhancements help at any scale?
- Which enhancement has best ROI?
- Why do enhancements hurt at 600K+?

---

### 5. Question Type Analysis

**Research Question**: Which question types are hardest?

**Question Types**:
- Navigation (10 questions): Single-file lookups
- Cross-reference (8 questions): Multi-file connections
- Depth (5 questions): Specific detail extraction

**Deliverable**: `results/analysis/question-type-breakdown.md`

**Comparisons**:
- Accuracy by type across all structures
- Which types degrade most with scale
- Which types benefit most from enhancements

---

### 6. Loading Method Analysis

**Research Question**: Does `--add-dir` vs `cd` matter?

**Data**: All test suites include both methods

**Deliverable**: `results/analysis/loading-method-comparison.md`

**Metrics**:
- Win/loss/tie counts
- Accuracy delta by structure
- Any structure-specific patterns

---

### 7. Failure Analysis

**Research Question**: What patterns cause failures?

**Approach**:
1. Identify all failed tests (score < 100)
2. Categorize by failure mode:
   - Wrong file referenced
   - Partial answer
   - Hallucination
   - Missing information
3. Cross-reference with structure/scale/question type

**Deliverable**: `results/analysis/failure-patterns.md`

**Special Focus**:
- XREF-006 (fails across all enhancements)
- Any question that fails only at V6 scale

---

### 8. Cost Analysis

**Research Question**: What's the token/cost efficiency?

**Metrics per test**:
- Input tokens
- Output tokens
- Total cost (Haiku pricing)

**Comparisons**:
- Cost by structure (does deep cost more?)
- Cost by corpus size
- Cost vs accuracy tradeoff

**Deliverable**: `results/analysis/cost-breakdown.md`

---

## Final Deliverables

### 1. Executive Summary (1 page)

`report/executive-summary.md`

- 3-5 key findings
- Primary recommendation
- When to deviate from recommendation

### 2. Full Technical Report

`report/README.md` (already exists, needs update)

- Methodology
- All findings with data
- Practical recommendations by use case
- Limitations

### 3. Cross-Variant Comparison

`results/cross-variant-comparison.md` (already exists, needs update with V6 extended)

- Side-by-side all structures
- All corpus sizes
- All enhancement strategies

### 4. Visualizations

`report/figures/`

- structure-accuracy-by-scale.png
- enhancement-comparison.png
- question-type-breakdown.png
- failure-heatmap.png

### 5. Raw Data Export

`results/consolidated/`

- all-results.json (machine-readable)
- all-results.csv (spreadsheet-ready)

---

## Execution Order

| Step | Task | Depends On | Output |
|------|------|------------|--------|
| 1 | Consolidate all results | Raw data | consolidated/all-results.json |
| 2 | Structure analysis | Step 1 | analysis/structure-comparison.md |
| 3 | Scale analysis | Step 1 | analysis/scale-effects.md |
| 4 | Enhancement analysis | Step 1 | analysis/enhancement-comparison.md |
| 5 | Question type analysis | Step 1 | analysis/question-type-breakdown.md |
| 6 | Loading method analysis | Step 1 | analysis/loading-method-comparison.md |
| 7 | Failure analysis | Step 1 | analysis/failure-patterns.md |
| 8 | Cost analysis | Step 1 | analysis/cost-breakdown.md |
| 9 | Update cross-variant comparison | Steps 2-8 | cross-variant-comparison.md |
| 10 | Update main report | Steps 2-9 | report/README.md |
| 11 | Write executive summary | Step 10 | report/executive-summary.md |
| 12 | Generate visualizations | Steps 2-8 | report/figures/*.png |

---

## Key Research Questions Summary

| # | Question | Analysis Task |
|---|----------|---------------|
| 1 | Does flat outperform nested? | Structure Analysis |
| 2 | Is there too much nesting? (optimal depth) | Structure Analysis |
| 3 | At what scale does accuracy degrade? | Scale Analysis |
| 4 | Do summaries/keywords help? | Enhancement Analysis |
| 5 | Which question types are hardest? | Question Type Analysis |
| 6 | Does loading method matter? | Loading Method Analysis |
| 7 | What causes failures? | Failure Analysis |
| 8 | What's the cost/accuracy tradeoff? | Cost Analysis |

---

## Architecture Principle (New Finding)

**One Topic = One File**

Document this as a core Phase 1 principle:
- Files should be topically cohesive
- Filenames act as implicit index
- Claude assesses relevance from directory listings
- This is why flat structure wins

---

## Timeline Estimate

| Task | Effort |
|------|--------|
| Data consolidation | 30 min |
| Structure analysis | 30 min |
| Scale analysis | 30 min |
| Enhancement analysis | 30 min |
| Question type analysis | 20 min |
| Loading method analysis | 15 min |
| Failure analysis | 45 min |
| Cost analysis | 30 min |
| Update reports | 45 min |
| Executive summary | 20 min |
| Visualizations | 30 min |

**Total**: ~5-6 hours

---

*Plan created: 2026-01-30*
