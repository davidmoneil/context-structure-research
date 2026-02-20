---
title: Phase 2.1 Results Report
type: research
status: active
created: 2026-02-19
updated: 2026-02-19
tags:
  - context-structure-research
  - phase-2
  - results
---

# Phase 2.1 Results Report

## Executive Summary

Phase 2.1 tested 14 context-structuring strategies across 686 individual tests to determine how Claude best navigates large file collections. The central finding is clear: **lightweight index strategies dramatically outperform both raw file loading and no-context baselines**, while every strategy that loads all files into context fails catastrophically at scale.

The winning strategy, **I4 (summary table)**, achieves 70.0% accuracy at $0.04 per test by providing Claude with a one-sentence summary per file and letting tools handle the rest. This is both the most accurate and one of the most cost-efficient approaches tested. Loading full files into context -- the intuitive approach -- overflows the 200K token window for every dataset tested, producing 0% accuracy across five strategies.

These results establish a practical design principle for Claude Code configurations: **tell the model where to look, not what the files contain**. A well-crafted index plus tool access consistently beats brute-force context loading.

---

## Study Design

### Parameters

| Parameter | Value |
|-----------|-------|
| **Model** | Haiku (`claude-haiku-4-5-20251001`) |
| **Total tests** | 686 (14 strategies x 2 datasets x ~24 questions) |
| **Total cost** | $23.37 |
| **Execution mode** | `claude -p` headless, `--permission-mode bypassPermissions` |
| **Tools available** | Read, Grep, Glob |
| **Scoring** | Exact match (1.0), variant match (0.9), partial keyword credit (0.0-0.7) |

### Datasets

| Dataset | Files | Words | Questions | Character |
|---------|-------|-------|-----------|-----------|
| **soong-v5** | 120 | 302K | 23 | Well-structured codebase documentation |
| **obsidian** | 213 | 282K | 26 | Real-world messy knowledge base |

### Strategy Taxonomy

Strategies fall into four families based on how they provide context to the model.

**R-family (Reference/file loading)** -- Load files directly into context via `@` references.

| Strategy | Description |
|----------|-------------|
| **R1** | No context provided. Pure tool navigation -- the baseline. |
| **R2.1** | All files loaded via `@refs`, no annotation |
| **R2.2** | All files loaded + 1-sentence summary per ref |
| **R2.3** | All files loaded + keyword annotations per ref |
| **R2.4** | All files loaded + 2-sentence summary per ref |
| **R3** | Sub-indexes only (per-directory keyword listings, no full file loading) |
| **R4** | Top 15-30 key files loaded via `@refs` (selected by size + name heuristic) |

**I-family (Index only)** -- Provide a structured index; the model uses tools to read files on demand.

| Strategy | Description |
|----------|-------------|
| **I1** | Keyword index table (file -> 8 keywords), no files loaded |
| **I2** | Relationship graph (topic -> connected files), no files loaded |
| **I3** | Semantic groupings (15 topic clusters), no files loaded |
| **I4** | Summary table (file -> 1-sentence summary), no files loaded |

**C-family (Combined)** -- Merge elements from R and I families.

| Strategy | Description |
|----------|-------------|
| **C1** | All files + keyword index (overflow) |
| **C2** | R4 key files + I2 relationship graph |
| **C3** | Keyword index + directory sub-indexes |

### Question Classification

#### Question Types

| Type | Description | Example |
|------|-------------|---------|
| **Navigation** | Find a specific fact in a single file | "Who is the CEO?" |
| **Depth** | Deep understanding of a single file's detailed content | "What are the four tiers in Document Guard's validation model?" |
| **Cross-reference** | Connect information across multiple files | "Which department does Project Prometheus report to, and who leads it?" |
| **Synthesis** | Combine information into a novel conclusion | "What common principle connects Document Guard's tier model with the orchestration-detector's scoring?" |

#### Difficulty Levels

Difficulty is manually assigned based on:

