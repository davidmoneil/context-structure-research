---
tags:
  - status/draft
  - depth/deep
  - domain/ai
  - domain/infrastructure
  - artifact/template
created: 2025-12-31T16:55
updated: 2026-01-24T10:39
---
# Design Patterns vs Rules: A Philosophy for Claude Code Architecture

**Created**: 2025-12-31
**Context**: Explaining the architectural approach behind the AIProjects Claude Code configuration

---

## The Core Distinction

### What is a Rule Set?

A rule set is a collection of **prescriptive restrictions**:

```
- Always do X
- Never do Y
- Use tool A, not tool B
- Format outputs as Z
```

Rules are:
- **Static**: Written once, rarely updated
- **Reactive**: Respond to violations
- **Limiting**: Define boundaries
- **Brittle**: Break when edge cases appear

### What is a Design Pattern?

A design pattern is a **reusable framework for thinking**:

```
When encountering [situation type]:
1. First, understand the context
2. Then, follow this approach
3. Document what you learn
4. If repeated 3x, automate
```

Patterns are:
- **Evolutionary**: Grow from actual usage
- **Proactive**: Guide discovery and learning
- **Enabling**: Expand capabilities over time
- **Resilient**: Adapt to new situations

---

## The Philosophy: Teaching Claude HOW to Think, Not WHAT to Do

The AIProjects configuration doesn't tell Claude "do this, not that." Instead, it teaches Claude:

1. **Where to look** for information
2. **How to approach** different problem types
3. **When to document** discoveries
4. **How to evolve** the system itself

### Meta-Rules vs Operational Rules

The CLAUDE.md file contains very few actual "rules." Instead, it has **meta-rules**:

| Traditional Rule | Meta-Rule (Pattern-Based) |
|-----------------|---------------------------|
| "Always use Docker MCP tools" | "Check context first, prefer MCP, but adapt to situation" |
| "Never guess file locations" | "Reference paths-registry.yaml, ask if unknown" |
| "Format outputs as X" | "Use patterns from workflow-patterns.md for consistency" |
| "Always document changes" | "If task repeats 3x, propose automation" |

The meta-rules teach Claude to **navigate a living system**, not follow a static checklist.

---

## How This Evolved: From Discovery to Automation

### Phase 1: Manual Discovery (The Beginning)

When I first set up Claude Code, I discovered things manually:

```
"What Docker containers are running?"
→ ran docker ps
→ noted the output somewhere
→ forgot where I noted it
→ asked again next session
```

**Problem**: No memory, no consistency, repeating work.

### Phase 2: Documentation Capture

I started documenting discoveries:

```
.claude/context/systems/docker/n8n.md
```

This file captured:
- What n8n is
- Where its config lives
- Common commands
- Known issues

**Problem**: Still manual, needed to remember to check docs.

### Phase 3: Pattern Recognition

After documenting multiple Docker containers, I noticed a **pattern**:

```
Every time I discover a container:
1. Check if running
2. Inspect configuration
3. Find compose file
4. Document in context file
5. Update paths-registry.yaml
```

This became the **Infrastructure Discovery Pattern** in `workflow-patterns.md`.

### Phase 4: Pattern Codification

The pattern became a **slash command**:

```markdown
# /discover-docker

Discover and document the $ARGUMENTS Docker container:

## Workflow Phases

### Phase 1: Container Discovery
1. Check if container exists (MCP first, bash fallback)
2. Inspect container configuration
3. Get container logs

### Phase 2: Configuration Discovery
1. Find compose file
2. Check logs location

### Phase 3: Connectivity Testing
...
```

Now any session can run `/discover-docker n8n` and get consistent, thorough documentation.

### Phase 5: Automated Enforcement

Finally, I created **hooks** that enforce patterns automatically:

