# Context Structure Research: How File Organization Affects Claude Code Accuracy

**A systematic study of Claude Code's @ reference system across 849 test configurations**

---

## Executive Summary

We tested how different context file organizations affect Claude Code's ability to answer questions accurately. Testing 849 configurations across corpora from 120K to 622K words, we found:

### Key Findings

1. **Flat structure wins** — Files in a single directory achieve 100% accuracy up to 302K words, and 97.35% at 622K words

2. **One topic per file** — Topically cohesive files with descriptive names outperform all other organizational strategies

3. **Enhancements hurt at scale** — Adding keyword indexes or summaries provides diminishing returns, and actually *hurts* accuracy at 622K words (-4.6%)

4. **Nesting degrades gracefully** — Each level of folder nesting costs ~1-2% accuracy, but even 5 levels maintains 95%+ at 622K words

5. **Scale is less impactful than structure** — Accuracy drops only 2.65% when scaling from 302K to 622K words with flat structure

### The Bottom Line

For Claude Code projects: **use flat structure with descriptive filenames, skip enhancement indexes.**

The simplest approach is the best approach.

---

## Why This Research Matters

Claude Code users face a practical question: *How should I organize my context files?*

Current guidance is limited to general best practices. No one has systematically tested what actually works. We filled that gap with controlled experiments measuring accuracy across:

- **5 structure variants** (flat, shallow, deep, very-deep, monolith)
- **6 enhancement strategies** (summaries, keywords, combinations)
- **3 corpus sizes** (120K, 302K, 622K words)
- **2 loading methods** (classic cd, --add-dir flag)
- **23 question types** (navigation, cross-reference, depth)

Total: **849 individual tests** with ground-truth evaluation.

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
| V5 | 302,000 | 121 | Medium scale |
| V6 | 622,561 | 277 | Large scale |

### Structure Variants

| Structure | Description | Nesting Depth |
|-----------|-------------|---------------|
| Flat | All files in root directory | 0 |
| Shallow | One level of folders | 1 |
| Deep | 3-4 levels of nesting | 3 |
| Very-Deep | 5+ levels of nesting | 5 |
| Monolith | Single combined file | 0 |

### Enhancement Variants

| Enhancement | Description |
|-------------|-------------|
| V5.1 | 2-sentence summary per file |
| V5.2 | 5-sentence summary per file |
| V5.3 | 10 keywords per file |
| V5.4 | 5-sentence summary + keywords |
| V5.5 | 2-sentence summary + keywords |

### Question Types

- **Navigation (10)**: Single-file lookups ("Who is the CEO?")
- **Cross-reference (8)**: Multi-file connections ("What is the relationship between Project X and Y?")
- **Depth (5)**: Specific detail extraction ("What safety protocols exist for ATLAS?")

### Evaluation

Each test received a score from 0-100 based on:
- Exact match with ground truth answer
- Acceptable variant matches
- Partial credit for keyword presence

---

## Results

### Structure Performance by Corpus Size

| Structure | V4 (120K) | V5 (302K) | V6 (622K) |
|-----------|-----------|-----------|-----------|
| **Flat** | **100%** | **100%** | **97.35%** |
| Shallow | 100% | 100% | 94.42% |
| Monolith | 100% | 100% | N/A |
| Deep | 96.78% | 92.04% | 95.00% |
| Very-Deep | 95.65% | 96.04% | 96.04% |

**Finding**: Flat structure maintains highest accuracy across all scales. First degradation appears at 600K+ words.

### Nesting Depth Impact

| Depth | Description | Average Accuracy |
|-------|-------------|------------------|
| 0 | Flat | 99.12% |
| 1 | Shallow | 98.14% |
| 3 | Deep | 94.61% |
| 5 | Very-Deep | 95.91% |

**Finding**: Each level of nesting costs ~1-2% accuracy. Surprisingly, very-deep sometimes outperforms deep (inconsistent).

**Recommendation**: Prefer flat. If nesting required, limit to 1-2 levels.

### Enhancement Strategy Impact

#### Recovery Rate on Previously Failed Questions