| Level | Criteria | Example |
|-------|----------|---------|
| **Easy** | Single known fact, one source file, short exact answer | "Who is the CEO?" (answer: Dr. Maya Chen) |
| **Medium** | Requires locating 1-2 files, moderate detail extraction | "What decision was made in the October 2124 board meeting regarding AI safety?" |
| **Hard** | Multi-file reasoning, analysis/synthesis, or obscure specifics | "What common themes emerge across the security content and AI infrastructure projects?" |

#### Question Distribution

| Type | Easy | Medium | Hard | Total |
|------|------|--------|------|-------|
| navigation | 12 | 5 | 0 | 17 |
| depth | 1 | 5 | 7 | 13 |
| cross-reference | 1 | 10 | 3 | 14 |
| synthesis | 0 | 0 | 5 | 5 |
| **Total** | **14** | **20** | **15** | **49** |

Note: Synthesis questions only appear in the obsidian dataset (5 questions). All synthesis questions are rated hard.

### Experimental Controls

- A root `.claude/CLAUDE.md` (~1,500 chars) was loaded for all strategies as a constant baseline
- Each strategy folder contained a `data/` symlink to the identical source corpus
- Strategy-specific `CLAUDE.md` and `@refs` defined the initial context window
- All questions were identical across strategies within each dataset

---

## Results

### Overall Strategy Rankings

Ranked by average score across all 49 tests per strategy (both datasets combined).

|  Rank | Strategy                       | Family       | Avg Score | Exact Match | Cost/Correct Answer |
| ----: | ------------------------------ | ------------ | --------: | ----------: | ------------------: |
|     1 | **I4** (summary table)         | Index        |   71.2% |      18/49 |              $0.110 |
|     2 | **I1** (keyword index)         | Index        |   68.1% |      17/49 |              $0.118 |
|     3 | **I3** (semantic groups)       | Index        |   68.0% |      17/49 |              $0.119 |
|     4 | **R1** (no context)            | Reference    |   66.7% |      16/49 |              $0.115 |
|     5 | **R3** (sub-indexes)           | Reference    |   66.4% |      16/49 |              $0.122 |
|     6 | **C3** (keyword + sub-index)   | Combined     |   66.0% |      17/49 |              $0.130 |
|     7 | **I2** (relationship graph)    | Index        |   65.0% |      15/49 |              $0.193 |
|     8 | **R4** (key files)             | Reference    |   33.9% |      10/49 |              $0.410 |
|     9 | **C2** (key files + graph)     | Combined     |   33.8% |       9/49 |              $0.486 |
| 10-14 | **C1**, **R2.1**, **R2.2**, **R2.3**, **R2.4** | Ref/Combined |    0.0% |    0/49 |      N/A (overflow) |

**Five strategies scored 0.0%** due to context window overflow. These all attempted to load the full file corpus into the 200K token window.

### Strategy x Dataset Breakdown

Performance varies significantly between the well-structured (soong-v5) and messy (obsidian) datasets.

| Strategy          | soong-v5 (120 files) | obsidian (213 files) | Delta |
| ----------------- | -------------------: | -------------------: | ----: |
| **I4** |              72.8% |                69.8% |  -3.0 |
| **I1** |              69.2% |                67.1% |  -2.1 |
| **I3** |              73.9% |                62.7% | -11.2 |
| **R1** |              70.7% |                63.2% |  -7.5 |
| **R3** |              70.9% |                62.4% |  -8.4 |
| **C3** |              70.9% |                61.7% |  -9.1 |
| **I2** |              69.6% |                60.9% |  -8.8 |
| **R4** |              72.3% |      0.0% (overflow) |    -- |
| **C2** |              72.0% |      0.0% (overflow) |    -- |
| **R2.1-R2.4, C1** |               0.0% |                 0.0% |    -- |

Notable observations:
- **I4 is the most robust** -- only a 3-point drop from structured to messy data
- **R4 and C2 overflow on the larger dataset** -- selective file loading is dataset-size dependent
- **All working strategies degrade on obsidian**, but index strategies degrade less

### Token Usage and Efficiency

Per-test averages for strategies that produced results (non-overflow tests only).

