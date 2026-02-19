# Phase 1 Complete Analysis

**Generated**: 2026-02-18 19:39
**Total Tests**: 849

## Overall Performance

- **Average Score**: 96.0%
- **Perfect Scores**: 784/849 (92.3%)

## Structure Performance

| Structure | Corpus | Depth | Tests | Avg Score | Perfect |
|-----------|--------|-------|-------|-----------|---------|
| flat-v6 | v6 | 0 | 46 | 97.35% | 43 |
| very-deep-v6 | v6 | 3 | 46 | 96.04% | 43 |
| deep-v6 | v6 | 3 | 46 | 95.0% | 41 |
| shallow-v6 | v6 | 1 | 46 | 94.42% | 42 |
| flat-v6-v5.5 | v6 | 0 | 46 | 92.74% | 39 |
| deep-v6-v5.5 | v6 | 3 | 46 | 92.3% | 41 |
| flat-v5 | v5 | 0 | 46 | 100.0% | 46 |
| flat-v5-v5.5 | v5 | 0 | 56 | 100.0% | 56 |
| monolith-v5 | v5 | 0 | 7 | 100.0% | 7 |
| shallow-v5 | v5 | 1 | 46 | 100.0% | 46 |
| deep-v5-v5.2 | v5 | 3 | 10 | 97.0% | 9 |
| very-deep-v5 | v5 | 3 | 46 | 96.04% | 43 |
| deep-v5-v5.3 | v5 | 3 | 10 | 96.0% | 9 |
| deep-v5 | v5 | 3 | 46 | 92.04% | 38 |
| deep-v5-v5.5 | v5 | 3 | 56 | 90.14% | 45 |
| deep-v5-v5.1 | v5 | 3 | 10 | 86.0% | 8 |
| deep-v5-v5.4 | v5 | 3 | 10 | 75.6% | 5 |
| flat | v4 | 0 | 46 | 100.0% | 46 |
| monolith | v4 | 0 | 46 | 100.0% | 46 |
| shallow | v4 | 1 | 46 | 100.0% | 46 |
| deep | v4 | 3 | 46 | 96.78% | 43 |
| very-deep | v4 | 3 | 46 | 95.65% | 42 |

## Scale Effects

| Corpus | Words | Tests | Avg Score | Perfect Rate |
|--------|-------|-------|-----------|--------------|
| v4 | 120,000 | 230 | 98.49% | 97.0% |
| v5 | 302,000 | 343 | 95.47% | 91.0% |
| v6 | 622,561 | 276 | 94.64% | 90.2% |

## Nesting Depth Analysis

**Research Question**: Is there too much nesting?

| Depth | Tests | Avg Score | V4 | V5 | V6 |
|-------|-------|-----------|-----|-----|-----|
| 0 | 293 | 98.44% | 100.0 | 100.0 | 95.04 |
| 1 | 138 | 98.14% | 100.0 | 100.0 | 94.42 |
| 3 | 418 | 93.62% | 96.22 | 91.73 | 94.45 |

## Question Type Performance

| Type | Tests | Avg Score | V4 | V5 | V6 |
|------|-------|-----------|-----|-----|-----|
| cross-reference | 308 | 94.01% | 97.78 | 91.85 | 93.85 |
| depth | 194 | 93.62% | 98.6 | 94.31 | 88.51 |
| navigation | 347 | 99.14% | 99.0 | 100.0 | 98.33 |

## Enhancement Strategy Performance

| Enhancement | Tests | Avg Score | V5 | V6 |
|-------------|-------|-----------|-----|-----|
| baseline | 276 | 95.26% | 94.04 | 95.52 |
| v5.1 | 10 | 86.0% | 86.0 | n/a |
| v5.2 | 10 | 97.0% | 97.0 | n/a |
| v5.3 | 10 | 96.0% | 96.0 | n/a |
| v5.4 | 10 | 75.6% | 75.6 | n/a |
| v5.5 | 204 | 93.92% | 95.07 | 92.52 |

## Loading Method Comparison

- **Classic wins**: 31
- **Adddir wins**: 26
- **Ties**: 361
- **adddir**: 96.35% avg (421 tests)
- **classic**: 95.69% avg (428 tests)

## Key Findings

### Best Structure by Corpus Size
- **120,000 words (v4)**: flat (100.0%)
- **302,000 words (v5)**: flat-v5 (100.0%)
- **622,561 words (v6)**: flat-v6 (97.35%)

### Optimal Nesting Depth
- **Best overall**: Depth 0 (98.44%)

### Enhancement Strategy Recommendation
- **Best enhancement**: v5.2 (97.0%)
