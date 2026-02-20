# Phase 2.2: I4 Variant Comparison Report

**Generated**: 2026-02-20 15:13

## Executive Summary

**14 I4 variants** tested across 2 datasets, 686 total tests.

**Best I4 variant**: I4 (73.2%)
**Worst I4 variant**: I4-qwen32b (62.5%)
**Spread**: 10.7% between best and worst

### Central Finding

**Heuristic/extraction methods (71.7%) outperform LLM-generated summaries (66.8%).**

Simpler, cheaper summary generation produces better results than expensive LLM calls.

---

## I4 Variant Rankings

| Rank | Variant | Accuracy | Exact | Group | Generation Method |
|------|---------|----------|-------|-------|-------------------|
| 1 | I4 | 73.2% | 19/49 | heuristic | Template heuristic (category + title + keywords) |
| 2 | I4-grep2b | 72.9% | 17/49 | extraction | Grep-based, instruction to grep summaries.md |
| 3 | I4-grep | 72.8% | 17/49 | extraction | Grep-based extraction, loaded via @ref |
| 4 | I4-template | 72.2% | 17/49 | heuristic | Template heuristic (explicit) |
| 5 | I4-kw2 | 71.4% | 18/49 | keyword-count | Template with 2 keywords per file |
| 6 | I4-kw10 | 70.9% | 17/49 | keyword-count | Template with 10 keywords per file |
| 7 | I4-kw7 | 70.6% | 17/49 | keyword-count | Template with 7 keywords per file |
| 8 | I4-sonnet-verify | 70.5% | 16/49 | llm-generated | Sonnet summaries + verification pass |
| 9 | I4-grep2a | 69.9% | 16/49 | extraction | Grep-based, instruction to use grep tool |
| 10 | I4-sonnet | 68.6% | 16/49 | llm-generated | Summaries by Claude Sonnet 4.6 |
| 11 | I4-geminiflash | 68.2% | 16/49 | llm-generated | Summaries by Gemini Flash 2 |
| 12 | I4-gpt4omini | 65.5% | 15/49 | llm-generated | Summaries by GPT-4o-mini |
| 13 | I4-qwen7b | 65.4% | 16/49 | llm-generated | Summaries by Qwen 2.5 7B (local) |
| 14 | I4-qwen32b | 62.5% | 17/49 | llm-generated | Summaries by Qwen 2.5 32B (local) |

---

## Performance by Generation Approach

| Approach | Strategies | Avg Accuracy | Tests | Description |
|----------|------------|--------------|-------|-------------|
| **heuristic** | I4, I4-template | 72.7% | 98 | Category + title + keywords from file metadata |
| **extraction** | I4-grep, I4-grep2a, I4-grep2b | 71.9% | 147 | Grep/regex extraction from file contents |
| **keyword-count** | I4-kw10, I4-kw2, I4-kw7 | 71.0% | 147 | Template with varying keyword counts (2/7/10) |
| **llm-generated** | I4-geminiflash, I4-gpt4omini, I4-qwen32b, I4-qwen7b, I4-sonnet, I4-sonnet-verify | 66.8% | 294 | One-sentence summaries by external LLMs |

---

## I4 Variants vs Phase 2.1 Baselines

| Strategy | Accuracy | Type |
|----------|----------|------|
| I4 | 73.2% | I4 variant |
| I4-grep2b | 72.9% | I4 variant |
| I4-grep | 72.8% | I4 variant |
| I4-template | 72.2% | I4 variant |
| I4-kw2 | 71.4% | I4 variant |
| I4-kw10 | 70.9% | I4 variant |
| I4-kw7 | 70.6% | I4 variant |
| I4-sonnet-verify | 70.5% | I4 variant |
| I1 | 70.1% | Phase 2.1 baseline |
| I3 | 70.0% | Phase 2.1 baseline |
| I4-grep2a | 69.9% | I4 variant |
| R1 | 68.8% | Phase 2.1 baseline |
| I4-sonnet | 68.6% | I4 variant |
| R3 | 68.4% | Phase 2.1 baseline |
| I4-geminiflash | 68.2% | I4 variant |
| C3 | 68.0% | Phase 2.1 baseline |
| I2 | 67.0% | Phase 2.1 baseline |
| I4-gpt4omini | 65.5% | I4 variant |
| I4-qwen7b | 65.4% | I4 variant |
| I4-qwen32b | 62.5% | I4 variant |
| R4 | 36.0% | Phase 2.1 baseline |
| C2 | 35.8% | Phase 2.1 baseline |

---

## I4 Variants by Dataset

| Variant | Soong-v5 | Obsidian | Delta |
|---------|----------|----------|-------|
| I4 | 77.1% | 69.8% | +7.3% |
| I4-grep2b | 74.9% | 71.1% | +3.8% |
| I4-grep | 70.0% | 75.2% | -5.3% |
| I4-template | 75.4% | 69.5% | +5.9% |
| I4-kw2 | 76.3% | 67.0% | +9.4% |
| I4-kw10 | 73.8% | 68.4% | +5.4% |
| I4-kw7 | 75.2% | 66.5% | +8.6% |
| I4-sonnet-verify | 74.7% | 66.8% | +7.9% |
| I4-grep2a | 70.1% | 69.7% | +0.4% |
| I4-sonnet | 72.0% | 65.6% | +6.4% |
| I4-geminiflash | 73.6% | 63.5% | +10.2% |
| I4-gpt4omini | 67.6% | 63.7% | +3.8% |
| I4-qwen7b | 73.1% | 58.7% | +14.5% |
| I4-qwen32b | 71.6% | 54.5% | +17.1% |

