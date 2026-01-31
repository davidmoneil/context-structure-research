# Prior Art: Code Indexing & Context Optimization Research

**Researched**: 2026-01-30
**Purpose**: Survey existing approaches to the problem we're solving

---

## Summary

This problem space is actively being explored by industry (Cursor, Windsurf, Qodo) and academia. Key finding: **no one has published systematic research on optimal file structure for LLM context** - most focus is on retrieval/indexing algorithms, not source organization.

---

## Industry Approaches

### Cursor's Architecture

[Source: PixelsTech - Understanding Cursor and Windsurf's Code Indexing Logic](https://www.pixelstech.net/article/1734832711-understanding-cursor-and-windsurf-s-code-indexing-logic)

- **Vector database indexing**: Entire project indexed into vector store
- **Two-stage retrieval**: Vector search → AI re-ranking
- **Emphasis on comments/docstrings**: Encoder model specially weights documentation
- **Continuous reindexing**: Updates as files change
- **Cloud-powered, privacy-masked**: Embeddings stored, not plaintext

Key insight: Cursor's encoder model "specially emphasizes comments and docstrings to better capture each file's purpose." This validates our Strategy C (function + keywords).

### Windsurf's Architecture

[Source: DataCamp - Windsurf vs Cursor Comparison](https://www.datacamp.com/blog/windsurf-vs-cursor)

- **RAG-based context engine**: Automatically indexes entire codebase
- **SWE-grep models**: 20x faster than traditional RAG, "browses" codebase
- **Real-time context awareness**: Reacts to edits, adjusts plan
- **Enterprise scale focus**: Designed for millions of lines of code

Key insight: Windsurf uses "LLM-based search that outperforms traditional embedding-based search for code." This suggests semantic understanding matters more than keyword matching.

### Comparison

| Aspect | Cursor | Windsurf |
|--------|--------|----------|
| Context selection | Developer-curated (@ symbols) | Automatic (Cascade awareness) |
| File reading | First 250 lines default | Locate file, selective reading |
| Scale | Smaller codebases | Enterprise-scale designed |

---

## RAG for Codebases Research

### AST-Based Chunking

[Source: Medium - RAG for LLM Code Generation using AST-Based chunking](https://medium.com/@vishnudhat/rag-for-llm-code-generation-using-ast-based-chunking-for-codebase-c55bbd60836e)

Traditional text chunking fails for code. AST-based approaches:
- Parse code into Abstract Syntax Tree
- Extract meaningful units (functions, classes, methods)
- Preserve syntactic integrity of chunks
- Enable varying granularity (class-level vs method-level)

**Relevance to our research**: Our Strategy C (file + functions + keywords) aligns with method-level chunking. AST parsing could auto-generate our indexes.

### Meta-RAG / Hierarchical Retrieval

[Source: arXiv - Meta-RAG on Large Codebases Using Code Summarization](https://arxiv.org/html/2508.02611v1)

- Uses **summaries at different hierarchical levels** (file, class, function)
- LLM starts at higher levels, hones in on lower levels
- Summaries "convey more information in fewer tokens"

**Relevance**: Validates our Strategy E (semantic grouping) and Combo approaches. Hierarchical summaries = our architecture + function indexes.

### Two-Stage Retrieval

[Source: Qodo - Evaluating RAG for Large-Scale Codebases](https://www.qodo.ai/blog/evaluating-rag-for-large-scale-codebases/)

1. Initial retrieval from vector store
2. LLM filters and ranks results by relevance

**Relevance**: Claude Code does something similar - lists files, then selects. Our indexes help Stage 1 (discovery).

### Specialized Chunking by File Type

[Source: Qodo - RAG for a Codebase with 10k Repos](https://www.qodo.ai/blog/rag-for-large-scale-code-repos/)

Different file types need different strategies:
- Code files: AST-based chunking
- OpenAPI specs: Chunk by endpoint
- Config files: Chunk by section

**Relevance**: Our Phase 2 should consider file type in index strategy.

---

## Claude Code Best Practices (Official)

### CLAUDE.md Guidelines

[Source: Anthropic - Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
[Source: Claude Blog - Using CLAUDE.MD files](https://claude.com/blog/using-claude-md-files)

- **100-200 lines max** for CLAUDE.md
- Move details to per-folder CLAUDE.md files
- Include: commands, style guidelines, key files, testing instructions
- Context window fills fast; performance degrades as it fills

### Hierarchy Support

- Root CLAUDE.md (always loaded)
- Folder-level CLAUDE.md (loaded on demand)
- Monorepo support (multiple CLAUDE.md files)

**Relevance**: Validates flat structure. Per-folder files = our shallow structure. Official guidance says "keep it short."

---

## Code Summarization Research

### LlamaIndex Document Summary Index

[Source: LlamaIndex Blog - A New Document Summary Index](https://www.llamaindex.ai/blog/a-new-document-summary-index-for-llm-powered-qa-systems-9a32ece2f9ec)

- Extract unstructured summary for each document
- Look up documents by summary relevance to query
- LLM reasoning > embedding-based lookup for relevance

**Relevance**: Our V5.1/V5.2 (summaries) approach is similar. Our finding that summaries don't help as much as keywords suggests embedding-based may work better for Claude Code's discovery phase.

### Multi-Agent Documentation Systems

[Source: Springer - Automated summarization of software documents](https://link.springer.com/article/10.1007/s10515-025-00588-4)

- LLM-based multi-agent systems for documentation
- Teacher-Student architecture for summary generation
- Focus on relevance and precision

**Relevance**: Could use multi-agent approach to generate our indexes automatically.

---

## Context Window Optimization

### Dynamic Context Selection

[Source: Qodo - Understanding Context Window](https://www.qodo.ai/blog/context-windows/)

- Dynamically adjust context to relevant code structures
- Asymmetric context loads
- Reduce token usage by 70% by sending only relevant class/method/dependencies

**Relevance**: Our research confirms this - flat structure allows better dynamic selection.

### Chunk Strategies

[Source: Medium - How I Solved the Biggest Problem with AI Coding Assistants](https://medium.com/@timbiondollo/how-i-solved-the-biggest-problem-with-ai-coding-assistants-and-you-can-too-aa5e5af80952)

- Create `./context/` directory with state.md, schema.md
- Define purpose, parameters, return values without code
- Split requests into multiple steps

**Relevance**: Similar to our Strategy D (entry points) - task-oriented organization.

---

## Gaps in Existing Research

### What's NOT being studied:

1. **Optimal file structure for discovery** - Everyone focuses on retrieval algorithms, not source organization
2. **Index overhead vs accuracy tradeoff** - No one measuring when indexes hurt more than help
3. **Scale thresholds** - At what size do strategies break down?
4. **Empirical testing** - Most claims are theoretical; few controlled experiments

### Our Unique Contribution:

- **Controlled experiments** with ground-truth questions
- **Measuring index overhead** (V5.5 hurt at 622K)
- **Structure comparison** (flat vs nested, quantified)
- **Practical recommendations** based on data, not theory

---

## Implications for Phase 2

### Validated Approaches (worth testing):

1. **AST-based function extraction** → Auto-generate Strategy C
2. **Hierarchical summaries** → Combo 2 (file keywords + semantic groups)
3. **Two-stage retrieval awareness** → Structure aids Stage 1 discovery

### Questionable Approaches (Phase 1 findings suggest issues):

1. **Dense summaries** → Our V5.2 (5-sentence) hurt accuracy
2. **Combined indexes** → Noise problem at scale
3. **Deep hierarchies** → Flat consistently wins

### New Ideas to Consider:

1. **File-type aware indexing** → Different strategies for .ts, .py, .yaml
2. **LLM-generated descriptions** → Use Haiku to describe each function
3. **Dependency graph indexing** → What imports what, what calls what

---

## Sources

### Industry
- [Anthropic - Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Claude Blog - Using CLAUDE.MD files](https://claude.com/blog/using-claude-md-files)
- [PixelsTech - Understanding Cursor and Windsurf's Code Indexing Logic](https://www.pixelstech.net/article/1734832711-understanding-cursor-and-windsurf-s-code-indexing-logic)
- [DataCamp - Windsurf vs Cursor Comparison](https://www.datacamp.com/blog/windsurf-vs-cursor)
- [Qodo - RAG for Large-Scale Code Repos](https://www.qodo.ai/blog/rag-for-large-scale-code-repos/)
- [Qodo - Evaluating RAG for Large-Scale Codebases](https://www.qodo.ai/blog/evaluating-rag-for-large-scale-codebases/)
- [Qodo - Understanding Context Windows](https://www.qodo.ai/blog/context-windows/)

### Academic/Research
- [arXiv - Meta-RAG on Large Codebases](https://arxiv.org/html/2508.02611v1)
- [arXiv - Retrieval-Augmented Code Generation Survey](https://arxiv.org/pdf/2510.04905)
- [LlamaIndex - Document Summary Index](https://www.llamaindex.ai/blog/a-new-document-summary-index-for-llm-powered-qa-systems-9a32ece2f9ec)
- [Springer - Automated summarization of software documents](https://link.springer.com/article/10.1007/s10515-025-00588-4)
- [ICSE - Source Code Summarization in the Era of LLMs](https://wssun.github.io/papers/2025-ICSE-LLMs4CodeSum.pdf)

### Practitioner
- [Medium - RAG for LLM Code Generation using AST-Based chunking](https://medium.com/@vishnudhat/rag-for-llm-code-generation-using-ast-based-chunking-for-codebase-c55bbd60836e)
- [Medium - How I Solved the Biggest Problem with AI Coding Assistants](https://medium.com/@timbiondollo/how-i-solved-the-biggest-problem-with-ai-coding-assistants-and-you-can-too-aa5e5af80952)
- [Substack - The Hidden Algorithms Powering Your Coding Assistant](https://diamantai.substack.com/p/the-hidden-algorithms-powering-your)

---

*Research compiled: 2026-01-30*
