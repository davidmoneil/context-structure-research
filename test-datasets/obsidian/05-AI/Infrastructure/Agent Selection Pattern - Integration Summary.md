---
tags:
  - project/aiprojects
  - domain/ai
  - domain/infrastructure
  - depth/standard
  - depth/deep
created: 2026-01-01T00:44
updated: 2026-01-24T10:43
---
# Agent Selection Pattern - Integration Summary

**Date**: 2026-01-01
**Project**: AIProjects (Claude Code)
**Type**: Design Pattern Documentation

---

## Overview

Created a comprehensive decision framework for choosing between automation approaches in Claude Code. The pattern addresses the question: "When should I use a custom agent vs a built-in subagent vs a skill vs direct tools?"

## Two Agent Types

### Custom Agents (`/agent <name>`)
Your infrastructure-specific agents in `.claude/agents/`:
- **Persistent memory** - learns and improves over time
- **Session logging** - full transcript of work
- **Results files** - polished outputs
- **Manual invocation** - you decide when to use them

**Examples**: deep-research, service-troubleshooter, docker-deployer

### Built-in Subagents (Automatic)
Plugin-based agents invoked automatically:
- **No persistence** - fresh each time
- **Optimized for task type** - specialized capabilities
- **Automatic invocation** - Claude Code decides when

**Examples**: Explore, Plan, feature-dev:code-architect, feature-dev:code-reviewer

## Decision Matrix

| Task Type | Use This |
|-----------|----------|
| Code/architecture work | Built-in (feature-dev:*) |
| Recurring infrastructure | Custom agent |
| Quick repeatable operation | Skill/slash command |
| Simple one-off | Direct tools |

## Installed Plugins

### feature-dev
- `code-architect` - Design feature architectures
- `code-explorer` - Analyze existing features
- `code-reviewer` - Review code quality

### hookify
- `conversation-analyzer` - Create hooks from patterns

### agent-sdk-dev
- `agent-sdk-verifier-py` - Verify Python apps
- `agent-sdk-verifier-ts` - Verify TypeScript apps

## Integration with PARC

Added to the **Assess** phase of the PARC pattern:

```
ASSESS:
  [x] Searched patterns/ for relevant patterns
  [x] Checked workflows/ for applicable workflow
  [x] Searched Memory MCP for similar past work
  [NEW] Should I use an agent for this?
      - Code work? → Built-in subagent
      - Recurring task? → Custom agent
      - Quick operation? → Skill
      - One-off? → Direct tools
```

## Files Modified

| File | Change |
|------|--------|
| `agent-selection-pattern.md` | NEW - Full decision framework |
| `CLAUDE.md` | Added Quick Link, Built-in Subagents section |
| `prompt-design-review.md` | Added agent selection to Assess phase |
| `agent-system.md` | Added Built-in Subagents section |
| `patterns/_index.md` | Added new pattern entry |
| `context/_index.md` | Updated Agent System, Recent Updates |

## Links

- Pattern file: `.claude/context/patterns/agent-selection-pattern.md`
- Agent system docs: `.claude/context/systems/agent-system.md`
- Session notes: `knowledge/notes/session-20260101-agent-selection-pattern.md`

---

#claude-code #agents #patterns #ai-infrastructure
