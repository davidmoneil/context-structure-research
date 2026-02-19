---
tags:
  - project/aiprojects
  - depth/deep
  - domain/ai
  - domain/infrastructure
  - domain/personal
created: 2026-01-02T15:12
updated: 2026-01-24T10:43
---
# Claude Code vs OpenCode Comparison

> **Purpose**: Feature comparison and migration assessment for AIProjects
> **Created**: 2026-01-02
> **Context**: Comprehensive review of AIProjects architecture against OpenCode capabilities
> **Related**: [[AIProjects Architecture Overview]]

---

## Executive Summary

AIProjects is a **production-grade AI infrastructure orchestration platform** with 23 hooks, 21 commands, 10+ agents, and comprehensive documentation. Most of what AIProjects does with Claude Code can be replicated in OpenCode, but with different trade-offs. Claude Code's tight Anthropic integration enables features like the Task tool with specialized subagents that OpenCode lacks, while OpenCode's multi-provider flexibility and open-source nature offer advantages in customization.

---

## Platform Overview

| Aspect | Claude Code | OpenCode |
|--------|-------------|----------|
| **Developer** | Anthropic | Community (now [Crush/CharmBracelet](https://github.com/charmbracelet/crush)) |
| **Language** | TypeScript | Go |
| **Status** | Active | Archived → Crush |
| **Model Support** | Claude only | Multi-provider (OpenAI, Claude, Gemini, Bedrock, etc.) |
| **Interface** | CLI + IDE integration | TUI (Bubble Tea) |
| **Pricing** | API usage | API usage (bring your own) |

---

## Core Feature Comparison

| Feature | Claude Code | OpenCode | Winner |
|---------|-------------|----------|--------|
| **Hooks System** | 23 custom JS hooks | No native hooks | Claude Code |
| **Custom Commands** | Markdown in `.claude/commands/` | Markdown in `.opencode/commands/` | Tie |
| **MCP Support** | Full (SSE + stdio) | Full (SSE + stdio) | Tie |
| **Subagents/Task Delegation** | Task tool with specialized agents | "agentic" tool for sub-tasks | Claude Code |
| **Permission Model** | Baseline + accumulated + deny | Enabled by default, approval dialog | Claude Code |
| **LSP Integration** | Native | Experimental | Claude Code |
| **Multi-Provider** | Claude only | 7+ providers | OpenCode |
| **Session Persistence** | Limited | SQLite database | OpenCode |
| **Auto-Compact** | Manual context management | 95% threshold auto-compact | OpenCode |
| **GitHub Actions** | Via skills | Native `/opencode` mentions | OpenCode |

---

## AIProjects Feature Portability

| AIProjects Feature | Claude Code Implementation | OpenCode Equivalent | Portable? |
|-------------------|---------------------------|---------------------|-----------|
| **23 Hooks** | `.claude/hooks/*.js` | No equivalent | No |
| **21 Commands** | `.claude/commands/*.md` | `.opencode/commands/*.md` | Yes |
| **10+ Agents** | `.claude/agents/*.md` + Task tool | `agentic` tool + skills | Partial |
| **MCP Gateway** | SSE connection in `.mcp.json` | SSE in `opencode.json` | Yes |
| **Memory MCP** | Knowledge graph persistence | Same via MCP | Yes |
| **paths-registry.yaml** | YAML config | JSON config | Yes (format change) |
| **CLAUDE.md Entry Point** | Automatic loading | `SKILL.md` or prompt template | Manual |
| **Audit Logging** | Hook-based automatic | No equivalent | No |
| **Secret Scanning** | PreToolUse hook | No equivalent | No |
| **Branch Protection** | PreToolUse hook | No equivalent | No |
| **Project Detection** | UserPromptSubmit hook | No equivalent | No |
| **Context Reminder** | PostToolUse hook | No equivalent | No |
| **Docker Validation** | PreToolUse hook | No equivalent | No |

---

## Detailed Capability Analysis

### 1. Hooks (Claude Code Advantage)

**Claude Code**: 23 JavaScript hooks across 4 event types
```
PreToolUse (10)  → Validate before execution
PostToolUse (8)  → React after execution
Notification (2) → Session lifecycle
UserPromptSubmit → Parse user input
```

**OpenCode**: No native hook system
- Cannot intercept tool calls
- Cannot inject context dynamically
- Cannot block operations based on custom rules

**Impact**: AIProjects' security features (secret scanning, credential guard, branch protection) **cannot be replicated** in OpenCode without forking the codebase.

### 2. Commands/Skills (Parity)

**Claude Code**:
```yaml
# .claude/commands/check-service.md
---
argument-hint: <service-name>
description: Health check for services
allowed-tools: Bash(docker:*), MCP(memory:*)
model: opus
---
```

**OpenCode**:
```markdown
<!-- .opencode/commands/check-service.md -->
# Check Service
Run health check for $SERVICE_NAME
...
```

Both support:
- Markdown-based command definitions
- Argument placeholders
- Hierarchical organization (subdirectories)

**Difference**: Claude Code's frontmatter supports `model`, `allowed-tools` constraints; OpenCode has simpler format.

### 3. Agent/Subagent System (Claude Code Advantage)

**Claude Code Task Tool**:
```javascript
// Spawns specialized agent with own context
Task({
  subagent_type: "feature-dev:code-reviewer",
  prompt: "Review this code...",
  run_in_background: true
})
```

- 9 built-in subagent types (Explore, Plan, code-architect, etc.)
- Custom agents with persistent memory
- Background execution with `TaskOutput` retrieval
- Full context isolation

**OpenCode `agentic` Tool**:
- Single delegation capability
- No specialized subtypes
- No persistent agent memory
- No background execution

**Impact**: AIProjects' agent system (deep-research, service-troubleshooter, docker-deployer) would need significant reimplementation.

### 4. MCP Integration (Parity)

**Claude Code** `.mcp.json`:
```json
{
  "mcpServers": {
    "mcp-gateway": {
      "type": "sse",
      "url": "http://localhost:8080/sse"
    }
  }
}
```

**OpenCode** `opencode.json`:
```json
{
  "mcpServers": {
    "mcp-gateway": {
      "transport": "sse",
      "url": "http://localhost:8080/sse"
    }
  }
}
```

Both support:
- SSE and stdio transports
- Tool discovery
- Permission integration
- External service connections

**Result**: MCP Gateway, Memory MCP, Filesystem MCP would work identically.

### 5. Permission Model

**Claude Code** (3-layer):
```
DENY (always blocked)
  → BASELINE (settings.json: 130 rules)
    → ACCUMULATED (settings.local.json: 450+ rules)
      → USER PROMPT (new operations)
```

**OpenCode** (simple):
```
All tools enabled by default
  → Permission dialog on execution
    → Single/session approval
```

**Difference**: Claude Code's accumulating permissions reduce friction over time; OpenCode asks every session.

### 6. Multi-Provider (OpenCode Advantage)

**OpenCode Providers**:
- OpenAI (GPT-4.1, GPT-4o, O1/O3)
- Anthropic Claude (3.7, 4 Sonnet, 4 Opus)
- Google Gemini (2.5, 2.0 Flash)
- AWS Bedrock
- Groq
- Azure OpenAI
- Google VertexAI
- Self-hosted models

**Claude Code**: Claude models only

**Impact**: If you want to use Gemini's 1M context window for large refactors, OpenCode enables that; Claude Code doesn't.

---

## Migration Assessment

### What Would Transfer Easily

| Component | Migration Effort | Notes |
|-----------|------------------|-------|
| Commands (21) | Low | Reformat markdown, change syntax |
| MCP configs | Low | JSON format change |
| paths-registry.yaml | Low | Convert to JSON |
| Documentation | None | Already portable |
| Shell scripts | None | Already portable |

### What Would Require Significant Work

| Component | Migration Effort | Notes |
|-----------|------------------|-------|
| Hooks (23) | High | No equivalent - would need external wrapper |
| Agent system | High | Rewrite with `agentic` tool limitations |
| Permission baseline | Medium | No accumulated permissions |
| Context loading model | Medium | No dynamic injection |
| Session exit procedure | Medium | No hook enforcement |

### What Cannot Be Replicated

| Feature | Reason |
|---------|--------|
| PreToolUse hooks | OpenCode lacks interception |
| Secret scanning | No pre-commit hook point |
| Branch protection | No git operation hooks |
| Dynamic context injection | No PostToolUse triggers |
| Specialized subagents | No Task tool equivalent |
| Background agent execution | No parallel task system |

---

## Recommendations

### If Staying with Claude Code

1. **Fix the 2 identified issues**:
   - Move credentials to env vars in `weekly-docker-restart.sh`
   - Add Docker daemon check in `docker-validator.js`

2. **Consider adding**:
   - Unit tests for complex hook logic
   - Pre-commit hook using existing secret-scanner logic
   - "Known Issues" section to Architecture Overview

### If Considering OpenCode

1. **Understand limitations**:
   - No hook system means no automatic security enforcement
   - Agent system significantly less capable
   - Permission model less sophisticated

2. **Benefits to consider**:
   - Multi-provider flexibility (use best model per task)
   - Auto-compact for long sessions
   - Native GitHub Actions integration
   - Open-source (can fork and customize)

3. **Migration path**:
   - Start with commands (easiest)
   - Port MCP configurations
   - Implement external script wrapper for critical "hooks"
   - Accept agent limitations or implement custom solution

### Hybrid Approach

You could use both:
- **Claude Code** for AIProjects hub (complex orchestration, security)
- **OpenCode** for specific projects where multi-provider or Gemini context helps
- Share MCP servers between both

---

## Summary

| Dimension | Claude Code | OpenCode |
|-----------|-------------|----------|
| **Best For** | Complex orchestration, security-first, single provider | Multi-provider flexibility, simple workflows |
| **AIProjects Fit** | Excellent (built for it) | Partial (missing hooks, limited agents) |
| **Infrastructure Management** | Full capability | Reduced capability |
| **Security Enforcement** | Native via hooks | Requires external tooling |
| **Portability** | ~40% of features | Receives ~40% of features |

**Bottom Line**: AIProjects is deeply integrated with Claude Code's unique features (hooks, Task tool, subagents). While ~40% of functionality could port to OpenCode, the security automation and agent orchestration that make AIProjects powerful would require significant external tooling to replicate.

---

## Code Quality Issues Identified

During this review, the code reviewer agent identified 2 high-confidence issues:

### Issue 1: Hardcoded Credentials (Confidence: 95%)

**File**: `Scripts/weekly-docker-restart.sh` (lines 19-21)

```bash
# PROBLEM - Visible in git history
WEBHOOK_URL="https://n8n.theklyx.space/webhook/..."
WEBHOOK_SECRET="ebbaafd30a9ed2631e90f8f90b68fef9e112ab622e9d039a"
```

**Fix**: Move to `~/.config/weekly-restart/webhook-*` and source from environment variables.

### Issue 2: Missing Docker Error Handling (Confidence: 85%)

**File**: `.claude/hooks/docker-validator.js`

- `getExistingNetworks()` returns empty array when Docker daemon unavailable
- Valid external networks then flagged as missing (false positives)

**Fix**: Return `null` when Docker unreachable, skip network validation.

---

## Sources

- [OpenCode GitHub Repository](https://github.com/opencode-ai/opencode)
- [OpenCode CLI Documentation](https://opencode.ai/docs/cli/)
- [OpenCode Tools Documentation](https://opencode.ai/docs/tools/)
- [OpenCode MCP Tool Integration](https://github.com/frap129/opencode-mcp-tool)
- [Claude Code Alternatives Comparison](https://www.qodo.ai/blog/claude-code-alternatives/)
- [Agentic CLI Tools Comparison](https://research.aimultiple.com/agentic-cli/)

---

> [!note] OpenCode Status
> OpenCode has been archived and development continues as [Crush](https://github.com/charmbracelet/crush) under CharmBracelet's stewardship.

---

*Document created: 2026-01-02*
