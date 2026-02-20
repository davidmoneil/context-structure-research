# Phase 2: Context Strategy Testing — Comprehensive Plan

**Status**: In Progress (Steps 1-3 complete, ready for pilot run)
**Created**: 2026-02-19
**Updated**: 2026-02-19
**Supersedes**: `phase-2-codebase-testing.md`, `phase-2-indexing-strategies.md`

---

## What Changed from Original Phases 2-4

Original plan had 4 sequential phases. We restructured:

| Original | New | Reason |
|----------|-----|--------|
| Phase 2: Validate Phase 1 on code | Merged into Phase 3 (code track) | Code is just another content type, not a validation step |
| Phase 3: Indexing strategy experiments | **Phase 2** (this doc) | Promoted — this is the core research |
| Phase 4: Embeddings/external tools | **Phase 4** (separate) | Third-party tooling is fundamentally different |

Phase 2 now tests **our own index/reference strategies** against **two non-code datasets**. Code gets its own phase because it needs different index types.

---

## Research Questions

1. Do `@` reference strategies improve accuracy over baseline (no index)?
2. Do separately-built indexes (keyword maps, relationship graphs) improve accuracy?
3. Which strategy produces the best cost-per-correct-answer?
4. Do findings differ between structured (fake company) and heterogeneous (Obsidian) content?
5. What's the optimal index size — does bigger index = better, or is there a plateau/decline?
6. Do `@` ref annotations (keywords, summaries) help in CLAUDE.md the way they didn't in file structure? (Phase 1 retest)

---

## Test Execution Model

**All tests run via `claude -p` (Claude Code CLI headless mode).**

Each strategy gets its own folder containing:
- **Symlink to dataset** — no data duplication
- **CLAUDE.md** — strategy-specific context/references
- **Supporting artifacts** — index.md, relationships.md, etc. (referenced from CLAUDE.md via `@`)

```
strategies/
├── soong-v5/
│   ├── R1/
│   │   └── data -> ../../../corpus-versions/v5/shallow/
│   ├── R2.1/
│   │   ├── data -> ../../../corpus-versions/v5/shallow/
│   │   └── CLAUDE.md
│   ├── R2.2/
│   │   ├── data -> ../../../corpus-versions/v5/shallow/
│   │   └── CLAUDE.md
│   ├── I1/
│   │   ├── data -> ../../../corpus-versions/v5/shallow/
│   │   ├── CLAUDE.md        (references @index.md)
│   │   └── index.md
│   └── ...
├── obsidian/
│   ├── R1/
│   │   └── data -> ../../../test-datasets/obsidian/
│   └── ...
└── build-metrics.json
```

**Why `claude -p` and not API:** `@` references are a Claude Code feature. Testing via raw API would bypass the exact mechanism we're measuring. This tests real-world usage.

**Why symlinks:** One copy of each dataset. 17 strategy folders × 2 datasets = 34 folders, but zero data duplication.

---

## Strategy Categories

### Category 1: `@` Reference Enhancements

How you point Claude to content via CLAUDE.md. R2 has sub-variants that retest Phase 1 enhancement findings in a new context (CLAUDE.md annotations vs file-embedded metadata).

| ID | Strategy | CLAUDE.md Contains | LLM to Build? |
|----|----------|-------------------|----------------|
| R1 | **Baseline** | No CLAUDE.md at all | No |
| R2.1 | **Whole-file refs (plain)** | `@data/path/file.md` for every file | No |
| R2.2 | **Whole-file refs + 1-sentence summary** | `@data/path/file.md` — one-sentence summary | Yes (Haiku) |
| R2.3 | **Whole-file refs + keywords** | `@data/path/file.md` — extracted keywords | No (NLP) |
| R2.4 | **Whole-file refs + 2-sentence summary** | `@data/path/file.md` — two-sentence summary | Yes (Haiku) |
| R3 | **Hierarchical refs** | `@sub-indexes/topic.md` → files (nested) | No |
| R4 | **Selective refs** | `@` for ~10-15 key/entry-point files only | No (manual curation) |

**R2 sub-variants rationale:** Phase 1 tested keywords/summaries embedded in file names and file content. Phase 1 found keywords alone matched any combined approach, and enhancements hurt at scale (-4.6% at 622K). Phase 2 retests this with annotations in CLAUDE.md instead — different delivery mechanism may yield different results.

