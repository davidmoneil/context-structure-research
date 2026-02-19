---
tags:
  - artifact/research
  - status/active
  - domain/ai
  - project/context-orchestration
  - depth/deep
created: 2026-02-14
updated: 2026-02-14
---

# Combined Context Research Outline

Three research streams that converge on one problem: **how to get the right context to an LLM in the right form**.

---

## The Three Research Streams

### Stream 1: Context Structure (Empirical)
**Question**: How does file organization depth/shape affect AI comprehension?
**Location**: `~/Code/context-structure-research/` + `.claude/context/projects/context-structure-research.md`
**Status**: Phase 1 complete — 849 tests across V4/V5/V6 corpora. 92 V6-extended results pending analysis.
**Key findings**: Flat wins (97-100%), keywords help (+80% recovery), summaries add nothing beyond keywords, enhancement indexes hurt at scale (-4.6%).
**What it tells Context Forge**: Optimal input structure is flat/shallow. Strategy A (keywords) has empirical support. Strategy B (distillation/summaries) may add noise. Strategy C should target flat/shallow format.

### Stream 2: Context Management (Operational)
**Question**: How to organize, load, and lifecycle context files for Claude Code sessions?
**Key locations**:
- `.claude/context/designs/unified-context-strategy.md` — Three-tier loading, three storage layers
- `.claude/context/projects/context-consolidation-plan-2026-01.md` — 115 files, 97k tokens, 49% of context budget
- `knowledge/notes/consolidation-methodology-mcp-context-optimization.md` — Reusable 5-phase methodology
- `.claude/context/designs/context-aware-content-system.md` — Retrieval agent + context depth levels
- `.claude/context/ideas/dynamic-context-orchestrator.md` — External orchestrator concept
- `05-AI/Projects/2026.02.08- Testing project for Context Managenet.md` — Spread/hops/relevance brainstorm
**What it tells Context Forge**: The *problem space* from a practitioner's perspective — real data on context bloat, what works for loading strategies, the hop/spread model for relevance scoring.

### Stream 3: Context Forge (Research Project)
**Question**: Can a small LLM preprocessing layer improve output quality while reducing token usage?
**Location**: `05-AI/Research/2026.02.14- Context Orchistration/Context Orchestration Research Project.md`
**Status**: Design complete, build not started
**Key design**: 6 strategies (keyword, distill, reformat, inject, cache, chained) x 6 routing patterns x multiple models
**What it brings**: Rigorous experimental methodology, scoring pipeline, strategy taxonomy

---

## Where They Overlap

```
                    STRUCTURE RESEARCH
                    "What shape should context be?"
                           │
                    Informs optimal output
                    format for Strategy C/C2
                           │
                           ▼
CONTEXT MANAGEMENT ──────► CONTEXT FORGE
"What to load and when"    "How to transform what's loaded"

Provides:                  Provides:
- Relevance/hop model      - Compression strategies
- Tiered loading rules     - Quality measurement
- Real token budgets       - Model-agnostic preprocessing
- File access patterns     - Semantic caching
```

**Key insight**: Context Management decides *what* goes in. Structure Research decides *what shape* it should be. Context Forge decides *how to transform* it for maximum signal density.

---

## Combined Project Outline

### Phase 0: Baseline & Infrastructure

- [ ] **0.1** Complete structure research analysis (**849 tests run, 92 pending analysis**)
  - Run evaluator.py on V6-extended results (shallow-v6, very-deep-v6)
  - Update cross-variant comparison with complete V6 data
  - Cost/token analysis across all test suites
  - Statistical significance testing (currently missing)
  - Update final report with complete findings
  - Fix `YOUR-USERNAME` → `davidmoneil` in report files
- [ ] **0.2** Build Context Forge scoring pipeline + baseline (Stream 3, Phase 1)
  - **Install tooling**: Promptfoo (YAML eval framework), llmlingua (baseline), scipy/krippendorff (stats)
  - **Promptfoo setup**: YAML test configs, Ollama provider, Claude judge with 5-dimension rubric
  - **LLM-as-Judge calibration**: 30-50 human-scored gold standard, chain-of-thought scoring, 3x median, alpha >= 0.80
  - **Create test corpus**: 50+ diverse test cases (prose, technical, code, structured)
  - **Run baselines**: (a) raw → Claude (no preprocessing), (b) LLMLingua-2 → Claude (published baseline)
  - **Statistical harness**: Paired bootstrap + Wilcoxon, 5 runs per config, BCa confidence intervals
  - **Metrics logging**: JSON per run (all fields from design doc + compression ratio + latency)
