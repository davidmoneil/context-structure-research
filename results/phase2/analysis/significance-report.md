# Phase 2: Statistical Significance Report

**Generated**: 2026-02-20 15:51
**Method**: Bootstrap CIs (10,000 resamples) + paired permutation tests (10,000 permutations)
**Seed**: 42 (reproducible)
**Significance level**: 0.05

## 1. Strategy Rankings with 95% Confidence Intervals

| Rank | Strategy | Accuracy | CI Lower | CI Upper | CI Width |
|------|----------|----------|----------|----------|----------|
| 1 | I4 | 73.2% | 65.9% | 80.2% | 14.4% |
| 2 | I4-grep2b | 72.9% | 66.6% | 79.2% | 12.6% |
| 3 | I4-grep | 72.8% | 65.4% | 79.7% | 14.4% |
| 4 | I4-template | 72.2% | 65.1% | 79.1% | 14.0% |
| 5 | I4-kw2 | 71.4% | 64.2% | 78.4% | 14.3% |
| 6 | I4-kw10 | 70.9% | 63.4% | 78.2% | 14.8% |
| 7 | I4-kw7 | 70.6% | 62.8% | 78.1% | 15.3% |
| 8 | I4-sonnet-verify | 70.5% | 63.5% | 77.5% | 14.0% |
| 9 | I1 | 70.1% | 62.1% | 77.8% | 15.7% |
| 10 | I3 | 70.0% | 62.4% | 77.3% | 14.9% |
| 11 | I4-grep2a | 69.9% | 62.0% | 77.5% | 15.5% |
| 12 | R1 | 68.8% | 61.3% | 76.0% | 14.7% |
| 13 | I4-sonnet | 68.6% | 60.4% | 76.6% | 16.1% |
| 14 | R3 | 68.4% | 60.5% | 75.9% | 15.4% |
| 15 | I4-geminiflash | 68.2% | 60.2% | 75.9% | 15.8% |
| 16 | C3 | 68.0% | 59.6% | 76.2% | 16.6% |
| 17 | I2 | 67.0% | 58.8% | 74.8% | 16.0% |
| 18 | I4-gpt4omini | 65.5% | 56.9% | 73.8% | 16.9% |
| 19 | I4-qwen7b | 65.4% | 56.6% | 73.8% | 17.2% |
| 20 | I4-qwen32b | 62.5% | 53.2% | 71.8% | 18.6% |
| 21 | R4 | 36.0% | 24.9% | 47.6% | 22.7% |
| 22 | C2 | 35.8% | 24.9% | 47.4% | 22.6% |

## 2. Statistical Tier Groupings

Strategies within a tier are **statistically indistinguishable** (overlapping 95% CIs
and pairwise permutation test p > 0.05 against tier leader).

**Tier 1** (68.2%–73.2%): I4, I4-grep2b, I4-grep, I4-template, I4-kw2, I4-kw10, I4-kw7, I4-sonnet-verify, I1, I3, I4-grep2a, R1, I4-sonnet, R3, I4-geminiflash

**Tier 2** (65.4%–68.0%): C3, I2, I4-gpt4omini, I4-qwen7b

**Tier 3** (62.5%–62.5%): I4-qwen32b

**Tier 4** (35.8%–36.0%): R4, C2

**Overflow Tier** (0.0%): C1, R2.1, R2.2, R2.3, R2.4
*(Excluded from pairwise tests — context window overflow caused 0% accuracy)*

## 3. Pairwise Significance Between Adjacent Ranks

| Rank | Strategy A | Strategy B | Delta | p-value | Significant? |
|------|------------|------------|-------|---------|--------------|
| 1→2 | I4 | I4-grep2b | 0.4% | 0.8425 | No |
| 2→3 | I4-grep2b | I4-grep | 0.1% | 0.9664 | No |
| 3→4 | I4-grep | I4-template | 0.6% | 0.7894 | No |
| 4→5 | I4-template | I4-kw2 | 0.9% | 0.5440 | No |
| 5→6 | I4-kw2 | I4-kw10 | 0.4% | 0.8165 | No |
| 6→7 | I4-kw10 | I4-kw7 | 0.4% | 0.8442 | No |
| 7→8 | I4-kw7 | I4-sonnet-verify | 0.1% | 0.9806 | No |
| 8→9 | I4-sonnet-verify | I1 | 0.4% | 0.8720 | No |
| 9→10 | I1 | I3 | 0.1% | 0.9834 | No |
| 10→11 | I3 | I4-grep2a | 0.1% | 0.9799 | No |
| 11→12 | I4-grep2a | R1 | 1.1% | 0.7787 | No |
| 12→13 | R1 | I4-sonnet | 0.2% | 0.9600 | No |
| 13→14 | I4-sonnet | R3 | 0.2% | 0.9614 | No |
| 14→15 | R3 | I4-geminiflash | 0.2% | 0.9160 | No |
| 15→16 | I4-geminiflash | C3 | 0.2% | 0.9552 | No |
| 16→17 | C3 | I2 | 1.0% | 0.7448 | No |
| 17→18 | I2 | I4-gpt4omini | 1.5% | 0.7295 | No |
| 18→19 | I4-gpt4omini | I4-qwen7b | 0.1% | 0.9810 | No |
| 19→20 | I4-qwen7b | I4-qwen32b | 2.9% | 0.3124 | No |
| 20→21 | I4-qwen32b | R4 | 26.5% | 0.0002 | Yes |
| 21→22 | R4 | C2 | 0.2% | 0.8789 | No |

