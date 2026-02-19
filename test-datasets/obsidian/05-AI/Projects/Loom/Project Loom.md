# Loom — Dynamic Context Orchestration System

**Concept Document v0.2 | February 2026 | Status: Concept / Blocked on Research**

> **Note (2026-02-18)**: Loom development is blocked on findings from [[Context-Structure-Research]]. Strategy experiments (previously Sections 8.4-8.5 here) have been moved to that project as Phase 3. Loom starts when research produces a winning strategy for the orchestration engine's output format. See `AIProjects/.claude/context/projects/loom.md` and `context-structure-research.md` for current state.

-----

## 1. Executive Summary

Loom is a dynamic context orchestration system designed to optimize how local LLMs (via Ollama) receive and process contextual information. Rather than naively loading all available context into a model’s context window, Loom builds a lightweight graph of concept nodes and content nodes, then uses a multi-signal ranking engine to determine the minimum relevant context needed to produce high-quality responses.

The system operates on the principle that sending less, more relevant context produces better results than flooding the context window — and does so with lower compute cost and faster inference times. As context windows grow larger, the value proposition shifts from “fitting within limits” to “optimizing signal-to-noise ratio.”

-----

## 2. Problem Statement

Current approaches to context management for LLMs fall into two extremes: load everything (wasteful, noisy, and limited by window size) or use basic RAG retrieval (often too narrow, missing related context that would improve the response). Neither approach dynamically adapts to the complexity of the query, the relationships between data, or the characteristics of the available context.

Loom addresses this gap by introducing an orchestration layer that understands the shape of available knowledge, the complexity of the incoming query, and the budget constraints of the context window — then makes intelligent loading decisions in real time.

-----

## 3. Architecture Overview

Loom consists of four distinct subsystems that operate in a pipeline. Each subsystem has defined inputs and outputs, enabling modular development and testing.

|Subsystem                  |Purpose                                                                 |Trigger                                   |Output                                            |
|---------------------------|------------------------------------------------------------------------|------------------------------------------|--------------------------------------------------|
|**Input Classifier**       |Classifies incoming content by type and complexity                      |Every user input, synchronous             |Classification metadata, chunked content if needed|
|**Graph Manager**          |Maintains concept nodes, content nodes, edges, and all metadata         |After classification; after LLM response  |Updated graph state                               |
|**Orchestration Engine**   |Scores content, calculates budget, assembles prompt with optimal context|Before each LLM call                      |Assembled prompt with context header              |
|**Post-Processing Indexer**|Indexes LLM responses, updates graph relationships, runs in background  |After LLM response, async while user reads|New/updated content and concept nodes             |

-----

## 4. Data Model

### 4.1 Concept Nodes

Concept nodes are abstract index entries that represent topics, subjects, or domains. They exist solely for the orchestration layer and are never sent to the LLM. Each concept node contains: a unique identifier, a human-readable name, a one-sentence description, an embedding vector (generated via Ollama embedding model such as nomic-embed-text), and a creation timestamp.

Concept nodes form the backbone of the graph. Edges between concept nodes represent semantic proximity, with the edge weight being the cosine similarity between their embedding vectors. These inter-concept edges are pre-calculated on node creation and updated when new concept nodes are added.

### 4.2 Content Nodes

Content nodes hold the actual data that may be loaded into the LLM’s context window. Each content node contains: a unique identifier, the raw content (text, code, logs, analysis, etc.), a content type classification (input, output, analysis, file reference), a token count, a staleness counter (exponential decay), a creation timestamp, and a provenance record (what created this node and why).

Content nodes are always attached to one or more concept nodes. A single content node can link to multiple concepts, creating a many-to-many relationship. Each edge between a content node and a concept node carries: the cosine similarity score at time of linking, the provenance direction (was this linked because of an input or an output?), and a timestamp.

### 4.3 Concept Node Creation Threshold

When new content is processed, the system generates an embedding and compares it against all existing concept nodes. If any existing concept node exceeds the similarity threshold (starting value: 0.8, tunable), the content is linked to all concepts above the threshold, with the similarity score stored on each edge. If no existing concept meets the threshold, a new concept node is created. The system also records the highest-scoring near-miss for debugging and threshold tuning purposes.

The threshold value of 0.8 is a starting hypothesis. It will need empirical tuning based on the embedding model used, as different models have different similarity distributions. This is identified as a critical tuning parameter for the project.