| Strategy | Avg Total Tokens | Avg Turns | Avg Cost/Test | Efficiency Profile                    |
| -------- | ---------------: | --------: | ------------: | :------------------------------------ |
| **R1** |          135,573 |       6.0 | $       0.038 | Highest turns, cheapest per-test      |
| **R3** |           89,362 |       3.5 | $       0.040 | Low tokens, moderate turns            |
| **I4** |           87,490 |       3.1 | $       0.040 | Low tokens, few turns                 |
| **I1** |           91,472 |       3.3 | $       0.041 | Low tokens, few turns                 |
| **I3** |          103,688 |       3.9 | $       0.041 | Moderate tokens, more turns           |
| **C3** |           88,410 |       2.8 | $       0.045 | Low tokens, fewest turns              |
| **I2** |          116,258 |       3.2 | $       0.059 | Higher tokens, few turns              |
| **R4** |          160,498 |       1.0 | $       0.178 | Single turn, expensive (file loading) |
| **C2** |          169,780 |       1.0 | $       0.190 | Single turn, most expensive           |

**R1 is the cheapest per-test** because Haiku's input tokens are cheap and tool calls are lightweight -- but it requires **6 turns** of exploration compared to ~3 for index strategies. Index strategies trade a modest increase in upfront context tokens for halved turn counts.

### Wall Clock Timing

Average elapsed time per test, measured end-to-end (includes subprocess overhead).

| Strategy | Avg Time | Median Time | Min | Max | Avg Turns | Tests |
| -------- | -------: | ----------: | --: | --: | --------: | ----: |
| **R1** |    15.7s |       13.4s | 6.5s | 44.4s |       6.0 |    49 |
| **R3** |    15.7s |       11.9s | 4.7s | 148.5s |       3.5 |    49 |
| **I4** |    12.8s |       11.6s | 4.5s | 26.7s |       3.1 |    49 |
| **I1** |    13.1s |       12.9s | 4.0s | 39.8s |       3.3 |    49 |
| **I3** |    13.7s |       13.2s | 3.3s | 38.5s |       3.9 |    49 |
| **C3** |    12.1s |       11.0s | 5.5s | 22.8s |       2.8 |    49 |
| **I2** |    13.5s |       13.0s | 4.8s | 32.5s |       3.2 |    49 |
| **R4** |    12.6s |       11.5s | 7.4s | 23.9s |       1.0 |    23 |
| **C2** |    12.6s |       11.3s | 7.6s | 32.8s |       1.0 |    23 |

Timing reinforces the turn-count story: R1 (6 turns avg) takes the longest wall clock time despite being cheapest in dollar cost. Index strategies (I1, I3, I4) cluster around 10-15 seconds with ~3 turns. R4/C2 are fast (single turn) but only because they dump everything into context at once -- and this approach fails on larger datasets.

### Performance by Question Type

**Important**: The "All Strategies" column includes overflow strategies (R2.1-R2.4, C1, and R4/C2 on obsidian) which score 0%, significantly dragging down averages. The "Working Strategies" column excludes these to show actual capability.

| Question Type | All Strategies | Working Strategies | Tests (All) | Tests (Working) |
|---------------|---------------:|-------------------:|------------:|----------------:|
| **Navigation** | 52.9% | 90.5% | 238 | 139 |
| **Depth** | 32.6% | 58.7% | 182 | 101 |
| **Cross-Reference** | 32.1% | 55.2% | 196 | 114 |
| **Synthesis** | 23.1% | 46.1% | 70 | 35 |

When overflow noise is removed, navigation questions reach ~80%, showing Claude's strong file-finding ability with index guidance. Synthesis remains the hardest category even for working strategies.

### Performance by Difficulty

| Difficulty | All Strategies | Working Strategies | Tests (All) | Tests (Working) |
|------------|---------------:|-------------------:|------------:|----------------:|
| **Easy** | 53.6% | 92.1% | 196 | 114 |
| **Medium** | 34.8% | 62.4% | 280 | 156 |
| **Hard** | 29.4% | 52.0% | 210 | 119 |

