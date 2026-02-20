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
| **Total tests** | 1323 (14 strategies x 2 datasets x ~24 questions) |
| **Total cost** | $53.44 |
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
|     1 | **I4** (summary table)         | Index        |   73.2% |      19/49 |              $0.104 |
|     2 | **I4-grep2b**                  |              |   72.9% |      18/49 |              $0.129 |
|     3 | **I4-grep**                    |              |   72.8% |      18/49 |              $0.130 |
|     4 | **I4-template**                |              |   72.2% |      18/49 |              $0.117 |
|     5 | **I4-kw2**                     |              |   71.4% |      18/49 |              $0.117 |
|     6 | **I4-kw10**                    |              |   70.9% |      18/49 |              $0.121 |
|     7 | **I4-kw7**                     |              |   70.6% |      18/49 |              $0.120 |
|     8 | **I4-sonnet-verify**           |              |   70.5% |      17/49 |              $0.165 |
|     9 | **I1** (keyword index)         | Index        |   70.1% |      18/49 |              $0.112 |
|    10 | **I3** (semantic groups)       | Index        |   70.0% |      18/49 |              $0.112 |
|    11 | **I4-grep2a**                  |              |   69.9% |      17/49 |              $0.137 |
|    12 | **R1** (no context)            | Reference    |   68.8% |      17/49 |              $0.108 |
|    13 | **I4-sonnet**                  |              |   68.6% |      17/49 |              $0.140 |
|    14 | **R3** (sub-indexes)           | Reference    |   68.4% |      17/49 |              $0.114 |
|    15 | **I4-geminiflash**             |              |   68.2% |      17/49 |              $0.127 |
|    16 | **C3** (keyword + sub-index)   | Combined     |   68.0% |      18/49 |              $0.123 |
|    17 | **I2** (relationship graph)    | Index        |   67.0% |      16/49 |              $0.181 |
|    18 | **I4-gpt4omini**               |              |   65.5% |      16/49 |              $0.151 |
|    19 | **I4-qwen7b**                  |              |   65.4% |      17/49 |              $0.143 |
|    20 | **I4-qwen32b**                 |              |   62.5% |      17/49 |              $0.138 |
|    21 | **R4** (key files)             | Reference    |   36.0% |      11/49 |              $0.373 |
|    22 | **C2** (key files + graph)     | Combined     |   35.8% |      10/49 |              $0.437 |
| 10-14 | **C1**, **R2.1**, **R2.2**, **R2.3**, **R2.4** | Ref/Combined |    0.0% |    0/49 |      N/A (overflow) |

**Five strategies scored 0.0%** due to context window overflow. These all attempted to load the full file corpus into the 200K token window.

### Strategy x Dataset Breakdown

Performance varies significantly between the well-structured (soong-v5) and messy (obsidian) datasets.