**1/21** adjacent pairs show statistically significant differences.

## 4. Per-Dataset Confidence Intervals

### soong-v5

| Rank | Strategy | Accuracy | CI Lower | CI Upper |
|------|----------|----------|----------|----------|
| 1 | I3 | 78.3% | 68.9% | 87.1% |
| 2 | I4 | 77.1% | 65.9% | 87.1% |
| 3 | R4 | 76.6% | 67.0% | 85.8% |
| 4 | I4-kw2 | 76.3% | 64.8% | 86.7% |
| 5 | C2 | 76.3% | 67.2% | 85.0% |
| 6 | I4-template | 75.4% | 63.6% | 85.9% |
| 7 | R3 | 75.2% | 63.5% | 85.9% |
| 8 | C3 | 75.2% | 63.1% | 85.9% |
| 9 | I4-kw7 | 75.2% | 63.2% | 85.9% |
| 10 | R1 | 75.1% | 64.0% | 84.7% |
| 11 | I4-grep2b | 74.9% | 64.3% | 85.0% |
| 12 | I4-sonnet-verify | 74.7% | 63.6% | 84.8% |
| 13 | I2 | 74.0% | 62.6% | 84.3% |
| 14 | I4-kw10 | 73.8% | 60.6% | 85.3% |
| 15 | I4-geminiflash | 73.6% | 60.1% | 85.4% |
| 16 | I1 | 73.5% | 61.9% | 84.1% |
| 17 | I4-qwen7b | 73.1% | 61.3% | 83.8% |
| 18 | I4-sonnet | 72.0% | 58.1% | 84.2% |
| 19 | I4-qwen32b | 71.6% | 58.4% | 83.7% |
| 20 | I4-grep2a | 70.1% | 57.7% | 81.5% |
| 21 | I4-grep | 70.0% | 56.7% | 82.0% |
| 22 | I4-gpt4omini | 67.6% | 53.3% | 80.3% |

### obsidian

| Rank | Strategy | Accuracy | CI Lower | CI Upper |
|------|----------|----------|----------|----------|
| 1 | I4-grep | 75.2% | 68.3% | 82.2% |
| 2 | I4-grep2b | 71.1% | 63.6% | 78.7% |
| 3 | I4 | 69.8% | 60.3% | 79.1% |
| 4 | I4-grep2a | 69.7% | 59.4% | 79.3% |
| 5 | I4-template | 69.5% | 61.1% | 77.9% |
| 6 | I4-kw10 | 68.4% | 59.1% | 77.5% |
| 7 | I1 | 67.1% | 55.5% | 77.8% |
| 8 | I4-kw2 | 67.0% | 57.6% | 76.2% |
| 9 | I4-sonnet-verify | 66.8% | 57.9% | 75.8% |
| 10 | I4-kw7 | 66.5% | 55.9% | 76.4% |
| 11 | I4-sonnet | 65.6% | 55.6% | 75.3% |
| 12 | I4-gpt4omini | 63.7% | 52.4% | 74.4% |
| 13 | I4-geminiflash | 63.5% | 53.6% | 73.3% |
| 14 | R1 | 63.2% | 53.0% | 73.4% |
| 15 | I3 | 62.7% | 51.3% | 73.5% |
| 16 | R3 | 62.4% | 52.4% | 72.2% |
| 17 | C3 | 61.7% | 49.7% | 73.3% |
| 18 | I2 | 60.9% | 49.9% | 71.8% |
| 19 | I4-qwen7b | 58.7% | 45.9% | 70.7% |
| 20 | I4-qwen32b | 54.5% | 41.4% | 67.2% |
| 21 | C2 | 0.0% | 0.0% | 0.0% |
| 22 | R4 | 0.0% | 0.0% | 0.0% |

## 5. Methodology

- **Bootstrap confidence intervals**: 10,000 resamples with replacement, percentile method (2.5th–97.5th)
- **Paired permutation test**: 10,000 permutations, two-sided, paired by (dataset, question_id)
- **Sample size**: 49 paired observations per strategy
- **Random seed**: 42 (all results reproducible)
- **Tier formation**: Walk down rankings; a strategy joins the current tier if its CI overlaps the tier leader's CI AND their permutation test p > 0.05
- **Overflow strategies excluded**: C1, R2.1, R2.2, R2.3, R2.4 (0% accuracy due to context overflow)
- **Total strategies analyzed**: 22 working + 5 overflow