Hard questions score roughly half as well as easy ones. This gradient holds across all strategies, suggesting it reflects genuine question difficulty rather than strategy-specific weaknesses.

### Strategy x Question Type Matrix (Working Strategies Only)

How each working strategy performs across question types.

| Strategy | Navigation | Depth | Cross-ref | Synthesis | Overall |
|----------|----------:|------:|----------:|----------:|--------:|
| **I4** | 94% | 62% | 58% | 55% | 71% |
| **I1** | 94% | 70% | 44% | 43% | 68% |
| **I3** | 94% | 52% | 60% | 45% | 68% |
| **R1** | 86% | 61% | 57% | 41% | 67% |
| **R3** | 86% | 55% | 58% | 50% | 66% |
| **C3** | 94% | 48% | 57% | 44% | 66% |
| **I2** | 88% | 58% | 52% | 44% | 65% |
| **R4** | 89% | 63% | 57% | N/A | 72% |
| **C2** | 89% | 66% | 55% | N/A | 72% |

Note: R4 and C2 only show soong-v5 results (obsidian overflowed). Synthesis questions only appear in the obsidian dataset.

### Cache Efficiency

How effectively each strategy uses Anthropic's prompt caching (higher cache read ratio = more tokens served from cache = cheaper).

| Strategy | Avg Cache Read | Avg Cache Create | Cache Hit Ratio | Avg Cost/Test |
| -------- | -------------: | ---------------: | --------------: | ------------: |
| **R1** |        119,928 |           14,335 |             89% | $       0.038 |
| **R3** |         67,376 |           20,962 |             76% | $       0.040 |
| **I4** |         63,329 |           23,156 |             73% | $       0.040 |
| **I1** |         67,201 |           23,199 |             74% | $       0.041 |
| **I3** |         80,452 |           21,947 |             79% | $       0.041 |
| **C3** |         60,104 |           27,262 |             69% | $       0.045 |
| **I2** |         78,532 |           36,503 |             68% | $       0.059 |
| **R4** |         22,551 |          136,936 |             14% | $       0.178 |
| **C2** |         22,440 |          146,359 |             13% | $       0.190 |

Strategies with higher cache hit ratios benefit from prompt caching -- the shared CLAUDE.md and strategy instructions get cached across questions in the same run. R1 has higher cache creation because each test starts fresh and builds context through tool calls.

### Hardest and Easiest Questions (Working Strategies)

**Top 5 Easiest** (highest average score across working strategies):

| Question | Avg Score | Tests | Type | Difficulty |
|----------|----------:|------:|------|------------|
| soong-v5/NAV-001 | 100% | 9 | navigation | easy |
| soong-v5/NAV-002 | 100% | 9 | navigation | easy |
| soong-v5/NAV-004 | 100% | 9 | navigation | easy |
| soong-v5/NAV-005 | 100% | 9 | navigation | easy |
| soong-v5/NAV-006 | 100% | 9 | navigation | medium |

**Top 5 Hardest** (lowest average score across working strategies):

| Question | Avg Score | Tests | Type | Difficulty |
|----------|----------:|------:|------|------------|
| soong-v5/NAV-008 | 0% | 9 | navigation | medium |
| obsidian/DEPTH-004 | 29% | 7 | depth | hard |
| soong-v5/XREF-006 | 30% | 9 | cross-reference | hard |
| soong-v5/XREF-002 | 36% | 9 | cross-reference | medium |
| obsidian/SYNTH-003 | 36% | 7 | synthesis | hard |

### Confidence Calibration

How well does the model's self-reported confidence correlate with actual accuracy?

| Confidence | Avg Score | Exact Match Rate | Tests |
|------------|----------:|-----------------:|------:|
| **High** | 69.8% | 35.4% | 362 |
| **Medium** | 50.9% | 31.8% | 22 |
| **Low** | 5.4% | 0.0% | 5 |

---

## Key Findings

### Finding 1: Index Strategies Dominate

