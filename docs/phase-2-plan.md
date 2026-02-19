# Phase 2: Context Strategy Testing — Comprehensive Plan

**Status**: Planning
**Created**: 2026-02-19
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

---

## Strategy Categories

### Category 1: `@` Reference Enhancements

How you point Claude to content. No separately-built artifacts — just CLAUDE.md configuration.

| ID | Strategy | Description | LLM to Build? |
|----|----------|-------------|----------------|
| R1 | **Baseline (no refs)** | No CLAUDE.md, no `@` references. Claude gets the files and that's it. | No |
| R2 | **Whole-file `@` refs** | CLAUDE.md with `@path/to/file.md` for every file | No |
| R3 | **Hierarchical `@` refs** | Nested `@` references mirroring directory structure (CLAUDE.md → sub-index → files) | No |
| R4 | **Selective `@` refs** | CLAUDE.md references only key/entry-point files, not everything | No |

### Category 2: Built Index Systems

Separately generated index artifacts that live alongside the content.

| ID | Strategy | Description | LLM to Build? |
|----|----------|-------------|----------------|
| I1 | **Keyword index** | `index.md` mapping each file to extracted keywords | No (NLP/regex) |
| I2 | **Relationship graph** | `relationships.csv` or `.md` mapping connections between files/topics | Partial (LLM for semantic relationships) |
| I3 | **Semantic grouping** | Files grouped by topic/feature, not by directory | Partial (LLM for grouping) |
| I4 | **Summary index** | 1-2 sentence summary per file (Phase 1 showed this hurts at scale — retest?) | Yes |

### Combinations

| ID | Combo | Rationale |
|----|-------|-----------|
| C1 | R2 + I1 | Whole-file refs + keyword index (does the index add value over just refs?) |
| C2 | R4 + I2 | Selective refs + relationship graph (minimal refs + rich connections) |
| C3 | R3 + I1 | Hierarchical refs + keyword index |

---

## Datasets

### Dataset 1: Fake Company Corpus (Soong-Daystrom)

**Source**: `corpus-versions/` (existing from Phase 1)
**Size**: ~120K words (v4), ~302K words (v5), ~622K words (v6)
**Ground truth**: `harness/questions.json` (23 questions — NAV, XREF, DEPTH types)
**Advantage**: Known ground truth, existing baselines to compare against

For Phase 2, we test strategies against the **v5 corpus** (302K words) — large enough to stress-test but not so large that everything degrades.

### Dataset 2: Obsidian Vault Subset