- [ ] **0.3** Document current AIProjects context loading metrics (Stream 2)
  - What gets loaded, how much, file access frequency from audit logs
  - Baseline token usage per session type

### Phase 1: Strategy Validation

- [ ] **1.1** Test individual Context Forge strategies A/B/C/C2 against baseline
  - Use Ollama local models as orchestration layer
  - Score with LLM-as-Judge (accuracy, completeness, conciseness, coherence, faithfulness)
- [ ] **1.2** Feed structure research results into Strategy C
  - If "shallow 2-level hierarchy" wins the structure test, use that as C's target format
  - If "flat with tags" wins, use that format instead
  - Data-driven reformatting, not guesswork
- [ ] **1.3** Test the spread/hop relevance model from Stream 2
  - Implement query complexity scoring (1 ask = 0.1 spread, 5 asks = 0.7)
  - Test 1-hop vs 2-hop vs 3-hop context loading
  - Measure quality vs. token reduction at each hop depth

### Phase 2: Integration Patterns

- [ ] **2.1** Combine relevance selection (Stream 2) with compression (Stream 3)
  - Select context via hop/relevance → compress via winning strategy → send to target
  - Full pipeline: intent analysis → relevance scoring → context selection → preprocessing → inference
- [ ] **2.2** Test chained strategies (Stream 3, Strategy F)
  - A+C2 (keywords + injection), A+B (keywords + distill), etc.
  - Measure compounding vs. diminishing returns
- [ ] **2.3** Cross-model portability
  - Does context compressed by Llama 8B work well for Mistral? Qwen? Claude?
  - Is the orchestration layer model-agnostic?

### Phase 3: Applied Context Orchestration

- [ ] **3.1** Build the orchestration layer
  - External process that sits between user and target model
  - Implements: intent analysis → relevance retrieval → strategy selection → preprocessing → inference
  - Technology: Python + Ollama + pgvector
- [ ] **3.2** Apply to Claude Code context management
  - Can Context Forge preprocess the 97k tokens of AIProjects context?
  - Test: forge-compressed CLAUDE.md vs. raw CLAUDE.md on real session tasks
  - Potential: reduce 49% context budget to 25-30% with same or better comprehension
- [ ] **3.3** Semantic cache layer (Stream 3, Strategy E)
  - Store preprocessed context in pgvector
  - Retrieve relevant cached chunks for new queries
  - Avoid re-compression of stable context

### Phase 4: Evaluation & Publication

- [ ] **4.1** Hand-scored validation of top findings
  - 20-30 item eval set scored by human
  - Confirm LLM-as-Judge alignment
- [ ] **4.2** Statistical analysis across all configurations
  - Identify winning patterns with confidence intervals
  - Variance analysis (consistency matters as much as average quality)
- [ ] **4.3** Value assessment
  - Who benefits? How many?
  - Does this already exist? (RAG is partial overlap, but the orchestration/strategy layer is different)
  - Distribution model: open-source tool? Research paper? Both?

---

## Shared Resources

| Resource | Used By | Purpose |
|----------|---------|---------|
| Ollama (local) | Forge, Structure | LLM inference |
| Claude API | Forge, Structure | Target model + scoring judge |
| Soong-Daystrom corpus (120K words) | Structure, Forge | Test content |
| pgvector (Postgres) | Forge | Semantic cache |
| AIProjects context files | Management, Forge | Real-world test content |
| Beads task tracking | All | Project management |
| Python test harness | Forge, Structure | Evaluation pipeline |

---

## Design Adjustments from Best Practices Research (2026-02-14)

Research findings documented in `Best Practices Research.md` (same folder). Key adjustments:

### Methodology Upgrades

