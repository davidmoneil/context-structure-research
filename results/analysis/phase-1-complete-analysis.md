# Phase 1 Complete Analysis

**Generated**: 2026-01-30
**Total Tests**: 849

---

## Executive Summary

Testing 849 configurations across corpora from 120K to 622K words revealed:

1. **Flat structure wins** - 100% accuracy at 120K-302K, 97.35% at 622K
2. **Enhancements hurt at scale** - V5.5 indexes reduce accuracy by ~4.6% at 622K words
3. **Nesting degrades gracefully** - ~3-5% accuracy loss per additional depth level
4. **Loading method doesn't matter** - Classic vs adddir shows no meaningful difference

---

## Test Data Summary

| Suite | Tests | Corpus | Structures |
|-------|-------|--------|------------|
| V4 Matrix | 230 | 120K words | flat, shallow, deep, very-deep, monolith |
| V5 Matrix | 191 | 302K words | flat, shallow, deep, very-deep, monolith |
| V5 Enhancements | 60 | 302K words | V5.1-V5.5 targeted tests |
| V5.5 Full Matrix | 92 | 302K words | flat-v5.5, deep-v5.5 |
| V6 Matrix | 184 | 622K words | flat-v6, deep-v6, +v5.5 variants |
| V6 Extended | 92 | 622K words | shallow-v6, very-deep-v6 |

---

## Structure Performance by Corpus Size

### V4 (120K words) - 230 tests

| Structure | Accuracy |
|-----------|----------|
| **flat** | **100.00%** |
| **shallow** | **100.00%** |
| **monolith** | **100.00%** |
| deep | 96.78% |
| very-deep | 95.65% |

**Overall V4 Accuracy**: 98.49%

### V5 (302K words) - 191 tests

| Structure | Accuracy |
|-----------|----------|
| **flat** | **100.00%** |
| **shallow** | **100.00%** |
| **monolith** | **100.00%** |
| very-deep | 96.04% |
| deep | 92.04% |

**Overall V5 Accuracy**: 97.13%

### V6 (622K words) - 276 tests

| Structure | Accuracy |
|-----------|----------|
| **flat-v6** | **97.35%** |
| very-deep-v6 | 96.04% |
| deep-v6 | 95.00% |
| shallow-v6 | 94.42% |
| flat-v6-v5.5 | 92.74% |
| deep-v6-v5.5 | 92.30% |

**Overall V6 Accuracy**: ~95%

---

## Nesting Depth Analysis

**Research Question**: Is there too much nesting? What's the optimal depth?

### By Nesting Depth

| Depth | Description | V4 (120K) | V5 (302K) | V6 (622K) |
|-------|-------------|-----------|-----------|-----------|
| 0 | Flat | **100%** | **100%** | **97.35%** |
| 0 | Monolith | **100%** | **100%** | N/A |
| 1 | Shallow | **100%** | **100%** | 94.42% |
| 3 | Deep | 96.78% | 92.04% | 95.00% |
| 5 | Very-Deep | 95.65% | 96.04% | 96.04% |

### Key Finding: Optimal Depth

**Depth 0 (Flat) is optimal across all scales.**

However, nesting doesn't severely degrade performance:
- Depth 0 → Depth 3: ~3-5% accuracy loss
- Very-deep (5) sometimes outperforms deep (3) - inconsistent

**Recommendation**: Prefer flat, but nested is acceptable if organizational needs require it. Avoid more than 3 levels.

---

## Scale Effects

### Accuracy Degradation by Corpus Size

| Corpus | Best Structure | Accuracy | Degradation |
|--------|---------------|----------|-------------|
| 120K (V4) | flat/shallow/monolith | 100% | - |
| 302K (V5) | flat/shallow/monolith | 100% | 0% |
| 622K (V6) | flat-v6 | 97.35% | -2.65% |

### Key Finding: Scale Impact

- **No degradation** from 120K → 302K (2.5x scale)
- **Minimal degradation** from 302K → 622K (-2.65%, 2x scale)
- **First meaningful degradation** appears around 600K words

**Recommendation**: Structure matters more than scale. Well-organized content stays accurate even at 622K words.

---

## Enhancement Strategy Analysis

### Recovery Rate on Failed Questions (V5 Targeted Tests)

| Enhancement | Description | Recovery Rate |
|-------------|-------------|---------------|
| V5.3 | 10 keywords | **80%** (4/5) |
| V5.4 | 5-sentence + keywords | **80%** (4/5) |
| V5.5 | 2-sentence + keywords | **80%** (4/5) |
| V5.1 | 2-sentence summary | 60% (3/5) |
| V5.2 | 5-sentence summary | 40% (2/5) |

### Enhancement Impact at Scale

| Variant | V5 (302K) | V6 (622K) | Delta |
|---------|-----------|-----------|-------|
| Base flat | 100% | 97.35% | -2.65% |
| Flat + V5.5 | 100% | 92.74% | **-7.26%** |
| Base deep | 92.04% | 95.00% | +2.96% |
| Deep + V5.5 | 89.83% | 92.30% | +2.47% |