-----

## 5. Ranking Signals

The orchestration engine scores every content node against the current query using multiple weighted signals. Each signal is normalized to a 0–1 range, then combined via configurable weights into a composite relevance score.

|Signal                     |Description                                                                                         |Default Weight|
|---------------------------|----------------------------------------------------------------------------------------------------|--------------|
|**Semantic Relevance**     |Embedding cosine similarity between query and content node concepts                                 |High          |
|**Hop Distance**           |Number of edges from the most relevant concept node                                                 |High          |
|**Staleness (Decay Curve)**|How recently the node was accessed; exponential decay, not linear                                   |Medium        |
|**Content Size**           |Token count of the content node; directly affects context budget                                    |Medium        |
|**Provenance Weight**      |Source type: input, output, or analysis. Analysis/output nodes are more information-dense per token |Medium        |
|**Link Density**           |Number of relevant concept nodes this content connects to. More relevant connections = higher signal|Low-Medium    |

Signal weights are tunable parameters. The testing framework (Section 8) will be used to determine optimal weight configurations for different use cases.

-----

## 6. Context Loading Strategy

### 6.1 Budget Calculation

The orchestration engine first determines the available context budget by subtracting reserved allocations from the model’s total context window. The reserved allocation includes: the system prompt (fixed size, known), an output reservation (estimated based on query complexity from the input classifier), and the context header/manifest (small, relatively fixed). The remaining tokens constitute the loadable context budget.

### 6.2 Loading Decision Tree

The orchestration engine follows a tiered loading strategy:

- If total relevant content fits within the budget, all relevant content is loaded with no summarization.
- If total relevant content exceeds the budget, nodes are loaded in descending composite score order until the budget is consumed.
- For high-scoring nodes that individually exceed a size threshold, the system evaluates whether to load the full content, load a summary (if one exists as a linked analysis node), or chunk the content and load only the most relevant segments.
- Low-scoring nodes that fall below the budget cutoff are excluded from the prompt but included in the context manifest header so the LLM is aware they exist.

### 6.3 Context Manifest Header

Every prompt assembled by the orchestration engine includes a lightweight header block at the top. This header lists the nodes that were loaded (with relevance score and source type), the count of relevant nodes that were not loaded, and a flag indicating whether callback retrieval is available. This header costs minimal tokens but gives the LLM awareness of what context it has and what additional context exists, enabling the callback mechanism in future versions.

Example:

```
[Context loaded: 3 of 7 relevant nodes]
[Node: OAuth token analysis | relevance: 0.92 | source: output]
[Node: Auth error logs summary | relevance: 0.85 | source: analysis]
[Node: API endpoint docs | relevance: 0.81 | source: input]
[Additional context available but not loaded: 4 nodes]
```

-----

## 7. Input Classification

### 7.1 Lightweight Classification (No LLM Call)

The input classifier uses rule-based and statistical methods to classify incoming content without requiring an inference call. The classification signals include: structural detection via regex (code blocks, log patterns, JSON/XML structures, timestamps, stack traces), lexical diversity (unique words divided by total words), complexity proxy (average word length, syllable count approximation), question detection (presence and count of question marks, interrogative keywords), line count and whitespace pattern analysis, and content length thresholds.

These signals produce a classification output with the following properties: content type (simple query, complex multi-part query, pasted data, code, logs, mixed), estimated complexity score (0–1), and a chunking recommendation (whether the input should be split before processing).

### 7.2 Chunking and Splicing

When the classifier detects that an input contains structurally different content (such as a question followed by pasted log data), it splits the input into separate content units. Each unit is processed independently by the graph manager: the conversational query becomes one content node, the pasted data becomes another. This prevents large data pastes from being treated as monolithic context and enables the orchestration engine to make granular loading decisions on future queries.

Chunking only occurs when content exceeds a configurable size threshold. Short inputs pass through without splitting regardless of structural signals.

-----

## 8. Testing and Validation

### 8.1 Core Testing Principle

Loom's V1 testing validates the **reference and retrieval system**, not the underlying data. The question is not “is the dataset complex enough?” but “given any dataset, does Loom build accurate references to it and retrieve the minimum relevant subset for a given query?” This means the dataset can be small, familiar, and well-understood — what matters is whether the developer can immediately judge if Loom picked the right content nodes and skipped the irrelevant ones.

### 8.2 Self-Referential Testing (Primary V1 Dataset)