| Enhancement | Description | Recovery Rate |
|-------------|-------------|---------------|
| V5.3 | Keywords only | **80%** (4/5) |
| V5.4 | 5-sentence + keywords | 80% (4/5) |
| V5.5 | 2-sentence + keywords | 80% (4/5) |
| V5.1 | 2-sentence summary | 60% (3/5) |
| V5.2 | 5-sentence summary | 40% (2/5) |

**Finding**: Keywords alone match any combined approach. Summaries add no value when keywords present.

#### Enhancement Impact at Scale

| Variant | V5 (302K) | V6 (622K) | Delta |
|---------|-----------|-----------|-------|
| Base flat | 100% | 97.35% | -2.65% |
| Flat + V5.5 | 100% | 92.74% | **-7.26%** |
| Base deep | 92.04% | 95.00% | +2.96% |
| Deep + V5.5 | 89.83% | 92.30% | +2.47% |

**Finding**: Enhancements HURT at 622K words. The ~27K words of index content becomes noise competing for context window space.

### Question Type Performance

| Type | V4 (120K) | V5 (302K) | V6 (622K) | Trend |
|------|-----------|-----------|-----------|-------|
| Navigation | 99% | 100% | 97.5% | Most robust |
| Cross-reference | 97.78% | 93.44% | 93.38% | Stable degradation |
| Depth | 98.6% | 96.8% | 89.59% | Steepest decline |

**Finding**: Navigation queries (single-file) most resilient. Depth queries (specific details) degrade most with scale.

### Loading Method Comparison

| Method | Accuracy | Wins | Ties | Avg Cost/Correct |
|--------|----------|------|------|-----------------|
| adddir | 96.35% | 26 | 361 | $0.0638 |
| classic | 95.69% | 31 | 361 | $0.0726 |

**Finding**: Minimal accuracy difference. adddir saves ~12% per correct answer due to better caching.

### Cost-Effectiveness

*How much does it cost to get a correct answer?*

Data source: 604/849 tests have token/cost data from raw API responses, joined with evaluator accuracy scores. See `results/analysis/cost-effectiveness.md` for full methodology.

#### By Corpus Size

| Corpus | Words | Accuracy | Cost/Test | Cost/Correct Answer | Tokens/Correct |
|--------|-------|----------|-----------|---------------------|----------------|
| V4 | 120K | 96.96% | $0.0751 | $0.0791 | 141,462 |
| V5 | 302K | 90.96% | $0.0671 | $0.0801 | 147,871 |
| **V6** | **622K** | **90.22%** | **$0.0494** | **$0.0547** | **106,419** |

**Finding**: Larger corpora are *cheaper* per correct answer ($0.055 at 622K vs $0.079 at 120K). Better cache hit rates at scale (78% vs 65%) more than offset the larger corpus.

#### By Question Type

| Type | Accuracy | Cost/Correct | Avg Duration |
|------|----------|-------------|--------------|
| Navigation | 99.14% | $0.0452 | 17.8s |
| Cross-reference | 87.34% | $0.0786 | 32.8s |
| Depth | 88.14% | $0.0980 | 39.4s |

**Finding**: Navigation questions are both cheapest and most accurate. Depth questions cost 2.2x more per correct answer and take 2.2x longer.

#### Cheapest Structures per Correct Answer (min 20 tests with cost data)

| Rank | Structure | Corpus | Cost/Correct | Accuracy | Tokens/Correct |
|------|-----------|--------|-------------|----------|----------------|
| 1 | deep-v6 | V6 | $0.0408 | 89.1% | 82,504 |
| 2 | deep-v6-v5.5 | V6 | $0.0453 | 89.1% | 88,591 |
| 3 | flat-v6 | V6 | $0.0532 | 93.5% | 90,153 |
| 4 | deep (v4) | V4 | $0.0539 | 93.5% | 101,078 |
| 5 | very-deep-v6 | V6 | $0.0563 | 93.5% | 107,937 |

**Finding**: At V6 scale, deep structures are cheapest per correct answer ($0.041) but less accurate. flat-v6 costs $0.012 more per answer but gets 4.4% more answers right. The cost premium for accuracy is small.

#### Total Research Cost

| Metric | Value |
|--------|-------|
| Total tests | 849 |
| Tests with cost data | 604 |
| Total API cost | $36.74 |
| Avg cost per test | $0.0608 |
| Avg cost per correct answer | $0.0682 |
| Avg cache hit rate | 74.2% |

