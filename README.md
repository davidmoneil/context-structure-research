# Context Structure Research

**How File Organization Affects Claude Code Accuracy**

A systematic study of Claude Code's `@` reference system across 849 test configurations.

---

## TL;DR

**Put your files in one directory with clear, descriptive names.** That's it.

| Structure | Accuracy (622K words) |
|-----------|----------------------|
| **Flat** | **97.35%** |
| Shallow (1 level) | 94.42% |
| Deep (3 levels) | 95.00% |
| Very Deep (5 levels) | 96.04% |

Flat structure wins. Deep nesting (3 levels) hurts most; very-deep (5 levels) partially recovers.

---

## Key Findings

### 1. Flat Structure Wins

Files in a single directory achieve 100% accuracy up to 302K words, and 97.35% at 622K words.

### 2. One Topic Per File

Claude assesses relevance from filenames. If each file covers one topic with a descriptive name, Claude can select the right files without reading them all.

**Example**: `employees-leadership-bios.md` beats `docs/org/people/leaders.md`

### 3. Nesting Depth Is Non-Linear

| Depth | Accuracy (all scales) |
|-------|----------------------|
| 0 (flat) | 98.4% |
| 1 (shallow) | 98.1% |
| 3 (deep) | 92.5% |
| 5 (very-deep) | 95.9% |

Deep nesting (3 levels) is the worst performer. Very-deep (5 levels) partially recovers — the degradation is not linear.

### 4. Skip Enhancement Indexes at Scale

| Enhancement | At 302K | At 622K |
|-------------|---------|---------|
| None (flat) | 100% | 97.35% |
| With indexes | 100% | 92.74% |

Adding keyword indexes or summaries **hurts** accuracy at 622K words (-4.6%). The overhead becomes noise.

### 5. Scale Is Manageable

First meaningful accuracy drop appears around 600K words, and it's only 2.65%. Structure matters more than size.

---

## Practical Recommendations

| Project Size | Strategy |
|--------------|----------|
| <100K words | Anything works |
| 100-300K words | Flat, keyword index optional |
| 300-600K words | Flat, skip indexes |
| 600K+ words | Flat, consider splitting |

### What Works

- Flat file organization
- Descriptive, entity-rich filenames
- Topically cohesive files (one topic = one file)
- Minimal CLAUDE.md

### What Doesn't Work

- Deep folder nesting (3+ levels)
- Long summaries (5-sentence performed worse than 2-sentence)
- Combined enhancements at scale
- Monolith files approaching context limits

---

## The Study

- **849 tests** across 5 structures, 6 enhancements, 3 corpus sizes
- **Corpus**: 120K → 302K → 622K words (Soong-Daystrom Industries)
- **Model**: Claude 3.5 Haiku
- **Ground-truth evaluation** against 23 known-answer questions

### Structure Variants Tested

| Structure | Nesting Depth | Description |
|-----------|---------------|-------------|
| Flat | 0 | All files in root directory |
| Shallow | 1 | One level of folders |
| Deep | 3 | Multiple nesting levels |
| Very-Deep | 5+ | Maximum practical nesting |
| Monolith | 0 | Single combined file |

### Enhancement Strategies Tested

| Enhancement | Description | Recovery Rate* |
|-------------|-------------|----------------|
| Keywords only | 10 keywords per file | **80%** |
| 2-sentence summary | Brief summary | 60% |
| 5-sentence summary | Detailed summary | 40% |
| Summary + keywords | Combined | 80% |

*\*Recovery Rate = % of 5 specific questions that failed without enhancements but succeeded with them. This is a targeted metric (denominator is 5 failed questions, not all questions); the overall accuracy improvement from keywords is 3.96%.*

**Finding**: Keywords alone match any combined approach. Summaries add no value when keywords present.

---

## Repository Structure

