---
tags:
  - artifact/research
  - status/draft
  - depth/deep
  - domain/ai
  - domain/dnd
created: 2026-01-02T23:06
updated: 2026-01-24T10:34
---
# Claude Code Research: Pattern Analysis

**Date**: 2026-01-02
**Source**: Deep analysis of 5 GitHub repositories
**Purpose**: Extract patterns for AIProjects & AIfred improvement

---

## Quick Reference: What to Adopt

### Priority 1: Quick Wins (8-10 hours)

| Pattern | Source | Effort | Impact |
|---------|--------|--------|--------|
| SessionStart Hook | hooks-mastery | 2h | Auto-load context on startup |
| SubagentStop Hook | hooks-mastery | 2h | Enable agent chaining |
| Desktop Notifications | my-claude-code-setup | 1h | Alert on task completion |
| Git Worktrees | my-claude-code-setup | 2h | Parallel Claude sessions |

### Priority 2: Significant Enhancements (20-24 hours)

| Pattern | Source | Effort | Impact |
|---------|--------|--------|--------|
| Task Orchestration | Claude-Command-Suite | 8h | `/orchestration:plan`, `:resume`, `:commit` |
| Memory Bank Synchronizer | my-claude-code-setup | 4h | Auto-sync docs with code |
| Skills Architecture | claude-flow | 4h | Replace commands with skills |
| Bi-Temporal Memory | memory-graph | 6h | Time-travel queries |

### Priority 3: Future (40+ hours)

| Pattern | Source | Effort | Impact |
|---------|--------|--------|--------|
| Queen/Worker Swarm | claude-flow | 24h | Multi-agent coordination |
| WFGY Semantic Reasoning | Claude-Command-Suite | 16h | Anti-hallucination |
| AgentDB | claude-flow | 20h | 96-164x faster memory |

---

## 1. Hooks System (hooks-mastery)

### All 8 Hook Types Available

```
.claude/hooks/
├── session_start.py      # NEW: Auto-load context
├── user_prompt_submit.py # Existing: Validation
├── pre_tool_use.py       # Existing: Security
├── post_tool_use.py      # Existing: Audit
├── notification.py       # Progress tracking
├── stop.py               # NEW: Desktop notifications
├── subagent_stop.py      # NEW: Agent chaining
└── pre_compact.py        # NEW: Context preservation
```

### SessionStart Hook Pattern

**Purpose**: Auto-load session-state.md when Claude starts

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["python-dotenv"]
# ///

import json, sys
from pathlib import Path

def load_context():
    context_parts = []

    # Git status
    branch, changes = get_git_status()
    if branch:
        context_parts.append(f"Branch: {branch}, Changes: {changes}")

    # Session state
    for file in [".claude/context/session-state.md",
                 ".claude/context/projects/current-priorities.md"]:
        if Path(file).exists():
            content = Path(file).read_text()[:1000]
            context_parts.append(f"--- {file} ---\n{content}")

    return "\n".join(context_parts)

try:
    input_data = json.loads(sys.stdin.read())
    context = load_context()

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }
    print(json.dumps(output))
    sys.exit(0)
except:
    sys.exit(0)  # Always exit cleanly
```

### Desktop Notification Pattern (Stop Hook)

```python
#!/usr/bin/env -S uv run --script
import subprocess, sys, json

try:
    input_data = json.loads(sys.stdin.read())

    # Linux notification
    subprocess.run([
        'notify-send',
        '--app-name=Claude Code',
        '--urgency=low',
        '--icon=dialog-information',
        'Claude Code Complete',
        'Task finished successfully'
    ], capture_output=True, timeout=5)

    sys.exit(0)
except:
    sys.exit(0)
```

### Key Insights

- **UV single-file scripts**: Inline dependencies, no venv needed
- **Exit codes**: 0 = success, 2 = block with stderr to Claude
- **Always fail silently**: Never crash Claude Code
- **Feature flags**: Use argparse for opt-in features

---

## 2. Agent/Swarm Patterns (claude-flow)

### Agent Lifecycle Architecture

```typescript
// Three parallel loops per agent
Agent {
  1. Heartbeat Loop (30s)      - "I'm alive" signals
  2. Communication Loop (1s)   - Process messages
  3. Learning Loop (5min)      - Analyze patterns
}