---

## The "One Topic = One File" Principle

This emerged as a key architectural insight:

| Approach | Result |
|----------|--------|
| One file with multiple topics | Claude must read entire file to assess relevance |
| One topic spread across files | Claude may miss connections |
| **One topic per file** | Claude can assess relevance from filename alone |

**Why it works**: Claude Code's discovery process lists directory contents first. If each filename clearly indicates its topic, Claude can select relevant files without reading them all.

This explains why:
- Flat structure wins (all filenames visible in one listing)
- Descriptive filenames matter (they ARE the index)
- Enhancement indexes hurt at scale (compete with actual content)

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

1. **Use flat structure** — All files in one directory
2. **One topic per file** — Topically cohesive content
3. **Descriptive filenames** — Include key entities (e.g., `employees-leadership-bios.md`)
4. **Keep CLAUDE.md minimal** — Brief overview, not comprehensive summary
5. **Skip enhancement indexes at scale** — They hurt more than help above 300K words

### What Works

- Flat file organization
- Descriptive, entity-rich filenames
- Topically cohesive files
- Minimal CLAUDE.md

### What Doesn't Work

- Deep folder nesting (3+ levels)
- Long summaries (5-sentence performed worse than 2-sentence)
- Combined enhancements at scale
- Monolith files approaching context limits

---

## Unsolved Cases

### XREF-006: "What is the relationship between Project Hermes and Project Prometheus?"

This question fails across ALL enhancement strategies on nested structures, but succeeds on flat. It requires connecting information across 2 files.

**Implication**: Complex cross-references are inherently harder in nested structures where Claude must navigate rather than scan.

---

## Implications for Claude Code Users

### Context Window Isn't the Bottleneck

We expected accuracy to drop as corpus size approached Haiku's 200K context limit. Instead, accuracy remained high even with 622K words of source material.

**Why**: Claude Code loads context selectively based on the question. It doesn't dump everything into context.

### Structure Aids Discovery

Flat structure works best because Claude can "see" all filenames in a single directory listing. Nested structures require navigation, increasing the chance of missing relevant content.

### Enhancement Overhead

At large scales, index content (~27K words in V5.5) competes with actual content for context window space. The overhead outweighs any discovery benefit.

---

## Reproduction

### Requirements
- Claude Code CLI
- Bash, Python 3.x, jq

### Quick Start
```bash
git clone https://github.com/davidmoneil/context-structure-research
cd context-structure-research

# Run a single test
./harness/run-test.sh --structure flat-v5 --question NAV-001

# Run full matrix
./harness/run-haiku-matrix-v5-no-monolith.sh

# Analyze results
python3 harness/evaluator.py results/v5/raw/haiku --output results/v5/analysis
```

### Directory Structure
```
context-structure-research/
├── README.md                    # This file
├── PROJECT-CHARTER.md           # Research mission and scope
├── docs/
│   ├── methodology.md           # Full test methodology
│   ├── phase-1-analysis-plan.md # Analysis planning
│   ├── phase-2-indexing-strategies.md  # Code indexing strategies
│   └── prior-art-research.md    # Industry research
├── harness/
│   ├── questions.json           # 23 test questions with ground truth
│   ├── run-test.sh              # Single test runner (headless Claude)
│   ├── evaluator.py             # Scores responses against ground truth
│   ├── consolidate-results.py   # Merges all suites into unified dataset
│   ├── analyze-all.py           # Full Phase 1 analysis (uses evaluator scores)
│   ├── cost-analyzer.py         # Token usage and API cost analysis
│   ├── cost-effectiveness.py    # Joins accuracy + cost → cost/correct answer
│   └── *.sh                     # Test matrix runner scripts
├── results/
│   ├── analysis/                # Consolidated analysis output
│   │   ├── phase-1-complete-analysis.md  # Structure/scale/nesting analysis
│   │   ├── cost-report.md                # Token and API cost breakdown
│   │   ├── cost-effectiveness.md         # Cost per correct answer (joined)
│   │   └── *.json                        # Raw data for each report
│   ├── v4/, v5/, v6-*/          # Per-suite raw results + evaluator output
│   └── cross-variant-comparison.md
├── soong-daystrom/              # Test corpus
│   ├── _source-v4/, v5/, v6/    # Source content
│   ├── flat-*, deep-*, etc.     # Structure variants
│   └── *-v5.*/                  # Enhancement variants
└── report/
    ├── README.md                # Full report (this file)
    └── executive-summary.md     # One-page summary
```

