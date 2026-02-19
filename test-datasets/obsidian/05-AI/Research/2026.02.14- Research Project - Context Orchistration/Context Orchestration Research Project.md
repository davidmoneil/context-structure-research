
## Project Codename: Context Forge

### Core Thesis

Small LLMs don’t fail because they lack reasoning ability — they fail because they’re drowning in noisy, unstructured context. By using a local LLM as a context orchestration layer that preprocesses, compresses, and restructures context before inference, we can significantly improve output quality, reduce token usage, and increase speed — potentially enabling small models to punch well above their weight class.

### Research Question

What kinds of context preparation yield the biggest quality lift when routing prompts through local LLMs, and does that hold across model sizes and families?

### Secondary Questions

- Does compressed/restructured context improve consistency (reduced variance), not just average quality?
- Are context preparation gains model-family-dependent or universal?
- Which combinations of strategies produce compounding benefits vs. diminishing returns?
- At what compression ratio does quality begin to degrade, and is that threshold consistent across task types?

-----

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  USER PROMPT                     │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│         CONTEXT ORCHESTRATION LAYER              │
│         (Local LLM via Ollama)                   │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │Strategy A│ │Strategy B│ │Strategy C / C2   │ │
│  │Keywords  │ │Distill   │ │Restructure/Inject│ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│                                                  │
│  Strategies can run individually or chained (F)  │
└─────────────┬───────────────────────────────────┘
              │  Composed context + prompt
              ▼