// Agent lifecycle
Initialize → Execute → Learn → Shutdown
```

### Queen/Worker Hierarchy

**Queen Coordinator**:
- Issues royal directives
- Allocates resources
- Designates succession (heir agent)
- Three governance modes: Hierarchical, Democratic, Emergency

**Worker Specialist**:
- Reports before/during/after every task
- Checks dependencies before starting
- Delivers comprehensive results with metrics

**Memory Key Pattern**:
```
swarm/queen/status          # Queen's state
swarm/worker-[ID]/status    # Individual worker states
swarm/shared/*              # Shared coordination data
```

### Skills vs Commands (New Architecture)

**Old (Commands)**:
```
.claude/commands/sparc-tdd.md      # Flat, manual
```

**New (Skills)**:
```
.claude/skills/
├── sparc-methodology/
│   └── SKILL.md                   # Auto-discovered
├── github-code-review/
│   └── SKILL.md
└── swarm-orchestration/
    └── SKILL.md
```

**Skill Frontmatter**:
```yaml
---
name: sparc-methodology
description: SPARC development methodology
tags: [development, tdd]
category: development
---
```

**Benefits**:
- Auto-discovery at startup
- Progressive disclosure (Overview → Details → Advanced)
- 40% context reduction
- Natural language invocation

---

## 3. Task Orchestration (Claude-Command-Suite)

### Command Namespace Structure

**13 namespaces, 148+ commands**:
- `/project:*` (12) - Project management
- `/dev:*` (14) - Code review, debugging
- `/test:*` (10) - Testing suite
- `/orchestration:*` (9) - **Task management** (priority)
- `/wfgy:*` (26) - Semantic reasoning

### Orchestration System

**File Structure**:
```
task-orchestration/
└── 01_02_2026/
    └── feature_auth/
        ├── MASTER-COORDINATION.md     # Human-readable
        ├── EXECUTION-TRACKER.md       # Progress metrics
        ├── TASK-STATUS-TRACKER.yaml   # Machine-readable
        └── tasks/
            ├── todos/
            ├── in_progress/
            ├── completed/
            └── on_hold/
```

**Key Commands**:
```
/orchestration:start "Build auth system"
  → Creates date-based folder
  → Decomposes into atomic tasks (2-8h each)
  → Coordinates 3 agents: orchestrator, decomposer, analyzer

/orchestration:resume
  → Restores full context after session loss
  → Shows: in-progress, blocked, next available

/orchestration:commit "Add login endpoint"
  → Links git commit to current task
  → Auto-generates conventional commit message

/orchestration:status
  → Shows task tree with progress percentages
```

**Task Status Protocol**:
```
pending → in_progress → review → testing → completed
              ↓              ↓
           blocked       cancelled
```

### WFGY Semantic Reasoning (Anti-Hallucination)

**Purpose**: Addresses AI limitations via mathematical validation

**Performance Improvements**:
- Reasoning accuracy: +22.4%
- Chain validity: +42.1%
- Stability: 3.6x improvement
- Hallucination: Significantly reduced

**Key Commands**:
```
/wfgy:init                    # Initialize system
/semantic:tree-init "Project" # Create memory tree
/wfgy:formula-all "Task"      # Apply reasoning
/reasoning:chain-validate     # Ensure consistency
```

---

## 4. Worktree & Memory Bank (my-claude-code-setup)

### Git Worktrees for Parallel Sessions

**Shell Functions**:
```bash
# Add to ~/.bashrc

# Create worktree and launch Claude
clx() {
    local branch="${1:-worktree-$(date +%Y%m%d-%H%M%S)}"
    git worktree add "../$branch" -b "$branch" && \
    cd "../$branch" && \
    claude --model sonnet
}

# Management
alias cxl='git worktree list'
cxd() { git worktree remove "../$1"; }
alias cxp='git worktree prune'
```

**.worktreeinclude Pattern**:
```
.env
.env.local
**/.claude/settings.local.json
```

**Result**: Complete session isolation while sharing Git history

### Memory Bank File Taxonomy

| File | Purpose |
|------|---------|
| CLAUDE-activeContext.md | Current session state |
| CLAUDE-patterns.md | Code conventions |
| CLAUDE-decisions.md | Architecture rationale |
| CLAUDE-troubleshooting.md | Known issues + fixes |
| CLAUDE-temp.md | Scratch pad (only read when referenced) |

### Memory Bank Synchronizer Agent

**Purpose**: Keep docs aligned with actual code

**Critical Preservation Rules**:
- NEVER delete: todo lists, roadmaps, planning
- ALWAYS preserve: session logs, troubleshooting, decisions
- UPDATE: technical specs, code examples, patterns

**Usage**:
```
User: "Our code changed but docs are outdated"
→ Triggers memory-bank-synchronizer agent
→ Updates technical content
→ Preserves strategic content
```

### Chain of Draft (CoD) Mode

**Purpose**: 80-92% token reduction for code searches

**Activation**: "use CoD", "chain of draft", "concise reasoning"

**Template**:
```
Target→Glob[pattern]→n→Grep[name]→file:line→signature
```

**Example**:
```
Standard: "Find payment processing code" (150 tokens)
CoD: "Payment→glob:*payment*→pay.service.ts:45" (15 tokens)
```

---

## 5. Bi-Temporal Memory (memory-graph)

### Four Temporal Fields

| Field | Type | Purpose |
|-------|------|---------|
| valid_from | TIMESTAMP | When fact became true |
| valid_until | TIMESTAMP | When fact stopped being true |
| recorded_at | TIMESTAMP | When we learned it |
| invalidated_by | TEXT | ID of superseding relationship |

### 35 Relationship Types (7 Categories)

**Causal**: CAUSES, TRIGGERS, LEADS_TO, PREVENTS, BREAKS
**Solution**: SOLVES, ADDRESSES, ALTERNATIVE_TO, IMPROVES, REPLACES
**Context**: OCCURS_IN, APPLIES_TO, WORKS_WITH, REQUIRES, USED_IN
**Learning**: BUILDS_ON, CONTRADICTS, CONFIRMS, GENERALIZES, SPECIALIZES
**Similarity**: SIMILAR_TO, VARIANT_OF, RELATED_TO, ANALOGY_TO, OPPOSITE_OF
**Workflow**: FOLLOWS, DEPENDS_ON, ENABLES, BLOCKS, PARALLEL_TO
**Quality**: EFFECTIVE_FOR, INEFFECTIVE_FOR, PREFERRED_OVER, DEPRECATED_BY, VALIDATED_BY

### Time-Travel Query Patterns

**Current Only** (default):
```sql
WHERE valid_until IS NULL
```

**Point-in-Time** ("What did we know on March 1, 2024?"):
```sql
WHERE valid_from <= $as_of
  AND (valid_until IS NULL OR valid_until > $as_of)