Loom's own codebase is the primary V1 test dataset. This is deliberate:

- **Intimate knowledge**: The developer knows every module, function, and design decision, enabling immediate judgment of whether Loom's reference selections are correct.
- **Natural growth**: As Loom is built, the dataset grows in complexity organically — starting with a few files and expanding to a full system with cross-module dependencies.
- **Dog-fooding**: Loom indexing its own code validates the system against the exact type of content it's designed to orchestrate.
- **Built-in progressive complexity**: Early development (2-3 files) tests basic reference accuracy. Mid-development (10-20 files) tests cross-module relevance. Late development (full system) tests budget-aware loading under real constraints.

Example test cases against Loom's own codebase:
- “How does the ranking engine score content?” → Should reference orchestration engine scoring logic and ranking signal config, not the graph manager or input classifier.
- “What format is graph.json?” → Should reference the schema definition, not the parser or loader.
- “Explain input classification” → Should load the classifier module and skip unrelated subsystems.

Grading is binary per node: **correct reference** (the node was relevant to the query) or **incorrect reference** (the node was loaded but not needed, or a needed node was omitted).

### 8.3 Secondary Test Datasets

Additional datasets validate that Loom generalizes beyond its own codebase. These are secondary — used after self-referential testing proves the core system works.

| Dataset | Purpose | Selection Criteria |
|---------|---------|-------------------|
| **DVWA** (Damn Vulnerable Web App) | Small external codebase (~50 PHP files) | Structured, well-documented, different language than Loom |
| **Larger OSS repo** (e.g., FastAPI, ~300 files) | Stress test for reference accuracy at scale | Forces harder relevance decisions across many modules |
| **Loom's own concept document** | Non-code content with cross-references | Validates that reference building works on prose, not just code |

Dataset selection is guided by the testing principle (8.1): choose datasets where the developer can confidently judge correctness, not datasets that are large or complex for their own sake.

### 8.4 Referencing Strategy Experiments

> **Moved (2026-02-18)**: This section has been moved to the [[Context-Structure-Research]] project as Phase 3. Strategy experiments test referencing approaches for Claude Code, which is research — not Loom product development. See `AIProjects/.claude/context/projects/context-structure-research.md` for the full experiment design (Strategies A-E, hub-and-spoke testing, experiment architecture).

Loom's orchestration engine output format will be informed by the winning strategy from this research.

### 8.6 Baseline Establishment

Strategy A (whole-file @ references, no index optimization) serves as the baseline. All other strategies are measured against it. The baseline records: correctness of the output, token usage per request, inference latency, and quality of analysis.

### 8.7 Progressive Complexity Testing

Test patterns increase in complexity over time across the following dimensions: number of files and concepts in the session, depth of cross-references between content, ambiguity of queries (requiring the system to make harder relevance judgments), and multi-turn conversations that test staleness and graph evolution. With the self-referential dataset, this progression happens naturally as Loom's codebase grows.

### 8.8 Success Metrics

The primary success metric is: does Loom produce equivalent or better output quality while using measurably less context? Secondary metrics include: token efficiency (relevant tokens loaded vs. total tokens available), precision of context selection (were the loaded nodes actually used by the model?), latency overhead of the orchestration layer, and correctness of concept node creation and linking.

An additional metric specific to reference accuracy: **reference precision and recall**. For a given query with a known set of relevant content nodes, measure what percentage of loaded nodes were correct (precision) and what percentage of relevant nodes were loaded (recall).

-----

## 9. Storage and Session Model

### 9.1 File-Based Storage (V1)

For V1, all data is stored as files for simplicity and debuggability. The recommended structure is a session directory containing:

