---
tags:
  - status/draft
  - depth/deep
  - domain/ai
  - domain/dnd
  - domain/mechanics
created: 2026-01-21T19:07
updated: 2026-01-24T10:39
---
# Fabric Integration Analysis for AIProjects

**Date:** 2026-01-21
**Project:** [danielmiessler/fabric](https://github.com/danielmiessler/fabric)
**Purpose:** Evaluate fabric as a potential addition to AIProjects infrastructure

---

## Executive Summary

**Fabric** is an open-source AI augmentation framework (38k+ GitHub stars) that provides:
- **234 curated prompt templates** ("patterns") for common tasks
- **Multi-LLM support** (OpenAI, Anthropic, Ollama, Gemini, etc.)
- **CLI + REST API** interfaces
- **Ollama compatibility mode** (can replace Ollama API)

**Verdict:** High value for specific use cases, but requires thoughtful integration strategy.

---

## What is Fabric?

Fabric organizes prompts by real-world task, solving AI's "integration problem" - making AI capabilities accessible in everyday workflows.

### Key Concept: Patterns

Patterns are structured Markdown prompts with:
- `IDENTITY and PURPOSE` - Expert persona definition
- `STEPS` - Processing instructions
- `OUTPUT SECTIONS` - Structured result format
- `OUTPUT INSTRUCTIONS` - Quality guidelines

**Example - summarize pattern:**
```markdown
# IDENTITY and PURPOSE
You are an expert content summarizer...

# OUTPUT SECTIONS
- ONE SENTENCE SUMMARY: 20 words
- MAIN POINTS: 10 items, 16 words each
- TAKEAWAYS: 5 best takeaways

# OUTPUT INSTRUCTIONS
- You only output human readable Markdown
- Output numbered lists, not bullets
```

---

## Architecture Overview

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| CLI | Go binary | Primary interface |
| REST API | Gin (Go) | HTTP interface + SSE streaming |
| Patterns | Markdown files | Prompt templates |
| Plugins | Go interfaces | AI provider abstraction |
| Storage | Filesystem | Sessions, patterns, config |

### Supported AI Providers

- OpenAI (GPT-4, o1, etc.)
- Anthropic (Claude)
- Google Gemini
- Ollama (local)
- Azure OpenAI
- Amazon Bedrock
- Perplexity
- Together AI
- Venice AI
- And 10+ more via OpenAI-compatible adapter

### Data Flow

```
User Input → CLI/API → Pattern Loading → Variable Substitution → AI Provider → Streaming Response
```

---

## Pattern Library Analysis

### Categories (234 Total)

| Category | Count | Examples |
|----------|-------|----------|
| Code Analysis | 19 | `review_code`, `explain_code`, `explain_project` |
| Security | 27 | `analyze_threat_report`, `create_stride_threat_model`, `analyze_logs` |
| Knowledge Extraction | 40 | `extract_wisdom`, `extract_insights`, `extract_recommendations` |
| Summarization | 21 | `summarize`, `summarize_meeting`, `summarize_paper` |
| Documentation | 24 | `create_design_document`, `create_prd`, `improve_writing` |
| Visualization | 10 | `create_mermaid_visualization`, `create_conceptmap` |
| Analysis | 23 | `analyze_paper`, `analyze_presentation`, `rate_ai_response` |
| Creation | 30 | `create_keynote`, `create_quiz`, `create_reading_plan` |
| Personal Dev | 15 | TELOS patterns for goal tracking |

### Top Patterns for AIProjects

**Code & Development:**
1. `review_code` - Principal Engineer-level code review
2. `explain_project` - C4-style project documentation
3. `summarize_git_diff` - Conventional commit messages
4. `write_pull-request` - PR description generation

**Infrastructure:**
5. `analyze_logs` - Server log analysis
6. `analyze_terraform_plan` - IaC change analysis
7. `create_stride_threat_model` - Security design reviews

**Knowledge Management:**
8. `extract_wisdom` - Content analysis (articles, videos, podcasts)
9. `extract_recommendations` - Action items
10. `summarize_meeting` - Meeting notes

**Documentation:**
11. `create_mermaid_visualization` - Architecture diagrams
12. `create_design_document` - System design docs
13. `improve_writing` - Content refinement

---

## Integration Opportunities

### Option 1: Pattern Mining (LOW EFFORT, HIGH VALUE)

**What:** Extract best patterns and adapt to Claude Code skills/commands

**How:**
1. Copy high-value patterns to `.claude/skills/` or `.claude/agents/`
2. Adapt format to match AIProjects conventions
3. Use directly in Claude Code workflows

**Pros:**
- Zero runtime overhead
- Full Claude Code integration (context, tools, memory)
- Cherry-pick only useful patterns

**Cons:**
- Manual maintenance for pattern updates
- Lose fabric's multi-LLM capability

**Recommended patterns to adapt:**
- `analyze_logs` → Infrastructure troubleshooting skill
- `create_mermaid_visualization` → Architecture documentation skill
- `extract_wisdom` → Content processing agent
- `summarize_git_diff` → Enhanced commit workflow

---

### Option 2: Fabric as Docker Service (MEDIUM EFFORT, HIGH VALUE)

**What:** Run fabric REST API as a service

**How:**
```yaml
# docker-compose.yaml
services:
  fabric:
    image: danielmiessler/fabric:latest
    ports:
      - "8080:8080"
    volumes:
      - ./fabric-config:/root/.config/fabric
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: ["--serve", "--port", "8080"]
```

**API Usage:**
```bash
# List patterns
curl http://localhost:8080/patterns

# Use a pattern
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [{
      "userInput": "your content here",
      "patternName": "summarize",
      "model": "gpt-4"
    }],
    "stream": true
  }'
```

**Pros:**
- Full pattern library available
- Multi-LLM support
- Can integrate with n8n workflows
- Ollama compatibility (any Ollama client works)

**Cons:**
- Another service to maintain
- Separate from Claude Code context
- API key management

---

### Option 3: CLI Integration (LOW EFFORT, MEDIUM VALUE)

**What:** Install fabric CLI and call from Claude Code bash commands

**How:**
```bash
# Install
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-amd64 \
  -o /usr/local/bin/fabric
chmod +x /usr/local/bin/fabric
fabric --setup

# Use from Claude Code
echo "content" | fabric --pattern summarize --model gpt-4
cat logfile.txt | fabric --pattern analyze_logs
```

**Pros:**
- Simple installation
- Can pipe content directly
- Works with local Ollama

**Cons:**
- Requires API key setup
- Sequential processing only
- Less integration than native skills

---

### Option 4: Ollama Replacement (SPECIALIZED)

**What:** Use fabric as Ollama proxy to get patterns as "models"

**How:**
```bash
fabric --serve --port 11434  # Ollama-compatible endpoint
# Now any Ollama client sees patterns as models
# e.g., "summarize:latest", "analyze_logs:latest"
```

**Use Case:** Replace Ollama in existing workflows to get fabric patterns + any backend LLM

---

## Comparison with AIProjects

| Aspect | AIProjects | Fabric |
|--------|------------|--------|
| **Philosophy** | Claude Code-native, context-aware | Standalone CLI, universal |
| **LLM Support** | Claude (Anthropic) | 15+ providers |
| **Prompt System** | Skills, agents, commands | Patterns (Markdown) |
| **Context** | Full session context, tools, memory | Input-only, stateless |
| **Extensibility** | Custom skills, hooks | Custom patterns, extensions |
| **Local LLMs** | Limited | Full Ollama support |

### What Fabric Does Better

1. **Pattern Library** - 234 battle-tested prompts vs creating from scratch
2. **Multi-LLM** - Easy switching between providers
3. **Local LLMs** - First-class Ollama support
4. **REST API** - Clean HTTP interface for n8n/automation

### What AIProjects Does Better

1. **Context** - Full conversation + codebase awareness
2. **Tools** - File operations, git, MCP servers
3. **Memory** - Persistent knowledge graph
4. **Integration** - Native Claude Code features (skills, hooks, agents)

---

## Recommendation

### Primary Recommendation: Hybrid Approach

**Phase 1: Pattern Mining (Immediate)**
- Extract 10-15 most valuable patterns
- Adapt to Claude Code skill format
- Test in daily workflows

**Candidate patterns:**
```
analyze_logs         → /infrastructure-ops enhancement
summarize_meeting    → Session documentation
extract_wisdom       → Content processing agent
create_mermaid_vis   → Architecture documentation
review_code          → Code review skill
```

**Phase 2: Docker Service (If patterns prove valuable)**
- Deploy fabric REST API
- Integrate with n8n for automation workflows
- Use for bulk processing tasks

**Phase 3: Consider for specific use cases:**
- Ollama replacement if using local LLMs
- Multi-LLM workflows needing provider switching

---

## Implementation Checklist

### Phase 1: Pattern Mining

- [ ] Clone fabric repo: `~/Code/fabric-review`
- [ ] Review top patterns (see list above)
- [ ] Create skill adapters:
  - [ ] `.claude/skills/fabric-adapted/analyze-logs/`
  - [ ] `.claude/skills/fabric-adapted/extract-wisdom/`
- [ ] Test in daily workflows
- [ ] Document which patterns are most useful

### Phase 2: Docker Deployment

- [ ] Add fabric to `mydocker/` compose
- [ ] Configure API keys (use existing Anthropic key)
- [ ] Create n8n integration workflow
- [ ] Document API endpoints in AIProjects

### Optional: CLI Installation

```bash
# One-liner install
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-amd64 \
  -o /usr/local/bin/fabric && chmod +x /usr/local/bin/fabric
```

---

## Key Pattern Deep Dives

### analyze_logs

**Purpose:** Identify patterns, anomalies, and insights from server logs

**Output sections:**
- LOG OVERVIEW
- PATTERNS
- ANOMALIES
- SECURITY CONCERNS
- RECOMMENDATIONS

**AIProjects Use:** Docker/service troubleshooting, health check enhancement

---

### extract_wisdom

**Purpose:** Extract insights, ideas, quotes, habits, facts from any content

**Output sections:**
- SUMMARY (25 words)
- IDEAS (20 items, 16 words each)
- INSIGHTS (10 items, 16 words)
- QUOTES (15 items)
- HABITS (15 items)
- FACTS (15 items)
- REFERENCES (all mentioned)
- RECOMMENDATIONS (15 items)

**AIProjects Use:** Processing technical talks, documentation, blog posts

---

### create_mermaid_visualization

**Purpose:** Convert concepts to detailed Mermaid diagrams

**Output:** Clean Mermaid code (no markdown fencing)

**AIProjects Use:** Architecture documentation, system diagrams

---

### summarize_meeting

**Purpose:** Structured meeting transcript analysis

**Output sections:**
- MEETING OVERVIEW
- KEY DECISIONS
- ACTION ITEMS (with owners)
- OPEN QUESTIONS
- FOLLOW-UP NEEDED

**AIProjects Use:** Session notes, standup documentation

---

## Resources

- **GitHub:** https://github.com/danielmiessler/fabric
- **Documentation:** https://github.com/danielmiessler/fabric/tree/main/docs
- **DeepWiki:** https://deepwiki.com/danielmiessler/fabric
- **Local clone:** `~/Code/fabric-review`
- **Pattern catalog:** `~/Code/fabric-review/data/patterns/`

---

## Questions to Explore

1. Which patterns would save the most time in daily workflows?
2. Is the REST API latency acceptable for interactive use?
3. Do we need multi-LLM support, or is Claude sufficient?
4. Could fabric patterns enhance n8n automation workflows?

---

**Next Steps:**
1. Review the top patterns listed above
2. Try one or two patterns via CLI
3. Decide on integration approach based on actual usage

---

## Hands-On Testing Results (2026-01-21)

### Setup

- **CLI**: `~/bin/fabric` v1.4.386
- **LLM Backend**: Local Ollama (qwen2.5:32b for complex, qwen2.5:7b-instruct for fast)
- **Config**: `~/.config/fabric/.env` + `~/.config/fabric/patterns/` (234 patterns)

### Test Results

| Pattern | Input | Speed | Quality |
|---------|-------|-------|---------|
| `summarize` | Sample text | ~10s | Good |
| `analyze_logs` | Prometheus logs (20 lines) | ~90s (32b) | Excellent - structured analysis with recommendations |
| `summarize_git_diff` | Git diff (168 lines) | ~15s (7b) | Excellent - clean conventional commit format |
| `review_code` | JS function | ~60s (7b) | Very good - prioritized recommendations |
| `extract_wisdom` | Obsidian note | ~30s (7b) | Good - extracted ideas, insights, quotes |
| `create_tags` | Obsidian note | ~10s (7b) | OK - messy format |

### Key Findings

1. **Local Ollama works well** - Both 32B and 7B models produce useful output
2. **Speed vs Quality tradeoff** - 7b-instruct is faster for simple patterns, 32b better for complex analysis
3. **Streaming helps** - `--stream` flag shows progress and avoids timeouts
4. **Some patterns timeout** - Large inputs with complex patterns may deadlock on 32B model

### Example Usage

```bash
# Log analysis
docker logs prometheus --tail 50 | ~/bin/fabric --pattern analyze_logs --stream

# Commit message
git diff HEAD~1 | ~/bin/fabric --pattern summarize_git_diff

# Code review (use faster model)
cat file.js | ~/bin/fabric --pattern review_code --model qwen2.5:7b-instruct

# Extract insights from notes
cat note.md | ~/bin/fabric --pattern extract_wisdom --model qwen2.5:7b-instruct
```

---

*Analysis conducted: 2026-01-21*
*Claude Code session: AIProjects fabric integration review*
