# Phase 2: Context Strategy Test Results

**1323 tests** evaluated.
**Total cost**: $53.44

## Overall Performance

- Average Score: **54.0%**
- Exact Matches: 347
- Variant Matches: 23
- Zero Scores: 344

## Strategy Rankings

| Strategy | Avg Score | Exact | Tests | Cost/Correct |
|----------|-----------|-------|-------|--------------|
| I4 | 73.2% | 19/49 | 49 | $0.104 |
| I4-grep2b | 72.9% | 17/49 | 49 | $0.129 |
| I4-grep | 72.8% | 17/49 | 49 | $0.130 |
| I4-template | 72.2% | 17/49 | 49 | $0.117 |
| I4-kw2 | 71.4% | 18/49 | 49 | $0.117 |
| I4-kw10 | 70.9% | 17/49 | 49 | $0.121 |
| I4-kw7 | 70.6% | 17/49 | 49 | $0.120 |
| I4-sonnet-verify | 70.5% | 16/49 | 49 | $0.165 |
| I1 | 70.1% | 17/49 | 49 | $0.112 |
| I3 | 70.0% | 17/49 | 49 | $0.113 |
| I4-grep2a | 69.9% | 16/49 | 49 | $0.137 |
| R1 | 68.8% | 14/49 | 49 | $0.108 |
| I4-sonnet | 68.6% | 16/49 | 49 | $0.140 |
| R3 | 68.4% | 14/49 | 49 | $0.115 |
| I4-geminiflash | 68.2% | 16/49 | 49 | $0.127 |
| C3 | 68.0% | 17/49 | 49 | $0.122 |
| I2 | 67.0% | 15/49 | 49 | $0.181 |
| I4-gpt4omini | 65.5% | 15/49 | 49 | $0.151 |
| I4-qwen7b | 65.4% | 16/49 | 49 | $0.143 |
| I4-qwen32b | 62.5% | 17/49 | 49 | $0.138 |
| R4 | 36.0% | 10/49 | 49 | $0.373 |
| C2 | 35.8% | 9/49 | 49 | $0.437 |
| C1 | 0.0% | 0/49 | 49 | N/A |
| R2.1 | 0.0% | 0/49 | 49 | N/A |
| R2.2 | 0.0% | 0/49 | 49 | N/A |
| R2.3 | 0.0% | 0/49 | 49 | N/A |
| R2.4 | 0.0% | 0/49 | 49 | N/A |

**Note**: R2.1–R2.4 (whole-file @-ref strategies with varying annotation levels) all exceeded the context window, producing 0% accuracy. The intended research question — whether @-ref annotations improve accuracy — remains unanswered due to overflow. A future test with fewer files would be needed to isolate this variable.

## By Dataset

| Dataset | Avg Score | Tests |
|---------|-----------|-------|
| obsidian | 48.4% | 702 |
| soong-v5 | 60.4% | 621 |

## Strategy × Dataset Matrix

| Strategy × Dataset | Avg Score | Exact | Tests |
|---------------------|-----------|-------|-------|
| C1/obsidian | 0.0% | 0/26 | 26 |
| C1/soong-v5 | 0.0% | 0/23 | 23 |
| C2/obsidian | 0.0% | 0/26 | 26 |
| C2/soong-v5 | 76.3% | 9/23 | 23 |
| C3/obsidian | 61.7% | 7/26 | 26 |
| C3/soong-v5 | 75.2% | 10/23 | 23 |
| I1/obsidian | 67.1% | 8/26 | 26 |
| I1/soong-v5 | 73.5% | 9/23 | 23 |
| I2/obsidian | 60.9% | 6/26 | 26 |
| I2/soong-v5 | 74.0% | 9/23 | 23 |
| I3/obsidian | 62.7% | 6/26 | 26 |
| I3/soong-v5 | 78.3% | 11/23 | 23 |
| I4/obsidian | 69.8% | 8/26 | 26 |
| I4/soong-v5 | 77.1% | 11/23 | 23 |
| I4-geminiflash/obsidian | 63.5% | 6/26 | 26 |
| I4-geminiflash/soong-v5 | 73.6% | 10/23 | 23 |
| I4-gpt4omini/obsidian | 63.7% | 7/26 | 26 |
| I4-gpt4omini/soong-v5 | 67.6% | 8/23 | 23 |
| I4-grep/obsidian | 75.2% | 8/26 | 26 |
| I4-grep/soong-v5 | 70.0% | 9/23 | 23 |
| I4-grep2a/obsidian | 69.7% | 8/26 | 26 |
| I4-grep2a/soong-v5 | 70.1% | 8/23 | 23 |
| I4-grep2b/obsidian | 71.1% | 7/26 | 26 |
| I4-grep2b/soong-v5 | 74.9% | 10/23 | 23 |
| I4-kw10/obsidian | 68.4% | 7/26 | 26 |
| I4-kw10/soong-v5 | 73.8% | 10/23 | 23 |
| I4-kw2/obsidian | 67.0% | 7/26 | 26 |
| I4-kw2/soong-v5 | 76.3% | 11/23 | 23 |
| I4-kw7/obsidian | 66.5% | 7/26 | 26 |
| I4-kw7/soong-v5 | 75.2% | 10/23 | 23 |
| I4-qwen32b/obsidian | 54.5% | 7/26 | 26 |
| I4-qwen32b/soong-v5 | 71.6% | 10/23 | 23 |
| I4-qwen7b/obsidian | 58.7% | 7/26 | 26 |
| I4-qwen7b/soong-v5 | 73.1% | 9/23 | 23 |
| I4-sonnet/obsidian | 65.6% | 7/26 | 26 |
| I4-sonnet/soong-v5 | 72.0% | 9/23 | 23 |
| I4-sonnet-verify/obsidian | 66.8% | 7/26 | 26 |
| I4-sonnet-verify/soong-v5 | 74.7% | 9/23 | 23 |
| I4-template/obsidian | 69.5% | 7/26 | 26 |
| I4-template/soong-v5 | 75.4% | 10/23 | 23 |
| R1/obsidian | 63.2% | 6/26 | 26 |
| R1/soong-v5 | 75.1% | 8/23 | 23 |
| R2.1/obsidian | 0.0% | 0/26 | 26 |
| R2.1/soong-v5 | 0.0% | 0/23 | 23 |
| R2.2/obsidian | 0.0% | 0/26 | 26 |
| R2.2/soong-v5 | 0.0% | 0/23 | 23 |
| R2.3/obsidian | 0.0% | 0/26 | 26 |
| R2.3/soong-v5 | 0.0% | 0/23 | 23 |
| R2.4/obsidian | 0.0% | 0/26 | 26 |
| R2.4/soong-v5 | 0.0% | 0/23 | 23 |
| R3/obsidian | 62.4% | 4/26 | 26 |
| R3/soong-v5 | 75.2% | 10/23 | 23 |
| R4/obsidian | 0.0% | 0/26 | 26 |
| R4/soong-v5 | 76.6% | 10/23 | 23 |

## By Question Type

| Type | Avg Score | Tests |
|------|-----------|-------|
| cross-reference | 42.9% | 378 |
| depth | 44.2% | 351 |
| navigation | 76.6% | 459 |
| synthesis | 34.1% | 135 |

## By Difficulty

| Difficulty | Avg Score | Tests |
|------------|-----------|-------|
| easy | 72.9% | 378 |
| hard | 40.0% | 405 |
| medium | 51.4% | 540 |

*Generated: 2026-02-20T15:11:22.759615*