| Strategy          | soong-v5 (120 files) | obsidian (213 files) | Delta |
| ----------------- | -------------------: | -------------------: | ----: |
| **I4** |              77.1% |                69.8% |  -7.3 |
| **I4-grep2b** |              74.9% |                71.1% |  -3.8 |
| **I4-grep** |              70.0% |                75.2% |  +5.3 |
| **I4-template** |              75.4% |                69.5% |  -5.9 |
| **I4-kw2** |              76.3% |                67.0% |  -9.4 |
| **I4-kw10** |              73.8% |                68.4% |  -5.4 |
| **I4-kw7** |              75.2% |                66.5% |  -8.6 |
| **I4-sonnet-verify** |              74.7% |                66.8% |  -7.9 |
| **I1** |              73.5% |                67.1% |  -6.4 |
| **I3** |              78.3% |                62.7% | -15.5 |
| **I4-grep2a** |              70.1% |                69.7% |  -0.4 |
| **R1** |              75.1% |                63.2% | -11.9 |
| **I4-sonnet** |              72.0% |                65.6% |  -6.4 |
| **R3** |              75.2% |                62.4% | -12.8 |
| **I4-geminiflash** |              73.6% |                63.5% | -10.2 |
| **C3** |              75.2% |                61.7% | -13.5 |
| **I2** |              74.0% |                60.9% | -13.1 |
| **I4-gpt4omini** |              67.6% |                63.7% |  -3.8 |
| **I4-qwen7b** |              73.1% |                58.7% | -14.5 |
| **I4-qwen32b** |              71.6% |                54.5% | -17.1 |
| **R4** |              76.6% |      0.0% (overflow) |    -- |
| **C2** |              76.3% |      0.0% (overflow) |    -- |
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
| **I4-template** |           86,274 |       3.0 | $       0.043 |                                       |
| **I4-kw2** |           95,930 |       3.3 | $       0.043 |                                       |
| **I4-geminiflash** |           93,131 |       3.2 | $       0.044 |                                       |
| **I4-kw7** |           94,117 |       3.1 | $       0.044 |                                       |
| **I4-kw10** |           91,917 |       3.0 | $       0.045 |                                       |
| **C3** |           88,410 |       2.8 | $       0.045 | Low tokens, fewest turns              |
| **I4-grep2b** |          145,918 |       5.2 | $       0.047 |                                       |
| **I4-grep2a** |          151,010 |       4.9 | $       0.048 |                                       |
| **I4-qwen32b** |           85,313 |       2.2 | $       0.048 |                                       |
| **I4-grep** |          139,658 |       4.8 | $       0.048 |                                       |
| **I4-sonnet** |           83,269 |       1.9 | $       0.049 |                                       |
| **I4-gpt4omini** |           84,982 |       2.0 | $       0.049 |                                       |
| **I4-qwen7b** |           97,704 |       2.8 | $       0.050 |                                       |
| **I4-sonnet-verify** |          112,344 |       2.9 | $       0.057 |                                       |
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
| **I4-template** |    12.5s |       11.7s | 4.3s | 24.6s |       3.0 |    49 |
| **I4-kw2** |    13.1s |       11.7s | 4.1s | 39.2s |       3.3 |    49 |
| **I4-geminiflash** |    13.2s |       12.2s | 5.0s | 30.5s |       3.2 |    49 |
| **I4-kw7** |    12.8s |       11.8s | 4.3s | 26.9s |       3.1 |    49 |
| **I4-kw10** |    12.6s |       11.1s | 3.8s | 26.8s |       3.0 |    49 |
| **C3** |    12.1s |       11.0s | 5.5s | 22.8s |       2.8 |    49 |
| **I4-grep2b** |    20.5s |       16.9s | 8.4s | 45.6s |       5.2 |    49 |
| **I4-grep2a** |    20.2s |       16.9s | 5.5s | 49.8s |       4.9 |    49 |
| **I4-qwen32b** |    13.0s |       10.9s | 5.0s | 38.0s |       2.2 |    49 |
| **I4-grep** |    16.8s |       15.7s | 6.1s | 39.8s |       4.8 |    49 |
| **I4-sonnet** |    13.1s |       12.0s | 5.6s | 26.8s |       1.9 |    49 |
| **I4-gpt4omini** |    16.9s |       12.3s | 5.2s | 146.9s |       2.0 |    49 |
| **I4-qwen7b** |    13.9s |       13.7s | 5.6s | 34.9s |       2.8 |    49 |
| **I4-sonnet-verify** |    15.1s |       13.2s | 5.9s | 33.5s |       2.9 |    49 |
| **I2** |    13.5s |       13.0s | 4.8s | 32.5s |       3.2 |    49 |
| **R4** |    12.6s |       11.5s | 7.4s | 23.9s |       1.0 |    23 |
| **C2** |    12.6s |       11.3s | 7.6s | 32.8s |       1.0 |    23 |

Timing reinforces the turn-count story: R1 (6 turns avg) takes the longest wall clock time despite being cheapest in dollar cost. Index strategies (I1, I3, I4) cluster around 10-15 seconds with ~3 turns. R4/C2 are fast (single turn) but only because they dump everything into context at once -- and this approach fails on larger datasets.

### Performance by Question Type

**Important**: The "All Strategies" column includes overflow strategies (R2.1-R2.4, C1, and R4/C2 on obsidian) which score 0%, significantly dragging down averages. The "Working Strategies" column excludes these to show actual capability.

| Question Type | All Strategies | Working Strategies | Tests (All) | Tests (Working) |
|---------------|---------------:|-------------------:|------------:|----------------:|
| **Navigation** | 76.6% | 97.7% | 459 | 360 |
| **Depth** | 44.2% | 57.4% | 351 | 270 |
| **Cross-Reference** | 42.9% | 54.8% | 378 | 296 |
| **Synthesis** | 34.1% | 46.0% | 135 | 100 |

When overflow noise is removed, navigation questions reach ~80%, showing Claude's strong file-finding ability with index guidance. Synthesis remains the hardest category even for working strategies.

### Performance by Difficulty

| Difficulty | All Strategies | Working Strategies | Tests (All) | Tests (Working) |
|------------|---------------:|-------------------:|------------:|----------------:|
| **Easy** | 72.9% | 93.1% | 378 | 296 |
| **Medium** | 51.4% | 66.7% | 540 | 416 |
| **Hard** | 40.0% | 51.6% | 405 | 314 |

Hard questions score roughly half as well as easy ones. This gradient holds across all strategies, suggesting it reflects genuine question difficulty rather than strategy-specific weaknesses.

### Strategy x Question Type Matrix (Working Strategies Only)

How each working strategy performs across question types.