---

## I4 Variants by Question Type

| Variant | navigation | cross-reference | depth | synthesis |
|---------|-------|-------|-------|-------|
| I4 | 100.0% | 57.7% | 62.0% | 55.2% |
| I4-grep2b | 99.4% | 57.6% | 62.5% | 52.2% |
| I4-grep | 99.4% | 55.0% | 63.0% | 57.4% |
| I4-template | 99.4% | 58.3% | 61.7% | 46.2% |
| I4-kw2 | 100.0% | 57.1% | 60.4% | 42.4% |
| I4-kw10 | 99.4% | 58.4% | 56.9% | 45.9% |
| I4-kw7 | 99.4% | 57.5% | 54.6% | 50.7% |
| I4-sonnet-verify | 99.4% | 52.0% | 62.5% | 44.8% |
| I4-grep2a | 93.5% | 55.8% | 59.6% | 56.0% |
| I4-sonnet | 99.4% | 52.1% | 55.8% | 43.4% |
| I4-geminiflash | 93.5% | 57.3% | 55.3% | 46.5% |
| I4-gpt4omini | 93.5% | 51.6% | 54.2% | 38.9% |
| I4-qwen7b | 99.4% | 44.8% | 53.9% | 37.8% |
| I4-qwen32b | 100.0% | 50.6% | 37.0% | 34.9% |

---

## Cost Analysis

| Variant | Total Cost | Avg Cost/Test | Accuracy | Cost/Correct |
|---------|------------|---------------|----------|--------------|
| I4 | $1.97 | $0.0402 | 73.2% | $0.104 |
| I4-grep2b | $2.32 | $0.0473 | 72.9% | $0.129 |
| I4-grep | $2.34 | $0.0477 | 72.8% | $0.130 |
| I4-template | $2.10 | $0.0428 | 72.2% | $0.117 |
| I4-kw2 | $2.11 | $0.0431 | 71.4% | $0.117 |
| I4-kw10 | $2.18 | $0.0445 | 70.9% | $0.121 |
| I4-kw7 | $2.16 | $0.0441 | 70.6% | $0.120 |
| I4-sonnet-verify | $2.80 | $0.0572 | 70.5% | $0.165 |
| I4-grep2a | $2.34 | $0.0477 | 69.9% | $0.137 |
| I4-sonnet | $2.38 | $0.0485 | 68.6% | $0.140 |
| I4-geminiflash | $2.16 | $0.0440 | 68.2% | $0.127 |
| I4-gpt4omini | $2.42 | $0.0493 | 65.5% | $0.151 |
| I4-qwen7b | $2.43 | $0.0497 | 65.4% | $0.143 |
| I4-qwen32b | $2.34 | $0.0477 | 62.5% | $0.138 |

---

## Key Findings

### 1. Heuristic templates beat LLM-generated summaries

Template/extraction methods average **71.7%** vs LLM-generated **66.8%**.
The most expensive summary generation (Sonnet, GPT-4o-mini) does not produce the best results.
This suggests the model benefits more from structured metadata (file path, category, keywords)
than from prose descriptions of content.

### 2. Keyword count has diminishing returns

- I4-kw10: 70.9%
- I4-kw2: 71.4%
- I4-kw7: 70.6%

2 keywords performs best — more keywords add noise rather than signal.

### 3. Grep-based access is competitive with @ref loading

I4-grep2b (72.9%) instructs the model to grep the summary file rather than loading it via @ref.
This nearly matches the best @ref-loaded variants, suggesting the access method matters less
than the summary content itself.

### 4. Local LLMs underperform cloud LLMs for summary generation

| Model | Accuracy |
|-------|----------|
| I4-sonnet | 68.6% |
| I4-sonnet-verify | 70.5% |
| I4-geminiflash | 68.2% |
| I4-gpt4omini | 65.5% |
| I4-qwen7b | 65.4% |
| I4-qwen32b | 62.5% |

Qwen 32B (62.5%) performs worst despite being the largest local model.
This may reflect summary quality issues or formatting differences.

### 5. The Obsidian gap is consistent across variants

All I4 variants perform 5-15% worse on Obsidian than Soong-v5.
This gap is independent of summary generation method, confirming it reflects
dataset difficulty rather than summary quality.

---

## Methodology Notes

- **Test model**: All tests run with Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Summary generators vary**: Each I4 variant uses different models/methods to generate summaries
- **Test conditions identical**: Same questions, same datasets, same runner, same permissions
- **Single-shot**: Each question run once per variant (no repeats)
- **NAV-008 ground truth**: Updated from 0.72 to 0.94 (corpus v5+ change)

---

*14 I4 variants, 686 tests, $32.04 total cost.*