### Category 2: Built Index Systems

Separately generated index artifacts. CLAUDE.md references the index via `@`.

| ID | Strategy | Artifact | CLAUDE.md References | LLM to Build? |
|----|----------|----------|---------------------|----------------|
| I1 | **Keyword index** | `index.md` — file → keywords map | `@index.md` | No (NLP/regex) |
| I2 | **Relationship graph** | `relationships.md` — connections between files/topics | `@relationships.md` | Partial (LLM for semantic) |
| I3 | **Semantic grouping** | `capabilities.md` — files grouped by topic/feature | `@capabilities.md` | Yes (LLM) |
| I4 | **Summary index** | `summaries.md` — 1-2 sentence summary per file | `@summaries.md` | Yes (LLM) |

### Combinations

| ID | Combo | CLAUDE.md Contains | Rationale |
|----|-------|--------------------|-----------|
| C1 | R2.1 + I1 | Whole-file `@` refs + `@index.md` | Does keyword index add value over just refs? |
| C2 | R4 + I2 | Selective `@` refs + `@relationships.md` | Minimal refs + rich connections |
| C3 | R3 + I1 | Hierarchical `@` refs + `@index.md` | Structure + keywords |

**Total: 14 strategies**

---

## Datasets

### Dataset 1: Fake Company Corpus (Soong-Daystrom v5)

**Source**: `corpus-versions/v5/shallow/` (using shallow structure — Phase 1 best performer at this scale)
**Size**: ~302K words, 23 questions
**Ground truth**: `harness/questions.json` (NAV, XREF, DEPTH types)
**Advantage**: Known baselines from Phase 1 to compare against

### Dataset 2: Obsidian Vault Subset

**Source**: `test-datasets/obsidian/` (frozen snapshot, 2026-02-19)
**Size**: 213 files, ~282K words from `05-AI/` + `03-Professional/CISO-Expert/`
**Ground truth**: `test-datasets/obsidian/questions.json` (26 questions — NAV, XREF, DEPTH, SYNTH)
**Advantage**: Real-world heterogeneous data

---

## Test Matrix

14 strategies × 2 datasets × ~25 questions avg = **~700 tests**

| | Soong-Daystrom v5 (23 Qs) | Obsidian (26 Qs) |
|---|---|---|
| R1 (baseline) | x | x |
| R2.1 (plain refs) | x | x |
| R2.2 (refs + 1-sentence) | x | x |
| R2.3 (refs + keywords) | x | x |
| R2.4 (refs + 2-sentence) | x | x |
| R3 (hierarchical) | x | x |
| R4 (selective) | x | x |
| I1 (keyword index) | x | x |
| I2 (relationship graph) | x | x |
| I3 (semantic grouping) | x | x |
| I4 (summary index) | x | x |
| C1 (R2.1 + I1) | x | x |
| C2 (R4 + I2) | x | x |
| C3 (R3 + I1) | x | x |

**Estimated cost**: ~$42 at Haiku pricing (~$0.06/test)
**Estimated time**: 3-5 hours (with rate limiting)

---

## Data Capture Schema

Every test result captures a provider-agnostic set of fields. Missing fields are `null`, not omitted.

### Per-Test Record

```json
{
  "test_id": "phase2-R2.1-soong-v5-NAV-001",
  "metadata": {
    "phase": "2",
    "strategy": "R2.1",
    "dataset": "soong-v5",
    "question_id": "NAV-001",
    "question_type": "navigation",
    "model": "claude-haiku-4-5-20251001",
    "provider": "anthropic",
    "timestamp": "2026-02-20T14:30:00Z"
  },
  "accuracy": {
    "score": 1.0,
    "scoring_method": "evaluator_v2",
    "correct": true
  },
  "cost": {
    "input_tokens": 45000,
    "output_tokens": 1200,
    "cache_read_input_tokens": 38000,
    "cache_creation_input_tokens": 7000,
    "thinking_tokens": null,
    "total_cost_usd": 0.045
  },
  "performance": {
    "wall_clock_ms": 3200,
    "ttft_ms": null,
    "tokens_per_second": null,
    "prompt_eval_ms": null
  },
  "context": {
    "index_tokens": 2400,
    "total_context_tokens": 45000,
    "files_referenced": 3,
    "tool_calls": 0
  }
}
```

