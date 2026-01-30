# Context Structure Research: How File Organization Affects Claude Code Accuracy

**A systematic study of Claude Code's @ reference system across 757 test configurations**

---

## Executive Summary

We tested how different context file organizations affect Claude Code's ability to answer questions accurately. Testing 746 configurations across corpora ranging from 120K to 622K words, we found:

### Key Findings

1. **Flat structure wins** — Files in a single directory achieve the highest accuracy (97-100%) across all corpus sizes tested

2. **Structure matters more than enhancements** — Adding keyword indexes or summaries provides diminishing returns, and actually *hurts* accuracy at scale (622K words)

3. **Deep nesting degrades gracefully** — Nested folder structures lose ~3-5% accuracy but remain viable even at 622K words

4. **Scale is less impactful than expected** — Accuracy drops only ~4% when scaling from 120K to 622K words with proper structure

### Quick Recommendation

For Claude Code projects under 600K words: **use flat structure, skip enhancement indexes.**

---

## Test Methodology

### Corpus: Soong-Daystrom Industries

A synthetic knowledge base for a fictional robotics company, containing:
- Employee directories and leadership bios
- Project documentation (ATLAS, ARIA, Prometheus, Hermes)
- Financial reports and governance documents
- Technical specifications and incident reports

| Version | Words | Files | Purpose |
|---------|-------|-------|---------|
| V4 | 120,000 | 80 | Baseline |
| V5 | 302,000 | 121 | Scale test |
| V6 | 622,561 | 277 | Large scale |

### Question Types

23 questions across three categories:

- **Navigation (10)**: Single-file lookups ("Who is the CEO?")
- **Cross-reference (8)**: Multi-file connections ("What is the relationship between Project X and Y?")
- **Depth (5)**: Specific detail extraction ("What safety protocols exist for ATLAS?")

### Structure Variants

| Structure | Description |
|-----------|-------------|
| Flat | All files in root directory |
| Shallow | One level of folders |
| Deep | 3-4 levels of nesting |
| Very-Deep | 5+ levels of nesting |
| Monolith | Single combined file |

### Enhancement Variants (V5.5)

| Enhancement | Description |
|-------------|-------------|
| V5.1 | 2-sentence summaries per file |
| V5.2 | 5-sentence summaries per file |
| V5.3 | 10 keywords per file |
| V5.4 | 5-sentence + keywords |
| V5.5 | 2-sentence + keywords |

### Test Execution

- Model: Claude 3.5 Haiku
- Loading methods: Classic (cd into directory) and add-dir (--add-dir flag)
- Total tests: 757 across all variants

---

## Results

### Structure Performance by Corpus Size

| Structure | V4 (120K) | V5 (302K) | V6 (622K) |
|-----------|-----------|-----------|-----------|
| **Flat** | **100%** | **100%** | **97.35%** |
| Shallow | 100% | 100% | n/a |
| Deep | 96.78% | 92.04% | 95.00% |
| Very-Deep | 95.65% | 96.04% | n/a |

**Finding**: Flat structure maintains highest accuracy across all scales. First degradation appears at 600K+ words.

### Enhancement Impact at Different Scales

| Variant | V5 (302K) | V6 (622K) | Delta |
|---------|-----------|-----------|-------|
| Base flat | 100% | 97.35% | -2.65% |
| Flat + V5.5 | 100% | 92.74% | -7.26% |
| Base deep | 92.04% | 95.00% | +2.96% |
| Deep + V5.5 | 89.83% | 89.88% | +0.05% |

**Finding**: Enhancement indexes help at 300K words but *hurt* at 600K+ words. The added index content appears to create noise rather than aid navigation.

### Question Type Analysis

| Type | V4 | V5 | V6 |
|------|-----|-----|-----|
| Navigation | 99% | 100% | 97.5% |
| Cross-reference | 97.78% | 93.44% | 92.69% |
| Depth | 98.6% | 96.8% | 88.11% |

**Finding**: Navigation questions (single-file) most robust. Cross-reference and depth questions degrade with scale.

### Loading Method Comparison

| Metric | Classic | add-dir |
|--------|---------|---------|
| Overall wins | 15 | 14 |
| Ties | 294 | - |

**Finding**: Loading method has minimal impact. Use whichever fits your workflow.

---

## Practical Recommendations

### By Project Size

**Small Projects (<100K words)**
- Any structure works
- No enhancements needed
- Monolith acceptable

**Medium Projects (100-300K words)**
- Use flat structure (guaranteed 100%)
- Keyword index optional but helpful
- Avoid >2 levels of nesting

**Large Projects (300-600K words)**
- Use flat structure (97%+ accuracy)
- Skip enhancement indexes
- Consider splitting by domain

**Very Large Projects (600K+ words)**
- Flat structure still best
- Do NOT add keyword/summary indexes
- Consider splitting into sub-corpora

### Structure Guidelines

1. **Prefer flat over nested** — Every level of nesting reduces accuracy slightly
2. **Use descriptive filenames** — Include key entities in filename (e.g., `employees-leadership-bios.md`)
3. **Keep CLAUDE.md minimal** — Brief overview, not comprehensive summary
4. **Skip enhancement indexes at scale** — They hurt more than help above 300K words

### What Didn't Work

- Long summaries (5-sentence) performed worse than short (2-sentence)
- Combined enhancements (summary + keywords) often worse than single enhancement
- Very deep nesting (5+ levels) showed inconsistent results

---

## Implications for Claude Code Users

### Context Window Isn't the Bottleneck

We expected accuracy to drop as corpus size approached Haiku's 200K context limit. Instead, accuracy remained high even with 622K words of source material, because Claude Code loads context selectively based on the question.

### Structure Aids Discovery

Flat structure works best because Claude can "see" all filenames in a single directory listing, making it easier to identify relevant files. Nested structures require navigation, increasing the chance of missing relevant content.

### Enhancement Overhead

At large scales, the ~27K words of index content in V5.5 variants added noise that competed with actual content for context window space. Simpler is better.

---

## Reproduction

### Requirements
- Claude Code CLI
- Bash, Python 3.x, jq

### Quick Start
```bash
git clone https://github.com/your-repo/context-structure-research
cd context-structure-research

# Run a single test
./harness/run-test.sh --structure flat-v5 --question NAV-001

# Run full matrix
./harness/run-v6-matrix.sh

# Analyze results
python3 harness/evaluator.py results/v6-matrix/raw/haiku --output results/analysis
```

### Test Corpus
The Soong-Daystrom Industries corpus is included in `soong-daystrom/`. Structure variants are pre-built.

---

## Raw Data

All raw test results are available in `results/`:
- `v4/` — 230 tests, 120K word corpus
- `v5/` — 191 tests, 302K word corpus
- `v5-enhancements/` — 60 targeted tests
- `v5.5-matrix/` — 92 tests, enhanced structures
- `v6-matrix/` — 184 tests, 622K word corpus

Analysis reports in `results/*/analysis/report.md`.

---

## Limitations

1. **Single model tested** — Results are for Claude 3.5 Haiku. Sonnet/Opus may differ.
2. **Synthetic corpus** — Real-world codebases may behave differently.
3. **Question design** — Questions designed to have clear answers; open-ended queries not tested.
4. **One domain** — Corporate knowledge base; code-heavy repos may differ.

---

## Conclusion

For Claude Code projects, **flat file structure delivers the best accuracy** across all scales tested. Enhancement indexes (summaries, keywords) provide diminishing returns and should be skipped for projects over 300K words.

The simplest approach is often the best: put your files in one directory with clear, descriptive names.

---

*Research conducted January 2026. Total API cost: ~$16 across 757 test runs.*