### Key Finding: Enhancements Hurt at Scale

- **Keywords alone = best ROI** (V5.3: minimal overhead, 80% recovery)
- **Summaries add no value** when keywords present
- **Combined enhancements hurt at 622K** (4.6% accuracy reduction)
- **Index content becomes noise** competing for context window

**Recommendation**: Skip enhancement indexes for projects >300K words. Use flat structure with descriptive filenames instead.

---

## Question Type Analysis

### Performance by Question Type

| Type | V4 (120K) | V5 (302K) | V6 (622K) | Trend |
|------|-----------|-----------|-----------|-------|
| Navigation | 99% | 100% | 97.5% | Most robust |
| Cross-reference | 97.78% | 93.44% | 93.38% | Moderate degradation |
| Depth | 98.6% | 96.8% | 89.59% | Steepest degradation |

### Key Finding: Question Type Matters

- **Navigation** (single-file lookup): Most resilient, nearly perfect at all scales
- **Cross-reference** (multi-file): Consistent ~93% at scale
- **Depth** (specific detail extraction): Degrades most with scale

**Recommendation**: For complex cross-reference or depth queries, consider splitting content or using targeted index files.

---

## Loading Method Analysis

### Classic vs Add-dir (--add-dir flag)

| Metric | Result |
|--------|--------|
| Classic wins | 15 |
| Add-dir wins | 14 |
| Ties | 294 |

### By Structure (V5.5)

| Structure | Classic | Add-dir | Difference |
|-----------|---------|---------|------------|
| flat-v5.5 | 100% | 100% | 0% |
| deep-v5.5 | 87.47% | 92.19% | +4.72% |

### Key Finding: Loading Method Doesn't Matter

Loading method has **no meaningful impact** overall. Slight advantage to add-dir in deep structures (+4.72% in V5.5 deep).

**Recommendation**: Use whichever fits your workflow.

---

## Unsolved Questions

### XREF-006: "What is the relationship between Project Hermes and Project Prometheus?"

- **Fails across ALL enhancement strategies** on deep structures
- **Succeeds on flat structures**
- Requires connecting information across 2+ files
- Suggests inherent limitation of nested structures for complex cross-references

---

## Practical Recommendations

### By Project Size

| Size | Recommendation |
|------|----------------|
| <100K words | Any structure works; monolith acceptable |
| 100-300K words | Flat structure recommended; keyword index optional |
| 300-600K words | Flat structure required; skip enhancement indexes |
| 600K+ words | Flat structure; consider splitting into sub-corpora |

### Structure Guidelines

1. **One topic per file** - Claude assesses relevance from filenames
2. **Prefer flat over nested** - Every level costs ~1-2% accuracy
3. **Use descriptive filenames** - Include key entities in name
4. **Keep CLAUDE.md minimal** - Brief overview only
5. **Skip enhancement indexes at scale** - They hurt more than help

### What Didn't Work

- Long summaries (5-sentence) performed worse than short (2-sentence)
- Combined enhancements often worse than single enhancement
- Very deep nesting (5+ levels) showed inconsistent results
- Monolith fails on Haiku with large corpora (context limit)

---

## Research Questions Answered

| # | Question | Answer |
|---|----------|--------|
| 1 | Does flat outperform nested? | **Yes** - flat wins at all scales |
| 2 | Is there too much nesting? | **Depth 0-1 optimal** - 3+ levels lose 3-5% |
| 3 | At what scale does accuracy degrade? | **~600K words** - first meaningful drop |
| 4 | Do summaries/keywords help? | **Keywords only** - summaries add no value |
| 5 | Which question types are hardest? | **Depth queries** - degrade most at scale |
| 6 | Does loading method matter? | **No** - trivial difference |
| 7 | What causes failures? | **Multi-file cross-references** in nested structures |

---

## Appendix: Raw Scores by Structure

### All Structures Ranked

| Rank | Structure | Corpus | Accuracy |
|------|-----------|--------|----------|
| 1 | flat | V4 | 100.00% |
| 1 | shallow | V4 | 100.00% |
| 1 | monolith | V4 | 100.00% |
| 1 | flat | V5 | 100.00% |
| 1 | shallow | V5 | 100.00% |
| 1 | monolith | V5 | 100.00% |
| 7 | flat-v6 | V6 | 97.35% |
| 8 | deep | V4 | 96.78% |
| 9 | very-deep-v6 | V6 | 96.04% |
| 10 | very-deep | V5 | 96.04% |
| 11 | very-deep | V4 | 95.65% |
| 12 | deep-v6 | V6 | 95.00% |
| 13 | shallow-v6 | V6 | 94.42% |
| 14 | flat-v6-v5.5 | V6 | 92.74% |
| 15 | deep-v6-v5.5 | V6 | 92.30% |
| 16 | deep | V5 | 92.04% |

---

*Analysis complete. 849 tests across 6 test suites.*