- **graph.json** — manifest that defines all concept nodes, content nodes, edges, metadata, and scores
- **content/** — subdirectory containing the actual content files referenced by content node IDs
- **embeddings/** — subdirectory containing cached embedding vectors

The graph.json file is the single source of truth for the orchestration layer. It reads the graph, makes loading decisions, and only touches content files for nodes it decides to load. This separation enables easy inspection and debugging of orchestration decisions by examining the graph state.

### 9.2 Session Scope (V1)

V1 is session-scoped only. Each session operates on its own graph with no cross-session persistence. This dramatically simplifies the implementation by eliminating graph merging, conflict resolution, and identity management across sessions. Cross-session persistence, project-based knowledge graphs, and session-to-project promotion are identified as V2/V3 features.

-----

## 10. Technology Stack (V1)

The V1 technology stack is intentionally minimal to reduce complexity during the concept validation phase.

|Component               |Technology                                 |Rationale                                                   |
|------------------------|-------------------------------------------|------------------------------------------------------------|
|**LLM Runtime**         |Ollama (local)                             |Local inference, no API costs, supports embedding models    |
|**Embedding Model**     |nomic-embed-text or all-minilm (via Ollama)|Fast, local, sufficient quality for concept similarity      |
|**Graph Storage**       |JSON files (graph.json per session)        |Simple, debuggable, no infrastructure overhead              |
|**Orchestration Layer** |Python                                     |Rich NLP/ML ecosystem, embedding library support            |
|**Input Classification**|Regex + lightweight NLP (TF-IDF, textstat) |No inference cost, fast, sufficient for structural detection|

-----

## 11. Future Scope (V2/V3)

The following capabilities are explicitly out of scope for V1 but identified as future development targets.

- **Cross-session persistence:** Concept and content nodes persist across sessions, enabling a growing knowledge graph. Requires graph merging and identity resolution.
- **Project-based knowledge graphs:** Sessions can be promoted into project-scoped graphs that accumulate knowledge over time.
- **Callback retrieval:** The LLM can request additional context from the orchestration layer mid-response. Requires a termination strategy (default limit of 2 callbacks, with potential for dynamic termination based on answer stability).
- **Graph database migration:** If graph complexity exceeds what JSON files can handle performantly, migrate to Neo4j Community Edition, NetworkX, or a purpose-built graph store.
- **Contradiction detection:** Automated identification of conflicting content nodes with recency-based resolution as the default strategy.
- **Multi-model support:** Extend beyond Ollama to support remote APIs (Anthropic, OpenAI) with context window budget adapting per model.

-----

## 12. Open Questions and Tuning Parameters

The following items require empirical testing to resolve. They are identified as tunable parameters, not design flaws.

|Parameter                        |Starting Hypothesis    |Tuning Method                                                                           |
|---------------------------------|-----------------------|----------------------------------------------------------------------------------------|
|**Concept similarity threshold** |0.8 cosine similarity  |Test with multiple embedding models; measure concept node proliferation vs. accuracy    |
|**Ranking signal weights**       |Equal weights initially|A/B test against full-context baseline with progressive complexity suite                |
|**Staleness decay curve**        |Exponential decay      |Compare linear, exponential, and logarithmic decay against long multi-turn conversations|
|**Output reservation percentage**|30% of context window  |Measure actual output sizes across query types; adjust reservation dynamically          |
|**Chunking size threshold**      |TBD (tokens)           |Test with varying input sizes; determine minimum size where chunking improves relevance |
|**Callback limit (V2)**          |2 callbacks max        |Compare hard limit vs. answer-stability termination                                     |

-----

## 13. Graph Population and Maintenance Strategies (Under Consideration)

The following approaches are candidates for how the graph gets initially populated from a codebase or knowledge base, and how it stays current over time. These are not mutually exclusive — the final implementation may combine several.

### 13.1 Structural Reference Nodes (Lazy Loading)

Content nodes store a **reference** (file path + line range + signature) rather than the actual content. The orchestration engine loads the real content on-demand via file read when the node scores high enough to include. This keeps the graph lightweight even for large codebases — a 50,000-line project might produce a graph.json of only a few hundred KB.

Example content node:
```json
{
  "id": "cn-auth-042",
  "type": "file_reference",
  "reference": { "file": "src/auth/login.ts", "lines": [23, 78], "signature": "async authenticateUser(credentials: AuthCredentials): Promise<AuthResult>" },
  "token_count_estimate": 340,
  "concepts": ["authentication", "login-flow"]
}
```

**Tradeoff**: Adds a file read at orchestration time. Content may have drifted from the reference if the file changed. Requires a freshness check or invalidation mechanism.

### 13.2 Tree-sitter for Baseline Index Generation

Use tree-sitter to extract function/class/method signatures across the codebase without loading full file contents. This produces the initial set of content nodes with structural references (per 13.1). Tree-sitter supports 48+ languages and extracts signatures in milliseconds.

This is the "baseline generation" path — run once to build the initial graph, then maintain incrementally. Output is deterministic and reproducible.

**Tradeoff**: Only captures structural elements (functions, classes, interfaces). Doesn't capture inline logic, comments with domain knowledge, or configuration files that lack parseable structure.

### 13.3 Git-Aware Incremental Updates

Track the last-indexed git commit hash per file. On subsequent indexing runs, only re-process files whose hash has changed since the last run. This converts a full O(n) reindex into a differential O(changed) update.

Implementation: store `{ "file": "src/auth/login.ts", "last_indexed_commit": "a3f9c2e" }` in graph metadata. On update, `git diff --name-only <last_commit>..HEAD` gives the changed file list. Only those files get re-indexed via tree-sitter and re-embedded.

**Tradeoff**: Requires git. Doesn't detect changes made outside git (unsaved edits, generated files). May need a fallback to file modification timestamps for non-git scenarios.

### 13.4 Flat-File Scale Boundaries

V1 uses graph.json for simplicity. Define concrete thresholds for when this becomes a bottleneck:
- Measure graph.json load/parse time at 1k, 5k, 10k, 25k, 50k nodes
- Identify the node count where load time exceeds 500ms (tentative threshold)
- This data informs the V2/V3 decision on graph database migration

Research reference: existing flat-file indexing tools (aider repo-map, Code-Index-MCP with SQLite) show practical limits around 10k-50k symbols before requiring structured storage.

### 13.5 Codebase Indexing as Primary Validation Domain

Code analysis is the primary validation domain (see Section 8.2 for the self-referential testing strategy). Code is ideal because it has well-defined structure (functions, classes, modules), measurable correctness (does the output compile and pass tests?), and existing tools to benchmark against (aider's repo-map, Code-Index-MCP, Serena).

The graph population strategies above (13.1–13.4) are designed to work together for codebase indexing: tree-sitter generates the baseline structural references (13.2), stored as lazy-loading reference nodes (13.1), maintained incrementally via git-aware updates (13.3), with flat-file scale monitored against defined boundaries (13.4).

Specific benchmark: given a bug report that touches 3 files across 2 modules in a 200-file project, does Loom load the right 3-5 content nodes out of hundreds, and does the resulting LLM output correctly identify and fix the bug?

-----

## 14. Related Work and Differentiation

Several existing projects address aspects of the context management problem. MemGPT/Letta implements hierarchical memory management for LLMs with tiered context (working memory, archival memory, recall memory). Loom differs by using a graph-based relevance model with multi-signal ranking rather than a fixed memory hierarchy. Standard RAG retrieves chunks by embedding similarity to the query. Loom extends this by maintaining relationship structure between content, considering multiple ranking signals beyond similarity, and making budget-aware loading decisions. LangChain/LlamaIndex provide retrieval and orchestration frameworks but typically operate at the document/chunk level without the concept-node abstraction layer that enables Loom’s orchestration decisions.

Loom’s key differentiator is the separation of concept nodes (for orchestration) from content nodes (for context loading), combined with a multi-signal ranking engine that considers relevance, recency, size, provenance, and graph structure simultaneously.

-----

## 15. Next Steps

### Prerequisite: Context-Structure-Research (External)

> **Loom development is blocked** until [[Context-Structure-Research]] Phases 2-3 produce a winning referencing strategy. Track progress via Beads tasks AIProjects-7qz (Phase 1.1), AIProjects-af9 (Phase 2), AIProjects-0he (Phase 3).

### Engine Development (when unblocked)

1. **Define the graph.json schema:** Formalize the node, edge, and metadata structures. The content node format should align with the winning strategy from research.
2. **Build the graph manager:** Node creation, edge creation, embedding generation via Ollama, and the similarity threshold logic.
3. **Build the orchestration engine:** Start with 2-signal scoring (semantic relevance + staleness), budget calculation, loading strategy, and prompt assembly with context manifest. Output format matches the winning referencing strategy.
4. **Validate against research baselines:** Loom's engine should match or exceed the best manual strategy results from context-structure-research Phase 3.
5. **Expand ranking signals:** Add hop distance, content size, provenance weight, link density — one at a time, measuring whether each improves results.
6. **Build input classifier** (if needed): Regex-based structural detection, lexical diversity scoring, chunking logic. May be deferred if the 2-subsystem core proves sufficient.
7. **Build post-processing indexer** (if needed): Background processing of LLM responses, graph updates, staleness management. Most valuable once cross-session persistence exists (V2).
8. **Tune parameters:** Empirically optimize similarity threshold, signal weights, and budget allocation.