| Strategy | Navigation | Depth | Cross-ref | Synthesis | Overall |
|----------|----------:|------:|----------:|----------:|--------:|
| **I4** | 100% | 62% | 58% | 55% | 73% |
| **I4-grep2b** | 99% | 63% | 58% | 52% | 73% |
| **I4-grep** | 99% | 63% | 55% | 57% | 73% |
| **I4-template** | 99% | 62% | 58% | 46% | 72% |
| **I4-kw2** | 100% | 60% | 57% | 42% | 71% |
| **I4-kw10** | 99% | 57% | 58% | 46% | 71% |
| **I4-kw7** | 99% | 55% | 57% | 51% | 71% |
| **I4-sonnet-verify** | 99% | 63% | 52% | 45% | 71% |
| **I1** | 99% | 70% | 44% | 43% | 70% |
| **I3** | 99% | 52% | 60% | 45% | 70% |
| **I4-grep2a** | 94% | 60% | 56% | 56% | 70% |
| **R1** | 92% | 61% | 57% | 41% | 69% |
| **I4-sonnet** | 99% | 56% | 52% | 43% | 69% |
| **R3** | 92% | 55% | 58% | 50% | 68% |
| **I4-geminiflash** | 94% | 55% | 57% | 47% | 68% |
| **C3** | 99% | 48% | 57% | 44% | 68% |
| **I2** | 94% | 58% | 52% | 44% | 67% |
| **I4-gpt4omini** | 94% | 54% | 52% | 39% | 66% |
| **I4-qwen7b** | 99% | 54% | 45% | 38% | 65% |
| **I4-qwen32b** | 100% | 37% | 51% | 35% | 63% |
| **R4** | 99% | 63% | 57% | N/A | 77% |
| **C2** | 99% | 66% | 55% | N/A | 76% |

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
| **I4-template** |         59,581 |           25,624 |             70% | $       0.043 |
| **I4-kw2** |         70,254 |           24,604 |             74% | $       0.043 |
| **I4-geminiflash** |         66,233 |           25,805 |             72% | $       0.044 |
| **I4-kw7** |         67,336 |           25,713 |             72% | $       0.044 |
| **I4-kw10** |         64,446 |           26,456 |             71% | $       0.045 |
| **C3** |         60,104 |           27,262 |             69% | $       0.045 |
| **I4-grep2b** |        125,299 |           19,229 |             87% | $       0.047 |
| **I4-grep2a** |        127,103 |           22,377 |             85% | $       0.048 |
| **I4-qwen32b** |         54,282 |           29,911 |             64% | $       0.048 |
| **I4-grep** |        114,333 |           23,864 |             83% | $       0.048 |
| **I4-sonnet** |         51,556 |           30,702 |             63% | $       0.049 |
| **I4-gpt4omini** |         52,703 |           30,842 |             63% | $       0.049 |
| **I4-qwen7b** |         66,642 |           29,831 |             69% | $       0.050 |
| **I4-sonnet-verify** |         76,115 |           35,047 |             68% | $       0.057 |
| **I2** |         78,532 |           36,503 |             68% | $       0.059 |
| **R4** |         22,551 |          136,936 |             14% | $       0.178 |
| **C2** |         22,440 |          146,359 |             13% | $       0.190 |

Strategies with higher cache hit ratios benefit from prompt caching -- the shared CLAUDE.md and strategy instructions get cached across questions in the same run. R1 has higher cache creation because each test starts fresh and builds context through tool calls.

### Hardest and Easiest Questions (Working Strategies)

**Top 5 Easiest** (highest average score across working strategies):

| Question | Avg Score | Tests | Type | Difficulty |
|----------|----------:|------:|------|------------|
| soong-v5/NAV-001 | 100% | 22 | navigation | easy |
| soong-v5/NAV-002 | 100% | 22 | navigation | easy |
| soong-v5/NAV-004 | 100% | 22 | navigation | easy |
| soong-v5/NAV-008 | 100% | 22 | navigation | medium |
| soong-v5/NAV-009 | 100% | 22 | navigation | easy |

**Top 5 Hardest** (lowest average score across working strategies):

| Question | Avg Score | Tests | Type | Difficulty |
|----------|----------:|------:|------|------------|
| soong-v5/XREF-002 | 17% | 22 | cross-reference | medium |
| soong-v5/XREF-006 | 27% | 22 | cross-reference | hard |
| obsidian/SYNTH-005 | 38% | 20 | synthesis | hard |
| soong-v5/DEPTH-005 | 39% | 22 | depth | hard |
| obsidian/SYNTH-003 | 41% | 20 | synthesis | hard |

### Confidence Calibration

How well does the model's self-reported confidence correlate with actual accuracy?

| Confidence | Avg Score | Exact Match Rate | Tests |
|------------|----------:|-----------------:|------:|
| **High** | 72.4% | 37.8% | 949 |
| **Medium** | 47.2% | 19.6% | 51 |
| **Low** | 16.1% | 3.8% | 26 |

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

Even the best strategies struggle with synthesis questions (46.0% average for working strategies). Navigation questions (97.7%) are significantly easier. This suggests that current tool-based retrieval handles "find and read" well but struggles with "find, read, and combine" -- a known limitation of sequential tool use patterns.

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
| Total experiment cost | $53.44 |
| Total tests executed | 1323 |
| Tests producing results (non-overflow) | 1026 |
| Tests lost to overflow | 297 |
| Average cost per productive test | $0.052 |
| Cost of overflow tests | ~$0.00 (estimated, prompt-only charges) |

| Total wall clock time (productive tests) | 246.8 minutes |
| Average time per productive test | 14.4s |

---

*Report generated 2026-02-19. Phase 2.1 of the Context Structure Research project.*
*Model tested: claude-haiku-4-5-20251001 | Harness: context-structure-research v2*