**I4 (summary table) wins overall at 70.0%.** All index strategies (I1-I4, C3) cluster between 63-70%, forming a clear performance tier above other approaches.

The pattern is consistent: give Claude a compact map of the territory and let tools do the detail work. The index tells the model *where to look*; tools retrieve *what's there*. This division of labor outperforms both extremes -- loading everything (overflow) and loading nothing (more exploration turns needed).

### Finding 2: No Context is Surprisingly Competitive

**R1 (no context) scores 65.4%**, only 4.6 points behind the winning strategy. Claude's built-in tool navigation -- Glob for discovery, Read for content -- is remarkably effective on its own.

However, R1 requires **6 turns** on average versus ~3 for index strategies. Indexes don't dramatically improve accuracy; they **halve the work required to reach similar accuracy**. In production, this translates directly to faster responses and lower latency.

### Finding 3: Full File Loading Fails at Scale

Every strategy that loads all files into context (R2.1, R2.2, R2.3, R2.4, C1) overflows Haiku's 200K token window on **both datasets**, producing 0% accuracy across 245 tests. Even selective loading (R4, C2) overflows on the larger obsidian dataset.

This is the sharpest result in the study: **the intuitive approach of "give the model everything" is not just inefficient -- it is non-functional** for any real-world corpus of meaningful size.

### Finding 4: Indexes Help More on Messy Data

| Strategy | soong-v5 | obsidian | I4 Advantage over R1 |
|----------|----------|----------|---------------------|
| **I4** | 72.8% | 69.8% | -- |
| **R1** | 70.7% | 63.2% | -- |
| **Delta (I4 - R1)** | +2.1 | **+6.6** | 3x larger on messy data |

On well-structured data (soong-v5), indexes provide a modest 2.1-point boost. On messy real-world data (obsidian), the boost triples to 6.6 points. **Indexes matter most when the underlying data lacks clear organization** -- precisely the scenario where human users also struggle most.

### Finding 5: Summary Table Beats Keywords

**I4 (summary table) = 70.0% vs I1 (keyword index) = 67.0%**, at nearly identical token cost ($0.040 vs $0.041 per test).

One-sentence prose summaries give the model better semantic signal than keyword lists. A summary like "Configuration file for the authentication middleware" communicates purpose and context more effectively than "config, auth, middleware, settings, jwt, tokens, security, access."

### Finding 6: Relationship Graphs Underperform

**I2 (relationship graph) = 63.6% at $0.059/test vs I4 = 70.0% at $0.040/test.** The topic-to-file relationship graph is both less accurate and 48% more expensive per test.

The graph structure introduces noise -- too many connections, not enough signal per entry. Simpler, flatter indexes outperform richer structural representations. This aligns with the general pattern: **compact, direct context beats elaborate, indirect context**.

### Finding 7: Selective File Loading is Dataset-Size Dependent

R4 (top 15-30 key files) scores 72.3% on soong-v5 but overflows on obsidian. C2 (key files + relationship graph) shows the same pattern. **Any strategy that loads file contents is fundamentally constrained by the ratio of selected content to context window size.** As datasets grow, these strategies break.

Index-only strategies (I1-I4) scale gracefully because their context footprint grows linearly with file *count*, not file *content*.

### Finding 8: Synthesis Remains the Hardest Question Type

Even the best strategies struggle with synthesis questions (46.1% average for working strategies). Navigation questions (90.5%) are significantly easier. This suggests that current tool-based retrieval handles "find and read" well but struggles with "find, read, and combine" -- a known limitation of sequential tool use patterns.

---

## Phase 1 vs Phase 2 Comparison

Phase 1 established that context structure matters by testing flat, shallow, deep, and very-deep CLAUDE.md organizations on a single codebase. The key Phase 1 finding was that **Very-Deep structure was the efficiency winner at 497 tokens per 1% accuracy**, suggesting that hierarchical organization with clear navigation paths outperforms both minimal and exhaustive context.

Phase 2 extends this in three ways:

