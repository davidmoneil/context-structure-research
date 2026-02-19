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

# Context Forge — Best Practices Research

Research conducted 2026-02-14 on state of the art for LLM context orchestration, compression, evaluation methodology, and statistical rigor. 28+ sources consulted.

---

## Executive Summary

Context Forge's hypothesis — that a small local LLM can preprocess/compress/restructure context to improve quality and reduce tokens — is **well-supported by existing research** but occupies a specific niche. The field has matured rapidly since 2023:

- **LLMLingua** (Microsoft): 20x compression with minimal loss
- **RECOMP** (ICLR'24): 94% compression at retrieval level
- **CompactPrompt** (2025): Compression can actually *improve* output quality at 2-2.5x

**The key finding**: Context Forge's *restructuring* angle (Strategies C/C2) is genuinely underexplored. Most existing work removes tokens; very few reorganize them. This is the novel contribution.

---

## 1. Existing Context Compression Work

### Taxonomy (NAACL 2025 Survey)

**Hard Prompt Methods** (modify text):
- Filtering: SelectiveContext, LLMLingua, LongLLMLingua, LLMLingua-2, AdaComp
- Paraphrasing: Nano-Capsulator, CompAct, FAVICOMP

**Soft Prompt Methods** (learned embeddings):
- Not relevant for Context Forge (requires model-specific fine-tuning, not transferable to API targets)

### Key Systems

| System | Compression | Quality | Approach |
|--------|------------|---------|----------|
| LLMLingua (EMNLP'23) | Up to 20x | Minimal loss | Token-level perplexity pruning |
| LLMLingua-2 (ACL'24) | 5-10x | 95-98% accuracy | Token classification via XLM-RoBERTa |
| LongLLMLingua (ACL'24) | 4x | +21.4% on NaturalQuestions | Long-context optimized |
| RECOMP (ICLR'24) | 94% reduction (16x) | Near-baseline | Extractive + abstractive compressors |
| Selective Context (EMNLP'23) | 2x (50%) | Minor quality drop | Self-information pruning |
| CompactPrompt (Oct 2025) | 2-2.5x | <5% drop, often *improvement* | N-gram abbreviation + quantization |
| DisComp (NAACL'25) | Variable | Task-aware optimization | Two-stage framework |

### Closest to Context Forge

**RECOMP's abstractive compressor** is the most similar — it's essentially a small model restructuring content for a larger model. But it's tied to RAG retrieval, not general context preprocessing.

**LLMLingua-2** uses a small model (XLM-RoBERTa) trained on large model outputs — architecturally analogous but only does token pruning, not restructuring.

### What Failed

1. **Aggressive token pruning (>50%)**: Produces ungrammatical text
2. **Query-agnostic abstractive summarization**: Weaker models omit critical info
3. **Soft prompt methods**: Not transferable across architectures
4. **Information-dense content** (code, math): Only 2-3x vs 10-20x for prose
5. **SQL join accuracy**: Dropped from 0.63 to 0.37 at 4.29x compression

### Compression Ratio Guidelines

| Content Type | Safe Range | Aggressive | Cliff Point |
|-------------|-----------|------------|-------------|
| Natural language prose | 5-10x | 10-20x | ~20x |
| Dense technical docs | 3-5x | 5-8x | ~10x |
| Code/structured data | 2-3x | 3-5x | ~5x |
| Math/formal logic | 1.5-2x | 2-3x | ~3x |
| Financial tables | 2-2.5x | 3x | ~4x |

### Critical Insight

**CompactPrompt found moderate compression (2-2.5x) can *improve* quality** for Claude (+6-10 points on financial QA). This directly validates Context Forge's core thesis — removing noise helps more than including everything.

---

## 2. LLM-as-Judge Best Practices

### Known Biases (Must Mitigate)

| Bias | Severity | Mitigation |
|------|----------|------------|
| **Position bias** | High (>10% accuracy shift) | Pointwise scoring (not pairwise) |
| **Verbosity/length bias** | High | Normalize for length; strict rubrics |
| **Self-preference** | Medium | Different model family for judge vs generator |
| **Concreteness bias** | Medium | Include in rubric that abstract is valid |
| **Knowledge bias** | Medium | Ground truth reference in scoring rubric |

### Scoring Format for Context Forge

1. **Pointwise scoring** (not pairwise) — comparing same-input across many configurations
2. **5-dimension rubric is well-designed**: Accuracy, Completeness, Conciseness, Coherence, Faithfulness
3. **1-5 Likert scale** (not 1-10; LLMs cluster more reliably on narrower scales)
4. **Chain-of-thought before scoring** (G-Eval style) — improves alignment with humans
5. **Temperature 0** for reproducibility
6. **3 runs per judgment, take median** — temperature 0 isn't fully deterministic

### Calibration Protocol

1. Create gold standard set: **30-50 examples** scored by human
2. Run judge on gold set, compare to human scores
3. Compute alignment: **Krippendorff's alpha** (handles ordinal data). Target >= 0.80
4. Iterate on rubric until alignment target met
5. For confidence intervals: ~200 calibration examples per label type (Lee & Zeng 2025)

### Claude-as-Judge Specifics

- Claude tends toward diplomatic/generous scoring — use strict rubrics with explicit "this means failure" examples
- **Self-preference warning**: When Claude generates AND judges, expect inflated scores. Mitigated by Ollama-as-generator / Claude-as-judge setup
- Request explanation *before* score for consistency

---

## 3. RAG vs Context Forge

| Dimension | Standard RAG | Context Forge | Hybrid |
|-----------|-------------|---------------|--------|
| When | Query-time retrieval | Pre-query preparation | Both |
| What | Finds relevant chunks | Restructures known context | Retrieves then restructures |
| Model role | Embedding + reranker | Small LLM as context engineer | Both |
| Context source | Large corpus | Known, bounded context | Either |
| Quality mechanism | Retrieval precision | Compression fidelity | Both |

**Context Forge is NOT RAG** because:
- Context is already known/selected — no retrieval step
- Small model's job is *restructuring*, not *finding*
- Optimization target is context quality, not retrieval relevance

**Hybrid worth exploring**: RAG retrieval → Context Forge preprocessing → target model

### "Lost in the Middle" Opportunity

LLMs lose 15-47% performance as context grows (Stanford research). Context Forge can address this by:
- Putting most important information at beginning/end
- Removing redundant context that dilutes attention
- Restructuring to match target model's attention patterns

---

## 4. Small Model Orchestration Patterns

### Existing Work

| System | Pattern | Result |
|--------|---------|--------|
| FrugalGPT (Stanford 2023) | LLM cascade (small → large) | 98% cost reduction matching GPT-4 |
| RouteLLM (LMSYS, ICLR'25) | Query-difficulty routing | 85% cost reduction on MT Bench |
| OrchestraLLM | SLM + LLM complementary | 50%+ cost reduction |
| Pick and Spin (Dec 2025) | Multi-model orchestration | 21.6% higher success, 30% lower latency |

### Patterns Relevant to Context Forge

1. **Preprocessor Pattern** (our core): Small model restructures input, large model generates. Similar to RECOMP abstractive compressor but generalized
2. **Cascade with Early Exit**: Small model attempts answer; only sends to Claude if confidence low. Could save API costs for simple queries
3. **Router + Preprocessor**: Classify query complexity first, then apply appropriate preprocessing level
4. **Critic Pattern**: Small model reviews large model output for consistency, requests regeneration if needed

### Ollama Considerations

- Recommended models: Qwen2.5-7B-Instruct (good instruction following), Llama-3.1-8B, Phi-3-mini
- Expect 2-10 seconds per preprocessing call on consumer hardware
- Set `OLLAMA_NUM_CTX` to match preprocessing needs

---

## 5. Evaluation Pipeline Design

### Recommendation: Promptfoo + Custom Python

**Promptfoo** for test configuration and execution:
- YAML-based, Ollama-native, LLM-as-Judge built-in, A/B comparison, runs entirely locally

**Custom Python** for statistical analysis:
- scipy for paired bootstrap, Wilcoxon signed-rank
- pandas for data aggregation
- krippendorff for inter-rater reliability

### Alternative Frameworks

| Framework | Best For | Local Support | LLM-Judge |
|-----------|---------|--------------|-----------|
| Promptfoo | Config comparison | Excellent (Ollama) | Built-in |
| DeepEval | Python-native eval | Good | G-Eval |
| RAGAS | RAG-specific metrics | Via LangChain | Built-in |
| LangSmith | Production monitoring | Via LangChain | Paid |

### Pipeline Architecture

```
Test Cases (YAML/JSON)
    ↓
Preprocessing Layer (Ollama models, multiple configs)
    ↓
Target Model (Claude API, fixed config)
    ↓
Judge Model (Claude API, separate call with rubric)
    ↓
Score Collection (JSON/CSV per run)
    ↓
Statistical Analysis (Python: scipy, bootstrap)
    ↓
Report Generation (comparison tables, CIs)
```

### Metrics to Track

| Metric | What It Measures | Why It Matters |
|--------|-----------------|----------------|
| Token count reduction | Raw compression ratio | Cost savings |
| Latency (preprocessing + gen) | Total wall-clock time | Usability |
| Cost per query | API tokens consumed | Budget impact |
| Faithfulness | Claims grounded in source? | Prevents hallucination from compression |
| Information retention | Key facts preserved | Compression quality |
| Consistency (variance) | Score variance across runs | Reliability |

### Consider LLMLingua-2 as Free Baseline

`pip install llmlingua` — compare Ollama-based strategies against proven token-pruning approach. If restructuring doesn't beat mechanical pruning, the restructuring hypothesis weakens.

---

## 6. Statistical Methodology

### Primary Test: Paired Bootstrap + Wilcoxon

1. Fix randomness: Same test cases, same seeds across configs
2. Compute per-case deltas: delta = score(config_A) - score(config_B)
3. BCa Bootstrap CI: 10,000+ resamples on deltas
4. Wilcoxon signed-rank test (non-parametric paired test)
5. Declare significance only if: BCa CI lower bound > 0 AND p-value < 0.05

### Minimum Runs Per Configuration

| Effect Size | Runs Needed |
|------------|------------|
| Large (>5 points) | 3-5 |
| Moderate (2-5 points) | 5-10 |
| Small (<2 points) | 10+ |

**Recommendation**: 5 runs per configuration, 50+ test cases, paired analysis.

### Handling LLM Output Variance

1. Temperature 0 (reduces but doesn't eliminate variance)
2. 3-5 runs per test case, take median
3. Paired analysis eliminates inter-case variance
4. Report Cliff's delta alongside p-values

### Inter-Rater Reliability (Judge Validation)

- **Krippendorff's alpha**: Target >= 0.80
- **Weighted Cohen's kappa**: Target >= 0.60
- **Spearman's rho**: Rank correlation between judge and human

### Python Implementation

```python
from scipy.stats import wilcoxon, bootstrap
import numpy as np

# Paired scores
baseline = [...]
forge = [...]
deltas = np.array(forge) - np.array(baseline)

# Wilcoxon signed-rank
stat, p = wilcoxon(deltas, alternative='greater')

# Bootstrap CI
boot = bootstrap((deltas,), np.mean, n_resamples=10000,
                  method='BCa', confidence_level=0.95)
```

---

## 7. Common Pitfalls to Avoid

1. **Evaluating compression ratio alone** — always report quality alongside
2. **Single-run comparisons** — LLM outputs are stochastic
3. **Same model as generator and judge** — self-preference bias
4. **Ignoring content type** — compression effectiveness varies wildly
5. **Over-optimizing on benchmarks** — include diverse, realistic test cases
6. **Assuming compression always helps** — measure failure modes
7. **Ignoring latency** — 5s preprocessing overhead may negate 2s inference savings

---

## 8. Novel Gaps This Project Fills

1. **No studies on 7-8B Ollama models as preprocessors** for API models specifically
2. **Restructuring vs compression is under-studied** — most work removes tokens, few reorganize
3. **No standard benchmark for context preprocessing quality** — we'll create one
4. **Inter-model transfer of preprocessing** is under-studied
5. **Long-term drift** — no longitudinal studies on preprocessing quality vs model updates

---

## Key Sources

### Context Compression
- [LLMLingua (EMNLP'23)](https://arxiv.org/abs/2310.05736) — Microsoft, perplexity-based pruning
- [LLMLingua-2 (ACL'24)](https://llmlingua.com/llmlingua2.html) — Token classification
- [RECOMP (ICLR'24)](https://arxiv.org/abs/2310.04408) — Extractive + abstractive compression
- [CompactPrompt (Oct 2025)](https://arxiv.org/abs/2510.18043) — Unified pipeline, quality improvement finding
- [Prompt Compression Survey (NAACL'25)](https://aclanthology.org/2025.naacl-long.368/) — Comprehensive taxonomy
- [Characterizing Prompt Compression (2024)](https://arxiv.org/html/2407.08892v1) — Degradation cliffs

### LLM-as-Judge
- [Survey on LLM-as-a-Judge (Nov 2024)](https://arxiv.org/abs/2411.15594) — 200+ paper survey
- [How to Correctly Report (Nov 2025)](https://arxiv.org/html/2511.21140v1) — Statistical methodology
- [Self-Preference Bias (Oct 2024)](https://arxiv.org/html/2410.21819v2)
- [LLM-judge-reporting (GitHub)](https://github.com/UW-Madison-Lee-Lab/LLM-judge-reporting)

### Orchestration
- [FrugalGPT (2023)](https://arxiv.org/abs/2305.05176) — LLM cascade
- [RouteLLM (ICLR'25)](https://github.com/lm-sys/RouteLLM) — Query-difficulty routing
- [Pick and Spin (Dec 2025)](https://arxiv.org/abs/2512.22402) — Multi-model orchestration

### Statistical Methods
- [Paired Bootstrap Protocol (Nov 2025)](https://arxiv.org/html/2511.19794v1)
- [Context Engineering Survey (Jul 2025)](https://arxiv.org/abs/2507.13334)

### Evaluation Frameworks
- [Promptfoo](https://github.com/promptfoo/promptfoo)
- [DeepEval](https://github.com/confident-ai/deepeval)
- [RAGAS](https://docs.ragas.io/en/stable/)