### Analysis Pipeline

The analysis pipeline runs in stages, each producing independent outputs:

```
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Test Execution (run-test.sh / runner scripts)     │
│  Input:  Corpus + questions.json                            │
│  Output: results/*/raw/haiku/*.json (raw API responses)     │
│          Each file = one question × one structure × one     │
│          loading method. Contains full Claude response       │
│          with answer text and API usage data.                │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┴──────────────┐
    ▼                            ▼
┌─────────────────────┐  ┌────────────────────────┐
│ Stage 2a: Evaluator  │  │ Stage 2b: Cost Analyzer │
│ (evaluator.py)       │  │ (cost-analyzer.py)      │
│                      │  │                          │
│ Reads: raw responses │  │ Reads: raw responses     │
│ Scores against       │  │ Extracts: input_tokens,  │
│ questions.json       │  │ output_tokens, cache      │
│ ground truth         │  │ tokens, cost_usd,         │
│                      │  │ duration_ms               │
│ Output: results/*/   │  │                          │
│ analysis/results.json│  │ Output: results/analysis/ │
│ (scores per test)    │  │ cost-report.md            │
└─────────┬───────────┘  └──────────┬─────────────┘
          │                         │
          └────────────┬────────────┘
                       ▼
          ┌────────────────────────┐
          │ Stage 3: Cost-         │
          │ Effectiveness          │
          │ (cost-effectiveness.py)│
          │                        │
          │ Joins evaluator scores │
          │ with raw cost data by  │
          │ composite key:         │
          │ (suite, structure,     │
          │  loading_method,       │
          │  question_id)          │
          │                        │
          │ Output: results/       │
          │ analysis/cost-         │
          │ effectiveness.md       │
          └────────────────────────┘
```

**Reproduction commands:**
```bash
cd context-structure-research

# Stage 2a: Score all test suites
for suite in v4 v5 v5-enhancements v5.5-matrix v6-matrix; do
  python3 harness/evaluator.py results/$suite/raw/haiku --output results/$suite/analysis
done
python3 harness/evaluator.py results/v6-extended/raw/haiku/haiku --output results/v6-extended/analysis

# Stage 2b: Consolidate + analyze
python3 harness/consolidate-results.py
python3 harness/analyze-all.py

# Stage 2c: Cost analysis
python3 harness/cost-analyzer.py results/*/raw/haiku results/v6-extended/raw/haiku/haiku \
  --output results/analysis --format both

# Stage 3: Cost-effectiveness (joins accuracy + cost)
python3 harness/cost-effectiveness.py
```

---

## Limitations

1. **Single model tested** — Results are for Claude 3.5 Haiku. Sonnet/Opus may differ.
2. **Synthetic corpus** — Real-world codebases may behave differently (Phase 2 planned).
3. **Prose content** — Code-heavy repos may need different strategies.
4. **Fixed question set** — 23 questions may not cover all query patterns.
5. **Single domain** — Corporate knowledge base; other domains untested.

---

## Future Work

### Phase 2: Code Repository Testing

The next phase will test these findings against real codebases:

- **Different content type**: Code vs prose
- **Function-level indexing**: Do code indexes help?
- **AST-based strategies**: Auto-generated function/class maps
- **Real-world validation**: Test on open-source repos

See `docs/phase-2-indexing-strategies.md` for the full plan.

---

## Conclusion

For Claude Code projects, **flat file structure with descriptive filenames delivers the best accuracy** across all scales tested.

Enhancement indexes provide diminishing returns and should be skipped for projects over 300K words.

The simplest approach—files in one directory with clear names—is often the best.

---

## Citation

If you use this research, please cite:

```
Context Structure Research: How File Organization Affects Claude Code Accuracy
https://github.com/davidmoneil/context-structure-research
January 2026
```

---

*Research conducted January-February 2026. 849 test runs, $36.74 total API cost.*