1. **Scale validation**: Phase 1 tested small contexts. Phase 2 confirms that the same principles hold at 120-213 file scale with 280-300K word corpora.
2. **Overflow boundary**: Phase 2 reveals that "stuffing everything into context" is not merely wasteful (as Phase 1 suggested) -- it is **physically impossible** beyond roughly 200K tokens. This transforms a soft optimization principle into a hard engineering constraint.
3. **Index as the scaling mechanism**: Phase 1's "Very-Deep" structure is conceptually an index -- it tells the model where things are without including all the content. Phase 2's I4 strategy formalizes this into a scalable pattern: one row per file, one sentence of context, tools for everything else.

The through-line across both phases: **the model needs orientation, not information**. Context should be a map, not the territory.

---

## Methodology Notes

### Execution Environment

- All tests executed via `claude -p` in headless mode
- `--permission-mode bypassPermissions` enabled unrestricted tool access
- Each strategy defined in its own folder with a `CLAUDE.md` and optional `@ref` files
- A `data/` symlink in each strategy folder pointed to the shared source corpus
- Root `.claude/CLAUDE.md` (~1,500 characters) loaded as a constant across all strategies

### Scoring Rubric

| Score | Criteria |
|------:|----------|
| 1.0 | Exact match with expected answer |
| 0.9 | Correct answer with minor variant (e.g., different path format) |
| 0.0-0.7 | Partial keyword credit based on overlap with expected answer |
| 0.0 | Incorrect, no answer, or overflow (context window exceeded) |

### Limitations

- **Single model**: All results are Haiku-specific. Strategy rankings may differ on Sonnet or Opus.
- **Two datasets**: While soong-v5 and obsidian represent structured and unstructured extremes, two datasets cannot capture all corpus characteristics.
- **Question design**: Questions were authored to cover navigation, depth, cross-reference, and synthesis categories, but may not represent all real-world query patterns.
- **Scoring subjectivity**: Partial credit (0.0-0.7 range) involves judgment calls on keyword overlap quality.

---

## Next Steps

| Phase | Focus | Goal |
|-------|-------|------|
| **2.2** | Model comparison | Test I4 (winning strategy) with Sonnet and local Ollama models to determine if strategy rankings are model-dependent |
| **2.3** | Failure analysis | Investigate question-level failures (e.g., NAV-008 at 0%, DEPTH-007 I4-specific gap) to understand where and why the best strategy still fails |
| **3.0** | Production application | Apply Phase 2 findings to real-world CLAUDE.md configurations for active projects |

### Phase 2.2 Design Note: Early Overflow Detection

Phase 2.1 spent an estimated ~$5.80 on overflow tests that could never produce results. In Phase 2.2 and beyond, the harness should implement **early overflow detection** to avoid wasting inference on strategies that will exceed the context window:

1. **Pre-flight token estimation**: Before running a test, estimate the total prompt size (CLAUDE.md + `@ref` files + question). If the estimate exceeds 80% of the model's context window, skip the test and record it as `overflow_predicted`.
2. **First-test sentinel**: For each (strategy, dataset) pair, run one test first. If it returns a "Prompt is too long" error or exit code 1, skip all remaining tests for that combination.
3. **Budget guard**: Set `--max-budget-usd` conservatively for strategies known to be near the context limit, so a single expensive failure doesn't consume the full test budget.

This is especially important for Phase 2.2's model comparison, since smaller models (Ollama local, GPT-4o-mini) may have smaller context windows and will overflow on strategies that worked for Haiku.

---

## Appendix: Cost Breakdown

| Category | Value |
|----------|------:|
| Total experiment cost | $23.37 |
| Total tests executed | 686 |
| Tests producing results (non-overflow) | 389 |
| Tests lost to overflow | 297 |
| Average cost per productive test | $0.060 |
| Cost of overflow tests | ~$0.00 (estimated, prompt-only charges) |

| Total wall clock time (productive tests) | 88.6 minutes |
| Average time per productive test | 13.7s |

---

*Report generated 2026-02-19. Phase 2.1 of the Context Structure Research project.*
*Model tested: claude-haiku-4-5-20251001 | Harness: context-structure-research v2*