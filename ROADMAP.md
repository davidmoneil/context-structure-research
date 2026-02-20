# Context Structure Research - Roadmap

**Last Updated**: 2026-02-20

---

## Current State

Phase 1 complete (849 tests). Phase 2.1 complete (686 tests). Phase 2.2 (I4 multi-model variants) in progress.

---

## Phase Overview

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 1**: File Structure | How file organization affects LLM accuracy | **Complete** |
| **Phase 2**: Context Strategies | `@` reference approaches + built index systems | **Phase 2.1 Complete, 2.2 In Progress** |
| **Phase 3**: Code Strategies | Code-specific indexes (signatures, dependency graphs) | Designed |
| **Phase 4**: External Tools | Third-party tooling (Aider, embeddings, SCIP) | Future |

**Comprehensive plan**: `docs/phase-2-plan.md`

---

## Phase 1: Complete

- [x] V4 corpus (120K words) — 230 tests
- [x] V5 corpus (302K words) — 191 tests
- [x] V5 enhancements (V5.1-V5.5) — 60 tests
- [x] V5.5 matrix — 92 tests
- [x] V6 matrix — 184 tests
- [x] V6 extended — 92 tests
- [x] Cost-effectiveness analysis ($36.74 total)
- [x] Final report and executive summary
- [ ] Statistical significance testing
- [ ] GitHub repo public release
- [ ] Blog post publish to cisoexpert.com

---

## Phase 2: Context Strategy Testing

### Execution Steps

1. [x] Design Obsidian vault test subset + ground truth questions
2. [x] Build strategy index artifacts for both datasets
3. [x] Build new Python harness (YAML config, streaming, provider-agnostic)
4. [x] Define result schema & validation
5. [x] Execute test matrix (686 tests, $23.37 actual cost)
6. [x] Analyze results — enhanced report generated
7. [ ] Phase 2.2: I4 multi-model variant testing (in progress)
8. [ ] Publish Phase 2 report

### Strategies

**References**: R1 (baseline), R2 (whole-file @), R3 (hierarchical @), R4 (selective @)
**Indexes**: I1 (keywords), I2 (relationship graph), I3 (semantic grouping), I4 (summaries)
**Combos**: C1 (R2+I1), C2 (R4+I2), C3 (R3+I1)

### Datasets

1. Soong-Daystrom corpus v5 (302K words, 23 existing questions)
2. Obsidian vault subset (~200-400 files, ~25 new questions)

---

## Phase 3: Code-Specific Strategies

- [ ] Select 1-2 test codebases
- [ ] Build code indexes (architecture, signatures, class maps, dependency graphs, entry points)
- [ ] Write code-specific ground truth questions
- [ ] Execute code strategy matrix
- [ ] Compare against Phase 2 findings

---

## Phase 4: External/Third-Party Tools

- [ ] Aider repo-map
- [ ] Embedding RAG (nomic-embed, all-minilm)
- [ ] SCIP/LSP indexing
- [ ] Code-Index-MCP
- [ ] LLMLingua context compression
- [ ] Compare against homegrown strategies from Phases 2-3

---

## Links

- **GitHub**: https://github.com/davidmoneil/context-structure-research
- **Report**: `report/README.md`
- **Phase 2 Plan**: `docs/phase-2-plan.md`
- **AIProjects context**: `.claude/context/projects/context-structure-research.md`
- **Project Loom** (consumer): `.claude/context/projects/loom.md`