┌─────────────────────────────────────────────────┐
│            TARGET MODEL                          │
│  (Larger local model OR Claude API)              │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│         POST-PROCESSING (Optional)               │
│  Compress output for semantic cache (Strategy E) │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│    STORAGE: Postgres Vector DB (pgvector)         │
│    Cached compressed outputs for reuse            │
└─────────────────────────────────────────────────┘
```

-----

## Context Strategies (Testable Modules)

Each strategy is an independent module that can run alone or be chained with others.

### Strategy A: Keyword Extraction

- **What it does:** Small model extracts keywords and key entities from the source context. Those keywords are bundled with the user prompt before sending to the target model.
- **Why it matters:** Already proven to improve Q&A quality when fed back to the same small model. The first pass extracts signal, the second pass reasons with concentrated signal.
- **Prior evidence:** Tested manually with positive results on Q&A tasks using LLM-as-judge evaluation.
- **Implementation:** Send context to local LLM with prompt: “Extract the key terms, entities, and concepts from this text. Return only the keywords.” Append result to user prompt.

### Strategy B: Distillation

- **What it does:** Small model produces a condensed narrative summary of larger context. Not keywords — a shorter but coherent version of the source material.
- **Why it matters:** Tests whether abstractive compression preserves enough signal for downstream reasoning.
- **Risk:** Lossy — the small model may drop important details or introduce subtle inaccuracies.
- **Implementation:** Send context to local LLM with prompt: “Distill the following into a concise summary preserving all key facts, relationships, and decisions.” Use output as replacement context.

### Strategy C: Structured Reformat

- **What it does:** Small model completely restructures messy/unstructured context into a clean tagged schema.
- **Why it matters:** Converts noise into parseable structure. The target model gets organized input instead of raw conversational or document text.
- **Risk:** Reformatting may lose contextual nuance that existed in the original structure.
- **Output format example:**
  
  ```
  [USER_INTENT] What the user is actually asking for
  [KEY_FACTS] Enumerated facts relevant to the query
  [PRIOR_DECISIONS] Any decisions already made in context
  [OPEN_QUESTIONS] Unresolved items
  [CONSTRAINTS] Known limitations or requirements
  ```
- **Implementation:** Send context + user prompt to local LLM with instructions to reformat into the schema. Send schema output as context to target model.

### Strategy C2: Context Injection

- **What it does:** Small model preserves the original prompt structure but inserts targeted context tags inline — enriching the prompt without rewriting it.
- **Why it matters:** Lower risk than C — the original prompt intent is preserved. Tests whether augmentation outperforms restructuring.
- **How it differs from C:** C rebuilds the prompt. C2 leaves the prompt intact and adds context markers around/within it.
- **Output format example:**
  
  ```
  <relevant_background>Summary of relevant prior context</relevant_background>
  <key_terms>Extracted terminology and definitions</key_terms>
  
  [ORIGINAL USER PROMPT UNCHANGED]
  
  <prior_decisions>Relevant decisions from conversation history</prior_decisions>
  ```
- **Implementation:** Small model analyzes context, generates injection tags, inserts them around the original prompt. Full enriched prompt sent to target model.

### Strategy E: Semantic Cache

- **What it does:** Compressed representations of previous outputs are stored in Postgres/pgvector and retrieved when the small model detects relevance to a new query.
- **Why it matters:** Avoids re-reasoning over previously processed information. Speed and cost optimization.
- **Dependency:** Only valuable once we’ve validated that compressed representations from Strategies A-C are high quality.
- **Implementation:** After target model responds, run response through compression strategy. Store compressed version with embedding in pgvector. On new queries, retrieve relevant cached chunks and include in context.
- **Build order:** Implement AFTER validating compression quality with Strategies A-C.

### Strategy F: Chained Combinations

- **What it does:** Runs multiple strategies in sequence before sending to the target model.
- **Combinations to test:**
  - A → C2 (extract keywords, then inject as context tags)
  - A → B (extract keywords, then distill with keywords as guide)
  - B → C (distill first, then restructure the distillation)
  - A → C2 → E (keywords + injection + cache retrieval)
- **Why it matters:** The core question is whether combinations compound or conflict. Does adding more preparation help or introduce cumulative noise?

-----

## Routing Patterns

|Pattern         |Flow                                                    |Purpose                                           |
|----------------|--------------------------------------------------------|--------------------------------------------------|
|**Direct**      |Raw context → target model                              |Baseline. No orchestration.                       |
|**Compress-Up** |Small model prepares → large model reasons              |Primary test pattern                              |
|**Reason-Down** |Large model reasons → small model compresses output     |Post-processing for caching                       |
|**Full Loop**   |Small prepares → large reasons → small compresses output|Complete orchestration                            |
|**Lateral**     |Small model A prepares → small model B reasons          |Tests if orchestration makes small-to-small viable|
|**Cross-Family**|Model family A prepares → model family B reasons        |Tests portability of compressed context           |

### Phase 1 routing (start here):

- Direct (baseline)
- Compress-Up (small → Claude API)

### Phase 2 routing (after initial results):

- Compress-Up across local model sizes (~3B, ~8B, ~14B, ~20B)
- Cross-Family (Llama prep → Mistral reasoning, etc.)
- Lateral (small → small)

### Phase 3 routing:

- Full Loop
- Reason-Down for semantic caching

-----

## Evaluation Methodology

### Primary Method: LLM-as-Judge (Claude API)

Use Claude API as an automated scoring judge for rapid iteration. For each test run, send the output along with a scoring rubric.

**Scoring Dimensions (each rated 1-5):**

|Dimension       |What It Measures                                        |
|----------------|--------------------------------------------------------|
|**Accuracy**    |Is the answer factually correct?                        |
|**Completeness**|Did it address the full question?                       |
|**Conciseness** |Did it answer without unnecessary padding?              |
|**Coherence**   |Does the answer flow logically?                         |
|**Faithfulness**|Does it stay true to source context (no hallucinations)?|

**Composite score:** Average of all five dimensions per run.

**Variance measurement:** Run each configuration 5-10 times on the same input. Calculate standard deviation of composite scores. High variance = unreliable strategy even if average is good.

### Validation Method: Hand-Scored Eval Set

Once LLM-as-Judge reveals patterns (e.g., “Strategy A+C2 consistently scores highest”), build a smaller hand-scored evaluation set (20-30 items) to validate that the automated judge aligns with human judgment.

### Metrics to Log Per Run

```
{
  "run_id": "uuid",
  "timestamp": "ISO-8601",
  "strategy": "A | B | C | C2 | E | F:A+C2 | none",
  "routing_pattern": "compress-up | direct | lateral | ...",
  "orchestration_model": "llama3:8b",
  "orchestration_model_size": "8B",
  "target_model": "claude-sonnet-4-5-20250929 | mistral:20b | ...",
  "target_model_size": "20B | API",
  "task_type": "qa | synthesis | ambiguous",
  "input_tokens_original": 2400,
  "input_tokens_after_strategy": 800,
  "token_reduction_ratio": 0.67,
  "output_tokens": 350,
  "latency_orchestration_ms": 1200,
  "latency_target_ms": 3400,
  "latency_total_ms": 4600,
  "score_accuracy": 4,
  "score_completeness": 5,
  "score_conciseness": 4,
  "score_coherence": 5,
  "score_faithfulness": 4,
  "score_composite": 4.4,
  "run_number_of_n": "3 of 10"
}
```

### Task Categories for Testing

1. **Long Context Q&A** — Provide a 3-4 page document as context, ask specific factual questions. Tests whether compression preserves the right details.
2. **Multi-Fact Synthesis** — Questions requiring combination of 3-4 separate facts from context. Tests whether compression maintains relationships between facts.
3. **Ambiguous/Nuanced Questions** — Context contains conflicting or subtle information. Tests whether compression flattens nuance.

**Initial test content:** Use Claude API to generate test documents and questions with known correct answers. This bootstraps the eval set quickly without manual authoring.

-----

## Build Order

### Phase 1: Scoring Pipeline + Baseline

**Goal:** Get the measurement infrastructure working before testing any strategies.

1. Build the test harness (Python)
- Input: test question + context document
- Output: answer from target model
- Scoring: send output to Claude API with rubric, log scores
- Storage: log all metrics to file/DB
1. Run baseline tests (Strategy: none, Routing: direct to Claude API)
- Establish quality baseline across all task categories
- Establish latency and token usage baselines
- Run each test 5-10 times to establish variance baseline
1. Validate that scoring pipeline produces consistent results

### Phase 2: Individual Strategies

**Goal:** Test each strategy in isolation against the baseline.

1. Implement Strategy A (keyword extraction) via Ollama
- Test with primary small model (~8B)
- Compare scores against baseline
- Measure token reduction and latency overhead
1. Implement Strategy B (distillation) via Ollama
- Test with same model as A for apples-to-apples
- Compare against baseline AND against A
1. Implement Strategy C (structured reformat)
- Compare against baseline, A, and B
1. Implement Strategy C2 (context injection)
- Compare against baseline, A, B, and C
- Specifically compare C vs C2 — restructure vs. augment

### Phase 3: Combinations + Cross-Model

**Goal:** Test strategy chains and model portability.

1. Implement Strategy F combinations
- A+C2, A+B, B+C — test top combos
- Compare against best individual strategy
1. Cross-model testing
- Replay winning strategies across different orchestration models
- Test: Llama, Mistral, Phi, Qwen at ~8B
- Test: different sizes within same family (3B, 8B, 14B)
1. Cross-family routing
- Prep with model family A, reason with family B
- Key question: is compressed context portable?

### Phase 4: Caching + Optimization

**Goal:** Build persistence and reuse layer.

1. Implement Strategy E (semantic cache)
- Store compressed outputs in pgvector
- Test retrieval relevance
- Measure quality impact of cached vs. fresh context
1. Full Loop routing
- Small model orchestrates → target reasons → small model compresses output → cache
- End-to-end performance measurement

### Phase 5: Analysis + Publication Decision

1. Aggregate all data
- Statistical analysis across all configurations
- Identify winning patterns
- Build hand-scored eval set to validate top findings
1. Determine if findings are publishable
- Novel contribution?
- Consistent, reproducible results?
- Clear practical implications?

-----

## Technology Stack

|Component        |Technology                                                            |
|-----------------|----------------------------------------------------------------------|
|Local LLM runtime|Ollama                                                                |
|Small models     |Llama 3 8B, Mistral 7B, Phi-3, Qwen 2 (TBD based on available compute)|
|Large local model|~20B parameter model (TBD)                                            |
|Cloud API        |Claude API (Sonnet for judging, target model for testing)             |
|Orchestration    |Python (primary), potentially n8n for workflow visualization          |
|Vector storage   |Postgres with pgvector                                                |
|Metrics storage  |JSON logs initially, Postgres if volume warrants it                   |
|Test harness     |Python with async support for parallel runs                           |

-----

## Open Questions

- [ ] What specific models are available on the home lab given compute constraints?
- [ ] What compression ratio targets are we aiming for? (50%? 75%? Test to find the cliff?)
- [ ] Should the scoring rubric be task-type-specific or universal?
- [ ] How do we handle strategies that improve some dimensions but hurt others? (e.g., better conciseness but worse completeness)
- [ ] Is there value in testing context preparation for code generation tasks in addition to Q&A/synthesis?
- [ ] What is the right sample size per configuration for statistical significance?
- [ ] Should we track embedding-space drift as a metric (cosine similarity between original and compressed context)?

-----

## Success Criteria

- **Minimum viable finding:** At least one strategy consistently outperforms raw context (baseline) by ≥ 0.5 composite score points with ≤ 10% variance increase.
- **Strong finding:** A strategy or combination that reduces tokens by 50%+ while maintaining or improving quality scores.
- **Publishable finding:** Cross-model portability results — evidence that context preparation is (or is not) model-family-dependent, with statistical backing across multiple model families and sizes.%%  %%