**Source**: `/mnt/synology_nas/Obsidian/Master/` (David's real knowledge base)
**Characteristics**: Heterogeneous — daily notes, project docs, research, reference material, personal notes
**Ground truth**: Must be created (20-30 questions with verified answers)
**Advantage**: Real-world messy data, not synthetic

**Subset selection criteria**:
- Pick 2-3 well-populated folders with enough cross-referencing (e.g., AI research, projects, professional)
- Target ~200-400 files (enough to stress context, not so many that setup is unwieldy)
- Must include some cross-topic connections that require the model to synthesize

**Question types to write**:
- Navigation: "What folder/file contains info about X?"
- Cross-reference: "What's the relationship between X and Y?"
- Depth: "What are the specific details of X?"
- Synthesis: "What themes connect these topics?"

---

## Data Capture Schema

Every test result captures a provider-agnostic set of fields. Missing fields are `null`, not omitted.

### Per-Test Record

```json
{
  "test_id": "phase2-R2-soong-v5-NAV-001",
  "metadata": {
    "phase": "2",
    "strategy": "R2",
    "dataset": "soong-v5",
    "question_id": "NAV-001",
    "question_type": "navigation",
    "model": "claude-3.5-haiku",
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
    "ttft_ms": 850,
    "tokens_per_second": 42.3,
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

## Test Matrix

### Phase 2 Core Matrix

Strategies × Datasets = test cells. Each cell runs the full question set.

| | Soong-Daystrom v5 (23 questions) | Obsidian Subset (~25 questions) |
|---|---|---|
| R1 (baseline) | x | x |
| R2 (whole-file refs) | x | x |
| R3 (hierarchical refs) | x | x |
| R4 (selective refs) | x | x |
| I1 (keyword index) | x | x |
| I2 (relationship graph) | x | x |
| I3 (semantic grouping) | x | x |
| I4 (summary index) | x | x |
| C1 (R2 + I1) | x | x |
| C2 (R4 + I2) | x | x |
| C3 (R3 + I1) | x | x |

**11 strategies × 2 datasets × ~24 questions = ~528 tests**
**Estimated cost**: ~$32 at Haiku pricing (based on Phase 1 avg of $0.06/test)

### Loading Methods

Phase 1 tested `adddir` vs `classic`. For Phase 2, standardize on one method (recommend `adddir` — it's what real users do) unless there's reason to test both.

---

## Execution Steps

### Step 1: Design Obsidian Vault Test Subset

- [ ] Survey Obsidian vault structure, identify candidate folders
- [ ] Select 200-400 file subset with good cross-referencing
- [ ] Copy subset to `test-datasets/obsidian/` (snapshot, not live sync)
- [ ] Write 20-30 ground truth questions with verified answers
- [ ] Review questions for type balance (nav, xref, depth, synthesis)

### Step 2: Build Strategy Index Artifacts

For each strategy, create the index/CLAUDE.md for **both** datasets:

- [ ] R1: No artifacts needed (baseline)
- [ ] R2: Generate CLAUDE.md with whole-file `@` references
- [ ] R3: Generate CLAUDE.md + sub-indexes with hierarchical `@` references
- [ ] R4: Identify key files, write selective CLAUDE.md
- [ ] I1: Build keyword extraction script, generate `index.md` per dataset
- [ ] I2: Build relationship extractor, generate `relationships.md` per dataset
- [ ] I3: Build semantic grouper, generate `capabilities.md` per dataset
- [ ] I4: Build summary generator, generate `summaries.md` per dataset
- [ ] C1-C3: Combine relevant artifacts

Record build cost/time for each strategy (per-strategy record above).

### Step 3: Adapt the Harness

- [ ] New Python harness (bash won't scale for this matrix)
- [ ] YAML config for test matrix (strategy × dataset × model × questions)
- [ ] Provider-agnostic runner with streaming support (TTFT measurement)
- [ ] Reuse `evaluator.py` scoring logic
- [ ] Output format matching the per-test schema above
- [ ] Support for CLAUDE.md injection per strategy

### Step 4: Define Result Schema & Validation

- [ ] Finalize JSON schema (per-test and per-strategy records)
- [ ] Schema validation script (ensure no test result is missing required fields)
- [ ] Dashboard/report generator that reads the new schema
- [ ] Compatibility layer: can still compare Phase 2 results against Phase 1 baselines

### Step 5: Execute Test Matrix

- [ ] Dry run: 1 strategy × 1 dataset × 3 questions (validate harness works)
- [ ] Full matrix: all 11 strategies × 2 datasets × all questions
- [ ] Monitor for errors, retry failures
- [ ] Record per-strategy build metrics

### Step 6: Analyze Results

- [ ] Per-strategy accuracy breakdown
- [ ] Cost-per-correct-answer by strategy and dataset
- [ ] Strategy × question type heatmap
- [ ] Soong vs Obsidian comparison (do findings generalize?)
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

---

## Open Decisions (To Resolve During Execution)

1. Which Obsidian folders to include in the test subset?
2. Exact question sets for Obsidian dataset
3. Loading method: `adddir` only, or test both?
4. Model: Haiku only for Phase 2, or also test Sonnet?
5. Context budget: test at natural size, or also test with artificial budget constraints?

---

*Plan created: 2026-02-19*
*Supersedes: phase-2-codebase-testing.md, phase-2-indexing-strategies.md*