```javascript
// mcp-enforcer.js
// Encourages use of MCP tools over bash equivalents

const MCP_ALTERNATIVES = {
  'docker ps': {
    mcp: 'mcp__docker-mcp__list-containers',
    description: 'Use Docker MCP for container listing'
  },
  // ...
};
```

The hook doesn't **block** bash usage (that would be a rule). Instead, it **suggests** the pattern-aligned approach.

---

## Concrete Examples from the Project

### Example 1: Session Exit Procedure

**Started as**: Forgetting to commit work, losing session context

**Evolved into**: A documented workflow in `session-exit-procedure.md`

**Key insight**: The procedure has a **Quick Exit Checklist** (for simple sessions) AND **Detailed Procedure** (for complex sessions). It's not "always do all 9 steps" - it's "scale your effort to the task."

```markdown
## Quick Exit Checklist
- [ ] Update session-state.md
- [ ] Clear/review session todos
- [ ] Update current-priorities.md
- [ ] Commit any uncommitted changes
- [ ] Create session notes (optional, for complex sessions)
```

**Future automation potential**: The doc explicitly calls out:

```markdown
### Future: Create `/exit-session` Slash Command
A slash command could automate this workflow...
**Status**: Not yet implemented. Add to backlog if this becomes a frequent need.
```

This is the pattern in action: document first, automate when pain is proven.

### Example 2: The Paths Registry

**Started as**: "Where is the n8n config file?"

**Evolved into**: `paths-registry.yaml` - a single source of truth for ALL external paths

```yaml
docker:
  containers:
    n8n:
      compose: "/home/davidmoneil/Docker/mydocker/n8n/docker-compose.yml"
      config: "/home/davidmoneil/Docker/mydocker/n8n/data/n8n_data/n8n_root"
      url: "https://n8n.theklyx.space"
      url_local: "http://localhost:5678"
```

**Why this is a pattern, not a rule**:
- I don't say "always check paths-registry.yaml"
- I say "this is where paths live - update it when you discover new ones"

The system grows organically as I discover new services.

### Example 3: Workflow Patterns (Meta-Patterns)

`workflow-patterns.md` contains **pattern templates** like:

```markdown
## Pattern: Service Health Check

### Phase 1: Connectivity
- Check if service is reachable
- Verify DNS resolution

### Phase 2: Service Status
- **Docker**: Use `mcp__docker-mcp__list-containers` first
- **Web**: Navigate with browser or curl

### Phase 3: Log Review
...

### Phase 6: Memory Storage
Store in Memory MCP if:
- New issue pattern discovered
- Service status changed significantly
```

This is a **thinking template**, not a rule. It says "here's a comprehensive approach - adapt as needed."

### Example 4: The 3x Rule

Throughout the documentation, there's a recurring principle:

> "If a task repeats 3+ times, propose automation"

This is captured in CLAUDE.md:

```markdown
**Suggest automation**: If a task repeats 3+ times,
propose creating a slash command or workflow
```

And in workflow-patterns.md:

```markdown
**Philosophy**: Don't create workflows preemptively.
Use these patterns 3+ times before automating.
```

This prevents over-engineering while encouraging organic growth.

---

## The Growth Model: How This Design Enables Evolution

### Current State: A Living System

```
CLAUDE.md (entry point)
    ↓
.claude/context/ (knowledge base)
    ├── systems/ (what exists)
    ├── projects/ (what we're building)
    ├── integrations/ (how things connect)
    └── workflows/ (how to do things)
    ↓
.claude/commands/ (automated patterns)
    ├── /discover-docker
    ├── /check-service
    ├── /ssh-connect
    └── ...
    ↓
.claude/hooks/ (automated enforcement)
    ├── mcp-enforcer.js
    ├── audit-logger.js
    └── ...
```

### Growth Trajectory

#### Level 1: Documentation (Passive)
- Claude reads context files
- Information is available but not enforced
- Example: "n8n runs on port 5678"