1. **LLM-as-Judge calibration is more involved than planned**
   - Need chain-of-thought before scoring (G-Eval style), not just rubric → number
   - Run each judgment 3x, take median (temperature 0 isn't fully deterministic)
   - Create 30-50 human-scored gold standard to validate the judge
   - Target Krippendorff's alpha >= 0.80 for judge-human alignment
   - For full confidence intervals: ~200 calibration examples per label type

2. **Statistical methodology must be paired, not just averaged**
   - 5 runs per configuration minimum (paired analysis gives enough power)
   - Use paired bootstrap with BCa confidence intervals + Wilcoxon signed-rank test
   - Report effect size (Cliff's delta) alongside p-values
   - Structure research used accuracy %; Context Forge needs composite score + variance

3. **Add LLMLingua-2 as baseline comparison**
   - `pip install llmlingua` — proven token-pruning approach
   - If restructuring doesn't beat mechanical pruning, the restructuring hypothesis weakens
   - Free to run, gives a published-method comparison point

4. **Use Promptfoo for evaluation pipeline** (don't build from scratch)
   - YAML-based test configuration, native Ollama support, built-in LLM-as-Judge
   - Custom Python on top for statistical analysis only

5. **Self-preference bias is real**
   - Claude as both target and judge inflates scores
   - Ollama-as-generator / Claude-as-judge avoids this for preprocessing tests
   - Flag in methodology for baseline tests (raw → Claude → Claude judges)

### Compression Target Adjustments

Based on literature, target 2-5x compression as default operating range:
- **Quality improvement zone**: 2-2.5x may actually *improve* quality (CompactPrompt finding)
- **Safe zone**: 2-5x retains 95%+ quality across all methods
- **Content-aware**: Different strategies for prose vs code vs structured data
- **Measure at multiple levels**: 1x, 2x, 3x, 5x, 10x to find the cliff per content type

### Novel Contribution Confirmed

Context Forge's restructuring angle (Strategies C/C2) is genuinely underexplored:
- Most existing work removes tokens; very few reorganize them
- RECOMP's abstractive compressor is closest but tied to RAG
- No studies on 7-8B Ollama models as preprocessors for API models
- No standard benchmark for context preprocessing quality

### Tools to Install (Phase 0.2)

```bash
npm install -g promptfoo          # Evaluation framework
pip install llmlingua             # Compression baseline
pip install scipy numpy pandas    # Statistical analysis
pip install krippendorff          # Inter-rater reliability
pip install matplotlib            # Visualization
```

---

## Decision Points

| Decision | When | Impact |
|----------|------|--------|
| Run structure research first or in parallel? | Phase 0 | Structure data informs Forge's Strategy C target format |
| Which Ollama models to use? | Phase 0 | Constrained by home lab compute |
| MVP scope — stop at Phase 1 or go through Phase 3? | After Phase 1 results | If strategies don't beat baseline, pivot or stop |
| Build for personal use or distribution? | Phase 4 | Affects architecture decisions |
| Separate repo or part of AIProjects? | Phase 0 | Should be separate (per dynamic-context-orchestrator.md) |
| Promptfoo vs custom harness? | Phase 0.2 | **DECIDED**: Promptfoo + custom Python for stats |
| Include LLMLingua-2 baseline? | Phase 0.2 | **DECIDED**: Yes, as published-method comparison |
| Judge calibration depth? | Phase 0.2 | **DECIDED**: 30-50 gold standard, alpha >= 0.80 |

---

## Related Files (Complete Index)

### Stream 1: Structure Research
- `.claude/context/projects/context-structure-research.md`
- `~/Code/context-structure-research/` (project code)

### Stream 2: Context Management
- `.claude/context/designs/unified-context-strategy.md`
- `.claude/context/projects/context-consolidation-plan-2026-01.md`
- `knowledge/notes/consolidation-methodology-mcp-context-optimization.md`
- `.claude/context/audits/context-loading-review-2026-01-22.md`
- `.claude/context/designs/context-aware-content-system.md`
- `.claude/context/designs/fresh-context-agent-mode.md`
- `.claude/context/ideas/dynamic-context-orchestrator.md`
- `05-AI/Projects/2026.02.08- Testing project for Context Managenet.md`

### Stream 3: Context Forge
- `05-AI/Research/2026.02.14- Context Orchistration/Context Orchestration Research Project.md`
