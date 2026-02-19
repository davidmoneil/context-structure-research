---
tags:
  - project/aiprojects
  - domain/ai
  - domain/infrastructure
  - depth/standard
  - depth/deep
created: 2026-01-02T13:05
updated: 2026-01-24T10:40
---
# Design Pattern Terminology

**Purpose**: Define how design patterns are used within the AI Infrastructure projects (AIProjects, AIFred).

**Created**: 2026-01-02
**Last Updated**: 2026-01-02

---

## What is a Design Pattern?

A **design pattern** in this context is a documented, reusable solution to a recurring challenge in AI-assisted infrastructure management. Unlike software design patterns (which focus on code structure), these patterns focus on:

- **Workflow decisions**: When to use which tool or approach
- **Configuration strategies**: How to set up systems for optimal use
- **Operational procedures**: Steps to follow in specific scenarios
- **Rule enforcement**: What's mandatory vs. guidance

---

## Pattern Categories

### 1. Selection Patterns

Patterns that help choose between alternatives.

| Pattern | Purpose | File |
|---------|---------|------|
| **Agent Selection Pattern** | Choose between custom agents, built-in subagents, skills, or direct tools | `agent-selection-pattern.md` |
| **Model Selection Standard** | When to use Opus vs Sonnet vs Haiku | `model-selection.md` |

### 2. Loading/Configuration Patterns

Patterns that define how systems are configured and loaded.

| Pattern | Purpose | File |
|---------|---------|------|
| **MCP Loading Strategy** | Always-On vs On-Demand vs Isolated MCP servers | `mcp-loading-strategy.md` |

### 3. Storage Patterns

Patterns that define where and when to store information.

| Pattern | Purpose | File |
|---------|---------|------|
| **Memory Storage Pattern** | When/how to store findings in Memory MCP | `memory-storage-pattern.md` |

### 4. Process Patterns

Patterns that define step-by-step procedures.

| Pattern | Purpose | File |
|---------|---------|------|
| **PARC Design Review** | Pre-implementation check: Prompt → Assess → Relate → Create | `prompt-design-review.md` |
| **Session Exit Procedure** | Standard workflow for ending sessions | `session-exit-procedure.md` |

---

## Key Terminology

### Rule Types

| Term | Definition | Enforcement |
|------|------------|-------------|
| **Hard Rule** | Behavior that ALWAYS executes or is ALWAYS blocked | Hooks, settings, denylists |
| **Soft Rule** | Guidance that should be followed but doesn't block | CLAUDE.md, context files |

### MCP Loading Strategies

| Strategy | Definition | Token Impact |
|----------|------------|--------------|
| **Always-On** | MCP loaded at every session start | Always in context |
| **On-Demand** | MCP disabled by default, enabled for one session, auto-reverts | Only when enabled |
| **Isolated** | MCP never in main session, spawns separate process | Zero in main session |

### Session States

| Status | Symbol | Meaning |
|--------|--------|---------|
| **Idle** | 🟢 | No active work |
| **Active** | 🟡 | Work in progress |
| **Blocked** | 🔴 | Waiting on dependency |
| **Checkpoint** | 🔵 | Saved state for MCP restart |

### Severity Levels

| Level | Symbol | Use For |
|-------|--------|---------|
| **CRITICAL** | `[X]` | Immediate action required |
| **HIGH** | `[!]` | Address within 24h |
| **MEDIUM** | `[~]` | Address this week |
| **LOW** | `[-]` | Nice to fix |

---

## Pattern Structure

Each pattern document follows this structure:

```markdown
# Pattern Name

**Created**: YYYY-MM-DD
**Status**: Active | Draft | Deprecated
**Applies To**: Projects where pattern is relevant

---

## Overview
Brief description of what the pattern solves.

## The Pattern
Detailed explanation with diagrams/tables.

## Decision Criteria
When to use this pattern vs. alternatives.

## Implementation
How to apply the pattern.

## Enforcement
Hard rules vs. soft rules related to this pattern.

## Related Documentation
Links to related patterns and docs.

## Changelog
History of pattern updates.
```

---

## How Patterns Are Enforced

### Hard Enforcement (Automatic)

- **Hooks**: JavaScript hooks in `.claude/hooks/` that run on events
- **Settings**: `settings.json` / `settings.local.json` denylists
- **Exit Procedures**: Required steps in session exit workflow

### Soft Enforcement (Guidance)

- **CLAUDE.md**: Core principles and quick references
- **Context Files**: Detailed documentation
- **Pattern Files**: Decision frameworks

---

## Pattern Lifecycle

```
DISCOVERY → DOCUMENTATION → ENFORCEMENT → REVIEW
    ↓             ↓              ↓           ↓
 Identify     Create          Add        Periodic
 recurring    pattern         hooks/     evaluation
 challenge    document        rules      of usage
```

1. **Discovery**: Pattern emerges from 3+ similar solutions
2. **Documentation**: Create pattern file with decision criteria
3. **Enforcement**: Add hard rules (hooks) or soft rules (CLAUDE.md)
4. **Review**: Monthly check - is pattern still relevant?

---

## Related Documents

- [[AIProjects Architecture Overview]] - How all components work together
- [[MCP Loading Strategy Pattern]] - Detailed loading strategies
- [[Agent Selection Pattern - Integration Summary]] - Agent decision framework

---

*This document defines the terminology and structure used for design patterns in AIProjects and AIFred.*
