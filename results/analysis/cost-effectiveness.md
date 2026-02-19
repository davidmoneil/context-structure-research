# Cost-Effectiveness Analysis

**Generated**: 2026-02-18 19:57
**Total Tests**: 849 (604 with cost data)

---

## Methodology

### Data Sources

This report joins two independent data sources for each test:

1. **Accuracy scores** from `evaluator.py` (per-suite `results/*/analysis/results.json`)
   - Each test is scored against ground truth from `harness/questions.json` (23 questions)
   - Scoring: exact match (100%), acceptable variant match (100%), partial keyword credit (50-99%), or miss (0%)
   - Evaluator was run independently per suite, then scores are loaded by this script

2. **Cost/token data** from raw API responses (per-suite `results/*/raw/haiku/*.json`)
   - Each raw result contains the full Claude Code API response including `usage` block
   - Extracted fields: `input_tokens`, `output_tokens`, `cache_read_input_tokens`,
     `cache_creation_input_tokens`, `total_cost_usd`, `duration_ms`
   - 604/849 tests have cost data; early v4 runs (flat, monolith, shallow) used a format
     that didn't capture usage info

### Join Logic

Records are matched by composite key: `(suite, structure, loading_method, question_id)`.
The same key appears in both the evaluator output and the raw response filename.
For example, `v6-extended / shallow-v6 / adddir / NAV-001` links the evaluator's
accuracy score with the API response's token usage for that exact test run.

### Metrics

- **Accuracy (strict)**: Percentage of tests scoring exactly 100% (exact or variant match).
  Partial credit does NOT count as correct. This is stricter than the full analysis report
  which averages all scores including partial credit.
- **Cost/Correct Answer**: `total_cost / number_of_correct_answers` for the group
- **Tokens/Correct Answer**: `total_tokens / number_of_correct_answers` — includes
  input, output, cache read, and cache creation tokens
- **Cost-Effectiveness**: `accuracy_percentage / total_cost` (higher = more accuracy per dollar)

### Caveats

- Structures with < 20 cost-data points are excluded from the Key Insights rankings
- Token counts include cache tokens; effective cost depends on cache hit rates (74% average)
- All tests used Claude 3.5 Haiku pricing; costs would differ for Sonnet/Opus
- The v4 flat/monolith/shallow structures show $0 cost because those early runs
  didn't capture usage data — their accuracy is real but cost-effectiveness can't be computed

---

## Overall

| Metric | Value |
|--------|-------|
| Accuracy | 92.34% |
| Total Cost | $36.74 |
| Avg Cost/Test | $0.0608 |
| **Avg Cost/Correct Answer** | **$0.0682** |
| Avg Tokens/Test | 113,479 |
| **Avg Tokens/Correct Answer** | **127,164** |
| Cost-Effectiveness | 2.5 accuracy%/$ |

---

## By Structure (sorted by cost per correct answer)

| Structure | Corpus | Accuracy | Cost/Correct | Tokens/Correct | Cost-Eff |
|-----------|--------|----------|-------------|----------------|----------|
| flat-v5-v5.5 | v5 | 100.0% | $0.0005 | 0 | 196850.4 |
| flat-v5 | v5 | 100.0% | $0.0006 | 0 | 170068.0 |
| deep-v6 | v6 | 89.13% | $0.0408 | 82,504 | 53.3 |
| deep-v6-v5.5 | v6 | 89.13% | $0.0453 | 88,591 | 48.0 |
| flat-v6 | v6 | 93.48% | $0.0532 | 90,153 | 40.8 |
| deep | v4 | 93.48% | $0.0539 | 101,078 | 40.3 |
| very-deep-v6 | v6 | 93.48% | $0.0563 | 107,937 | 38.6 |
| very-deep | v4 | 91.3% | $0.0575 | 100,720 | 37.8 |
| shallow-v6 | v6 | 91.3% | $0.0581 | 115,188 | 37.4 |
| very-deep-v5 | v5 | 93.48% | $0.0611 | 110,532 | 35.6 |
| flat-v6-v5.5 | v6 | 84.78% | $0.0757 | 157,117 | 28.7 |
| deep-v5 | v5 | 82.61% | $0.0784 | 138,785 | 27.7 |
| deep-v5-v5.5 | v5 | 80.36% | $0.0821 | 149,265 | 21.8 |
| deep-v5-v5.1 | v5 | 80.0% | $0.0968 | 181,012 | 103.3 |
| deep-v5-v5.2 | v5 | 90.0% | $0.0977 | 222,704 | 102.3 |
| deep-v5-v5.3 | v5 | 90.0% | $0.0984 | 189,395 | 101.6 |
| shallow | v4 | 100.0% | $0.1225 | 216,412 | 17.7 |
| deep-v5-v5.4 | v5 | 50.0% | $0.1804 | 322,171 | 55.4 |
| flat | v4 | 100.0% | $0.0000 | 0 | 0 |
| monolith | v4 | 100.0% | $0.0000 | 0 | 0 |
| monolith-v5 | v5 | 100.0% | $0.0000 | 0 | 0 |
| shallow-v5 | v5 | 100.0% | $0.0000 | 0 | 0 |

---

## By Corpus Size

| Corpus | Words | Accuracy | Avg Cost/Test | Cost/Correct | Tokens/Correct |
|--------|-------|----------|---------------|-------------|----------------|
| v4 | 120,000 | 96.96% | $0.0751 | $0.0791 | 141,462 |
| v5 | 302,000 | 90.96% | $0.0671 | $0.0801 | 147,871 |
| v6 | 622,561 | 90.22% | $0.0494 | $0.0547 | 106,419 |

---

## By Question Type

| Type | Accuracy | Avg Cost/Test | Cost/Correct | Duration/Test |
|------|----------|---------------|-------------|---------------|
| navigation | 99.14% | $0.0447 | $0.0452 | 17,814ms |
| cross-reference | 87.34% | $0.0648 | $0.0786 | 32,764ms |
| depth | 88.14% | $0.0820 | $0.0980 | 39,385ms |

---

## By Loading Method

| Method | Accuracy | Avg Cost/Test | Cost/Correct | Tokens/Correct |
|--------|----------|---------------|-------------|----------------|
| adddir | 92.64% | $0.0573 | $0.0638 | 122,891 |
| classic | 92.06% | $0.0644 | $0.0726 | 131,485 |

---

## Key Insights

### Cheapest per Correct Answer (min 20 tests with cost data)

1. **deep-v6** (v6): $0.0408/correct answer (89.13% accuracy, 82,504 tokens/correct)
2. **deep-v6-v5.5** (v6): $0.0453/correct answer (89.13% accuracy, 88,591 tokens/correct)
3. **flat-v6** (v6): $0.0532/correct answer (93.48% accuracy, 90,153 tokens/correct)
4. **deep** (v4): $0.0539/correct answer (93.48% accuracy, 101,078 tokens/correct)
5. **very-deep-v6** (v6): $0.0563/correct answer (93.48% accuracy, 107,937 tokens/correct)

### Most Expensive per Correct Answer

1. **shallow** (v4): $0.1225/correct answer (100.0% accuracy, 216,412 tokens/correct)
2. **deep-v5-v5.5** (v5): $0.0821/correct answer (80.36% accuracy, 149,265 tokens/correct)
3. **deep-v5** (v5): $0.0784/correct answer (82.61% accuracy, 138,785 tokens/correct)

---

*Report generated by cost-effectiveness.py*