```
context-structure-research/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── report/
│   ├── README.md                # Full research report
│   └── executive-summary.md     # One-page summary
├── docs/
│   ├── methodology.md           # Test methodology
│   ├── phase-2-plan.md                # Phase 2 comprehensive plan
│   └── prior-art-research.md    # Industry research
├── harness/
│   ├── questions.json           # 23 test questions
│   ├── run-test.sh              # Single test runner
│   ├── evaluator.py             # Response evaluator
│   └── *.sh                     # Various test scripts
├── results/
│   └── analysis/                # Analysis reports
└── soong-daystrom/              # Test corpus
    ├── _source-v4/, v5/, v6/    # Source content by version
    ├── flat-*, deep-*, etc.     # Structure variants
    └── *-v5.*/                  # Enhancement variants
```

---

## Reproduction

### Requirements

- Claude Code CLI
- Bash, Python 3.x, jq

### Quick Start

```bash
# Clone the repository
git clone https://github.com/davidmoneil/context-structure-research
cd context-structure-research

# Run a single test
./harness/run-test.sh --structure flat-v5 --question NAV-001

# Run full matrix
./harness/run-haiku-matrix-v5-no-monolith.sh

# Analyze results
python3 harness/evaluator.py results/v5/raw/haiku --output results/v5/analysis
```

### Test Corpus

The Soong-Daystrom Industries corpus is a synthetic knowledge base for a fictional robotics company:

- Employee directories and leadership bios
- Project documentation (ATLAS, ARIA, Prometheus, Hermes)
- Financial reports and governance documents
- Technical specifications and incident reports

| Version | Words | Files |
|---------|-------|-------|
| V4 | 120,000 | 80 |
| V5 | 302,000 | 121 |
| V6 | 622,561 | 277 |

---

## Why This Research Matters

Claude Code users face a practical question: *How should I organize my context files?*

Current guidance is limited to general best practices. No one has systematically tested what actually works. We filled that gap with controlled experiments.

### The "One Topic = One File" Principle

This emerged as a key architectural insight:

| Approach | Result |
|----------|--------|
| One file with multiple topics | Claude must read entire file to assess relevance |
| One topic spread across files | Claude may miss connections |
| **One topic per file** | Claude can assess relevance from filename alone |

**Why it works**: Claude Code's discovery process lists directory contents first. If each filename clearly indicates its topic, Claude can select relevant files without reading them all.

---

## Limitations

1. **Single model tested** — Results are for Claude 3.5 Haiku. Sonnet/Opus may differ.
2. **Synthetic corpus** — Real-world codebases may behave differently (Phase 2 planned).
3. **Prose content** — Code-heavy repos may need different strategies.
4. **Fixed question set** — 23 questions may not cover all query patterns.
5. **Single domain** — Corporate knowledge base; other domains untested.
6. **Partial credit scoring** — Non-exact matches scored by keyword coverage using an arbitrary formula (0.1 + 0.6 × coverage). Keywords are matched without context, so keywords appearing in refusal statements ("I couldn't find information about X") earn credit. This affects absolute accuracy numbers but not relative rankings, since all strategies use the same scoring.
7. **@-ref annotation untested** — R2.1–R2.4 strategies (which tested @-ref with various annotation levels) all exceeded the context window, producing 0% accuracy. This means the research question "Do @-ref annotations (descriptions, nesting) improve accuracy?" remains unanswered. A future test with fewer files or a smaller corpus would be needed to isolate the annotation variable.

---

## Future Work

### Phase 2: Code Repository Testing

The next phase will test these findings against real codebases:

- **Different content type**: Code vs prose
- **Function-level indexing**: Do code indexes help?
- **AST-based strategies**: Auto-generated function/class maps
- **Real-world validation**: Test on open-source repos

See [docs/phase-2-plan.md](docs/phase-2-plan.md) for the full plan.

---

## License

MIT License. See [LICENSE](LICENSE).

## Citation

If you use this research, please cite:

```
Context Structure Research: How File Organization Affects Claude Code Accuracy
https://github.com/davidmoneil/context-structure-research
January 2026
```

---

## Links

- [Full Report](report/README.md) — Complete methodology, results, and analysis
- [Executive Summary](report/executive-summary.md) — One-page overview
- [Methodology](docs/methodology.md) — Detailed test methodology

---

*Research conducted January-February 2026. 849 test runs, $36.74 total API cost.*