#### Level 2: Patterns (Guided)
- Claude follows workflow patterns
- Consistent approach across sessions
- Example: "When checking Docker services, use this 6-phase approach"

#### Level 3: Commands (Automated)
- Claude has slash commands for common tasks
- One command triggers a full workflow
- Example: `/discover-docker ollama`

#### Level 4: Hooks (Enforced)
- Hooks run automatically on tool use
- Patterns are suggested/enforced without human intervention
- Example: "MCP alternative available for docker ps"

#### Level 5: Agents (Autonomous)
- Specialized agents for complex multi-step tasks
- Run in background, produce structured outputs
- Example: `/agent deep-research "OAuth2 best practices"`

### Future Growth Potential

The design explicitly supports:

1. **New Services**: Add to `paths-registry.yaml`, create context file
2. **New Patterns**: Add to `workflow-patterns.md`, observe 3x before automating
3. **New Commands**: Codify proven patterns as slash commands
4. **New Hooks**: Automate enforcement of important patterns
5. **New Agents**: Create specialized agents for domain-specific work

---

## Comparing Approaches

### Rule Set Approach (NOT what we're doing)

```markdown
# CLAUDE.md - Rule Set Style

RULES:
1. Always use MCP tools instead of bash
2. Always update paths-registry.yaml after discovering paths
3. Always create context files for new services
4. Never guess file locations
5. Always commit at end of session
6. Format all outputs using markdown tables
7. ...
```

**Problems**:
- Doesn't handle edge cases ("what if MCP is down?")
- Doesn't explain WHY
- Doesn't evolve
- Creates compliance mindset, not thinking mindset

### Pattern Approach (What we're doing)

```markdown
# CLAUDE.md - Pattern Style

## Key Principles
1. **Context-Driven**: Check `.claude/context/` before advice
2. **Solve Once, Reuse**: Document solutions for future reference
3. **Ask Questions**: When unsure, ask rather than assume
4. **Iterative Growth**: Start minimal, evolve based on actual use

## When Starting a Session
**ALWAYS check** session-state.md **first** to see:
- What was being worked on last
- Current work status

## Workflow
When asked to help with infrastructure tasks:
1. **Check context first**: Start with _index.md
2. **Verify paths**: Reference paths-registry.yaml
3. **Document discoveries**: Update context files
4. **Suggest automation**: If task repeats 3+ times, propose command
```

**Benefits**:
- Adapts to edge cases (fallback strategies documented)
- Explains the reasoning
- Grows organically
- Creates thinking mindset

---

## Summary: The Design Philosophy

### Core Tenets

1. **Patterns over Rules**: Teach HOW to think, not WHAT to do
2. **Evolution over Prescription**: Start minimal, grow from real usage
3. **Documentation as Memory**: Context files create persistent memory
4. **Automation as Graduation**: Commands/hooks emerge from proven patterns
5. **Meta-Rules over Operational Rules**: Guide discovery, don't restrict action

### The Result

A Claude Code configuration that:
- **Remembers** across sessions (context files, session-state.md)
- **Learns** from discoveries (paths-registry.yaml updates)
- **Improves** over time (patterns → commands → hooks)
- **Adapts** to new situations (flexible patterns, not rigid rules)
- **Teaches** rather than restricts (guidance, not guardrails)

### Key Insight

> "The best systems don't enforce compliance - they enable capability."

This configuration doesn't make Claude obey rules. It makes Claude capable of navigating, learning from, and improving a complex infrastructure environment.

---

## Related Documentation

- `/.claude/CLAUDE.md` - Main entry point
- `/.claude/context/integrations/workflow-patterns.md` - Pattern templates
- `/.claude/context/workflows/session-exit-procedure.md` - Evolved workflow example
- `/paths-registry.yaml` - Living knowledge base example
- `/.claude/hooks/` - Automated pattern enforcement

---

*This document itself follows the philosophy: it was created because explaining the pattern was valuable, not because a rule said "document everything."*