Note: TTFT/tokens-per-second may not be available from `claude -p` output. Capture what's available; null the rest. These fields exist for future API/local LLM testing.

### Per-Strategy Record (one-time, not per test)

```json
{
  "strategy_id": "I1",
  "dataset": "soong-v5",
  "index_build": {
    "method": "automated_nlp",
    "llm_calls": 0,
    "llm_cost_usd": 0,
    "build_time_seconds": 12,
    "index_size_bytes": 4200,
    "index_token_count": 2400
  },
  "maintenance": {
    "update_method": "full_rebuild",
    "estimated_update_cost": "same as build"
  }
}
```

---

## Execution Steps

### Step 1: Design Obsidian Vault Test Subset ✅ COMPLETE

- [x] Survey Obsidian vault structure, identify candidate folders
- [x] Select 200-400 file subset with good cross-referencing
- [x] Copy subset to `test-datasets/obsidian/` (snapshot, not live sync)
- [x] Write 26 ground truth questions with verified answers
- [x] Review questions for type balance (NAV:7, XREF:6, DEPTH:8, SYNTH:5)

### Step 2: Build Strategy Folders + Index Artifacts

Create the folder-per-strategy structure with symlinks and generate all artifacts.

**Non-LLM strategies (build first — free, deterministic):** ✅ COMPLETE
- [x] Create folder structure generator script (`harness/phase2/build-strategies.py`)
- [x] R1: Empty folder + data symlink (baseline)
- [x] R2.1: CLAUDE.md with plain `@data/path` for every file
- [x] R2.3: CLAUDE.md with `@data/path` + keywords (NLP extraction)
- [x] R3: CLAUDE.md + sub-index files with hierarchical `@` refs
- [x] R4: Curate key files, write selective CLAUDE.md
- [x] I1: Build keyword extraction script, generate `index.md`
- [x] C1: R2.1 + I1 combined
- [x] C3: R3 + I1 combined
- [x] Build metrics recorded to `strategies/build-metrics.json`

**LLM-dependent strategies (build second — costs money):**
- [ ] R2.2: CLAUDE.md with `@data/path` + 1-sentence summaries (Haiku)
- [ ] R2.4: CLAUDE.md with `@data/path` + 2-sentence summaries (Haiku)
- [ ] I2: Relationship graph generation (partial LLM)
- [ ] I3: Semantic grouping (LLM)
- [ ] I4: Summary index generation (LLM)

**Combinations (assemble from existing artifacts):**
- [ ] C1: Copy R2.1 CLAUDE.md + I1 index.md, merge CLAUDE.md refs
- [ ] C2: Copy R4 CLAUDE.md + I2 relationships.md, merge
- [ ] C3: Copy R3 structure + I1 index.md, merge

**Record build metrics** for every strategy (build-metrics.json).

### Step 3: Build the Test Runner ✅ COMPLETE

- [x] Bash runner script: `harness/phase2/run-tests.sh`
- [x] For each strategy × question: `cd` to folder, run `claude -p "question" --model haiku --output-format json`
- [x] Capture response text, token usage, cost from Claude JSON output
- [x] Write per-test JSON result to `results/phase2/raw/<strategy>/<dataset>/<qid>.json`
- [x] Support: dry-run, `--strategy`/`--dataset`/`--question` filters, `--resume`, `--max-tests`
- [x] Budget safety guard (`--max-budget-usd` per test, default $0.50)
- [x] Phase 2 evaluator: `harness/phase2/evaluate.py` (adapted from Phase 1 scoring)

### Step 4: Define Result Schema & Validation — Partially Complete

- [x] Finalize JSON schema (per-test records defined in `run-tests.sh`)
- [x] Result evaluator with reports (`evaluate.py` — markdown + JSON)
- [ ] Schema validation script (defer — not blocking execution)
- [ ] Phase 1 compatibility mapping for cross-phase comparison

### Step 5: Execute Test Matrix

