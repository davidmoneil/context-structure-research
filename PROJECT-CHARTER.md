# Context Structure Research - Project Charter

**Created**: 2026-01-30
**Owner**: David Moneil
**Status**: Phase 1 Complete, Phase 2 Proposed

---

## Mission Statement

Determine how file organization affects Claude Code's ability to accurately answer questions when using the `@` reference system, and provide actionable guidance for developers to optimize their project structure.

---

## Phase 1: Synthetic Corpus Testing (COMPLETE)

### Objective
Test Claude Code's accuracy across different directory structures using a controlled, synthetic knowledge base.

### What We Built
- **Soong-Daystrom Industries corpus**: Fictional robotics company documentation
- **Three scales**: V4 (120K words), V5 (302K words), V6 (622K words)
- **Five structure types**: flat, shallow, deep, very-deep, monolith
- **Six enhancement strategies**: summaries (2-sent, 5-sent), keywords, combinations

### What We Tested
- 757 total test configurations
- 23 questions across 3 types (navigation, cross-reference, depth)
- 2 loading methods (classic cd, --add-dir flag)
- Claude 3.5 Haiku model

### Key Findings

1. **Flat structure wins**: 97-100% accuracy across all scales
2. **Enhancement indexes hurt at scale**: -4.6% accuracy at 622K words
3. **Deep nesting degrades gracefully**: ~95% even at 622K words
4. **Loading method doesn't matter**: Classic vs add-dir shows no significant difference

### Data Anomalies
- Deep structure improved from V5 (92%) to V6 (95%) - counterintuitive
- Very-deep and shallow not tested at V6 scale (gap in data)

### Deliverables
- [x] Raw test results (`results/`)
- [x] Cross-variant analysis (`results/cross-variant-comparison.md`)
- [x] Final report (`report/README.md`)
- [x] Blog draft (Obsidian)

---

## Phase 2: Real Codebase Testing (PROPOSED)

### Objective
Validate Phase 1 findings on actual codebases and test code-specific indexing strategies.

### Research Questions

1. **Do prose findings apply to code?**
   - Code has different structure (imports, classes, functions)
   - Navigation patterns differ (call hierarchies vs topic relationships)

2. **What indexing strategies help for code?**
   - Function/class name indexes
   - Import/dependency maps
   - Call hierarchy summaries
   - File purpose descriptions

3. **What's the practical limit?**
   - At what codebase size does accuracy degrade significantly?
   - Can intelligent indexing extend that limit?

### Proposed Test Codebases

| Repo | Size | Language | Why |
|------|------|----------|-----|
| TBD - small | ~50K LOC | Python/TypeScript | Baseline |
| TBD - medium | ~200K LOC | Mixed | Scale test |
| TBD - large | ~500K+ LOC | Mixed | Stress test |

Candidates:
- Popular open-source projects with good documentation
- Projects with clear architecture (easier to create ground-truth questions)
- Mix of languages to test generalization

### Proposed Indexing Strategies

| Strategy | Description |
|----------|-------------|
| **Baseline** | Standard CLAUDE.md only |
| **Function Index** | List of all function names with file locations |
| **Class Map** | Class hierarchy with key methods |
| **Dependency Graph** | Import relationships between files |
| **Architecture Summary** | High-level component descriptions |
| **Combined** | All strategies together |

### Question Types for Code

| Type | Example |
|------|---------|
| **Location** | "Where is the authentication logic?" |
| **Implementation** | "How does the caching layer work?" |
| **Dependency** | "What calls the `processOrder` function?" |
| **Cross-cutting** | "How do errors propagate from API to UI?" |
| **Modification** | "What files need to change to add a new API endpoint?" |

### Success Metrics
- Accuracy on ground-truth questions
- Ability to locate specific code elements
- Quality of modification recommendations

---

## Phase 2.5: Complete V6 Data (IMMEDIATE)

Before Phase 2, complete the V6 data gap:

- [ ] Build very-deep-v6 structure
- [ ] Build shallow-v6 structure
- [ ] Run 92 additional tests (23 questions × 2 structures × 2 methods)
- [ ] Analyze trend: does very-deep continue to degrade or stabilize?

---

## Out of Scope

- Testing models other than Haiku (budget constraint)
- Real-time/streaming use cases
- Non-Claude AI assistants
- Prompt engineering (focus is on structure, not query formulation)

---

## Resources

| Item | Location |
|------|----------|
| Test harness | `harness/` |
| Raw results | `results/` |
| Corpus | `soong-daystrom/` |
| Final report | `report/README.md` |
| Blog draft | Obsidian: `AI-Sessions/Research/Context Structure Research - Blog Draft.md` |
| Session state | `SESSION-STATE.md` |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Use synthetic corpus for Phase 1 | Control variables, create ground truth |
| 2026-01-28 | Skip monolith at V5+ scale | Exceeds Haiku context limit |
| 2026-01-29 | Test enhancement strategies | Hypothesis: indexes help navigation |
| 2026-01-30 | Enhancement indexes hurt at scale | Finding: 27K index words = noise |
| 2026-01-30 | Propose Phase 2 real codebase testing | Practical applicability |

---

## How to Resume This Project

```bash
cd ~/Code/context-structure-research

# Check current state
cat SESSION-STATE.md

# See what's left to do
cat TODO.md

# See research charter and scope
cat PROJECT-CHARTER.md

# Run remaining V6 tests (if structures built)
./harness/run-v6-matrix.sh

# Analyze any new results
python3 harness/evaluator.py results/v6-matrix/raw/haiku --output results/v6-matrix/analysis
```

---

*Charter last updated: 2026-01-30*