```

**Full History** ("How did understanding evolve?"):
```sql
ORDER BY valid_from ASC
```

**Recent Changes** ("What changed this week?"):
```sql
WHERE recorded_at >= $since
```

### Adoption for AIProjects

**When storing solutions**:
```python
await memory.create_relationship(
    from_id="solution_id",
    to_id="problem_id",
    type="SOLVES",
    properties={
        "valid_from": "2024-01-01",  # When it started working
        "recorded_at": "2024-02-15", # When we learned it
        "context": "Increased pool to 50",
        "evidence": "Resolved timeouts"
    }
)
```

**When solutions stop working**:
```python
# 1. Create new solution
# 2. Invalidate old: valid_until = now, invalidated_by = new_id
# 3. Document WHY in context
```

---

## Implementation Roadmap

### Week 1: Foundation Hooks
- [ ] Create session_start.py with context loading
- [ ] Create stop.py with desktop notifications
- [ ] Test hooks together
- [ ] Update settings.json

### Week 2: Worktrees & Memory Bank
- [ ] Add clx/cxd shell functions
- [ ] Create .worktreeinclude
- [ ] Create memory-bank-synchronizer agent
- [ ] Create CLAUDE-decisions.md, CLAUDE-troubleshooting.md

### Week 3: Task Orchestration
- [ ] Create /orchestration:start command
- [ ] Create /orchestration:resume command
- [ ] Create /orchestration:status command
- [ ] Create /orchestration:commit command
- [ ] Create task-orchestrator agent

### Week 4: Memory Enhancement
- [ ] Add temporal fields to Memory MCP usage
- [ ] Implement time-travel query patterns
- [ ] Add relationship type vocabulary
- [ ] Create what-changed briefings

---

## Key Files for Reference

### hooks-mastery
- `.claude/hooks/session_start.py` - Context loading
- `.claude/hooks/stop.py` - Notifications
- `.claude/settings.json` - Hook configuration

### claude-flow
- `.claude/agents/hive-mind/queen-coordinator.md` - Queen pattern
- `.claude/agents/hive-mind/worker-specialist.md` - Worker pattern
- `docs/guides/skills-tutorial.md` - Skills architecture

### Claude-Command-Suite
- `.claude/commands/orchestration/ORCHESTRATION-README.md` - Full guide
- `.claude/agents/task-orchestrator.md` - Coordinator agent
- `.claude/agents/TASK-STATUS-PROTOCOL.md` - Status definitions

### my-claude-code-setup
- `README.md` (lines 91-319) - Worktree documentation
- `.claude/agents/memory-bank-synchronizer.md` - Sync agent
- `.claude/agents/code-searcher.md` - CoD implementation

### memory-graph
- `docs/adr/016-bi-temporal-tracking.md` - Architecture decision
- `src/memorygraph/relationships.py` - 35 relationship types
- `src/memorygraph/tools/temporal_tools.py` - Query patterns

---

#research #patterns #hooks #agents #orchestration #memory #aiprojects