- [ ] Dry run: R1 × soong-v5 × 3 questions (validate pipeline end-to-end)
- [ ] Full matrix: all 14 strategies × 2 datasets × all questions
- [ ] Monitor for errors, retry failures (max 3 retries)
- [ ] Verify build metrics recorded

### Step 6: Analyze Results

- [ ] Per-strategy accuracy breakdown
- [ ] Cost-per-correct-answer by strategy and dataset
- [ ] Strategy × question type heatmap
- [ ] Soong vs Obsidian comparison (do findings generalize?)
- [ ] R2.1 vs R2.2 vs R2.3 vs R2.4 comparison (do annotations help in CLAUDE.md?)
- [ ] Index size vs accuracy correlation
- [ ] Build cost analysis (which strategies are worth the build investment?)
- [ ] Statistical significance testing
- [ ] Generate Phase 2 report

---

## Phase 3: Code-Specific Strategies (After Phase 2)

Code gets its own phase because it needs fundamentally different indexes:

| ID | Strategy | Description |
|----|----------|-------------|
| CD1 | Baseline (no index) | Just the codebase, no index |
| CD2 | Architecture summary | High-level layer/pattern documentation |
| CD3 | Function signature index | tree-sitter extracted signatures with file:line |
| CD4 | Class/module map | Classes, inheritance, key methods |
| CD5 | Dependency graph | Import/require relationships |
| CD6 | Entry point map | Routes, handlers, CLI commands |
| CD7 | Semantic grouping | Files grouped by feature/capability |

**Datasets**: 1-2 real codebases (candidates: FastAPI, Express, or AIProjects itself)
**Questions**: Location, implementation, dependency, modification, cross-cutting

---

## Phase 4: External/Third-Party Tools (After Phase 3)

These require third-party dependencies and test a different question: "do existing tools beat our homegrown strategies?"

| Tool | What It Does |
|------|-------------|
| Aider repo-map | tree-sitter signatures + call graph |
| Embedding RAG | Vector similarity retrieval (nomic-embed, Voyage) |
| SCIP/LSP indexing | Language server definitions/references |
| Code-Index-MCP | MCP server wrapping code index |
| LLMLingua | Context compression (reduce tokens without losing signal) |

Test these against the **same datasets and questions** from Phases 2-3 for direct comparison.

---

## Success Criteria

Phase 2 is successful if we can answer:

1. **Which strategy category wins?** Reference enhancements, built indexes, or combinations?
2. **Does content type matter?** Same winner for structured (Soong) and heterogeneous (Obsidian)?
3. **What's the cost/benefit?** Is the best strategy worth its build cost?
4. **Where's the ceiling?** Can any index approach get us above Phase 1's 100% flat accuracy?
5. **Do CLAUDE.md annotations help?** Keywords/summaries in CLAUDE.md vs Phase 1's in-file approach.

---

## Resolved Decisions

1. ~~Which Obsidian folders?~~ → `05-AI/` + `03-Professional/CISO-Expert/` (213 files, 282K words)
2. ~~Question sets?~~ → 23 Soong + 26 Obsidian = 49 total
3. ~~Loading method?~~ → `claude -p` headless from strategy folders (not API)
4. Model: Haiku for Phase 2 (cheaper; Sonnet comparison is a future add-on)
5. Context budget: test at natural size first

---

## Known Considerations

1. **Root CLAUDE.md inheritance**: The project's `.claude/CLAUDE.md` (~1.5K chars) is loaded for ALL tests since Claude Code walks parent directories. This is constant across strategies and doesn't bias relative comparisons. R1 isn't truly "zero context" but reflects realistic usage.
2. **Context window limits**: R2.1 loads ALL files via `@` refs. For 300K+ word datasets, this may exceed Haiku's 200K token window. Claude Code may truncate. This is a valid finding about the strategy's real-world behavior.
3. **Tool use in R1**: With no `@` refs, R1 relies on Claude using Read/Glob tools to find answers. This tests a fundamentally different mode than preloaded strategies.
4. **Run from terminal**: The test runner must be executed from a regular terminal, NOT from inside a Claude Code session.

---

*Plan created: 2026-02-19*
*Updated: 2026-02-19 — Steps 1-3 complete, test runner + evaluator built, ready for pilot*
*Supersedes: phase-2-codebase-testing.md, phase-2-indexing-strategies.md*
