---
created: 2026-01-22T14:04
updated: 2026-01-24T10:33
tags:
  - project/aiprojects
  - depth/deep
  - domain/ai
  - domain/mechanics
  - domain/infrastructure
---
# AIProjects Architecture Taxonomy

> **Purpose**: Comprehensive visual documentation of the AIProjects infrastructure hub
> **Created**: 2026-01-22
> **Status**: Living document - update as system evolves
> **Canvases**: [[AIProjects-Architecture-Canvas]] (detailed) | [[AIProjects-Architecture-Simple]] (friendly) | [[AIProjects-Architecture-Domains]] (5 domains)

---

## Executive Summary

**AIProjects** is a personal AI infrastructure hub serving as the central orchestration point for home lab automation, knowledge management, and system integration.

### Quick Stats

| Component               | Count | Description                              |
| ----------------------- | ----- | ---------------------------------------- |
| **Skills**              | 11    | Multi-step workflow guides               |
| **Commands**            | 35+   | Slash commands (5 namespaces)            |
| **Hooks**               | 39    | Automatic behaviors (16 active)          |
| **Agents**              | 17    | Autonomous task executors                |
| **Context Files**       | 171   | Infrastructure documentation             |
| **Knowledge Files**     | 70    | Guides, references, notes                |
| **Scripts**             | 28    | Bash deterministic operations            |
| **Orchestration Plans** | 4+    | Complex task tracking                    |
| **Index Files**         | 6     | Navigation hubs (`_index.md`)            |
| **Templates**           | 6     | Component scaffolds (`_template*`)       |
| **History Categories**  | 4     | Learnings, decisions, research, sessions |

---

## Simplified Overview: The Helper's House

> *See also*: [[AIProjects-Architecture-Simple]] for the visual version | [[AIProjects-Architecture-Domains]] for domain groupings

Think of AIProjects like a well-organized house where a helpful robot lives. Everything belongs to one of **5 functional domains**:

### The 5 Domains

| # | Domain | Friendly Name | Purpose | Color |
|---|--------|---------------|---------|-------|
| 1 | **STARTUP** | Front Door | Initialize the helper | 🟢 Green |
| 2 | **KNOWLEDGE** | Memory & Reference | Store & retrieve information | 🟣 Purple |
| 3 | **EXECUTION** | The Workshop | Do the actual work | 🔵 Blue |
| 4 | **TRACKING** | The Planner | Track complex multi-step work | 🟠 Orange |
| 5 | **MONITORING** | The Watchers | Observe and record automatically | 🔴 Red |
| + | **SCAFFOLDING** | Tools | Support everything | ⚪ Gray |

### Components by Domain

| Component | Friendly Name | Domain | Analogy | One-Liner |
|-----------|---------------|--------|---------|-----------|
| `CLAUDE.md` | **The Rulebook** | 1.STARTUP | Rules on classroom wall | First thing read; sets behavior |
| `settings.json` | **Permission Slip** | 1.STARTUP | Permission slip from parents | What's allowed and forbidden |
| `context/` | **The Brain** | 2.KNOWLEDGE | Your memory of home | Active memory of the system |
| `knowledge/` | **The Library** | 2.KNOWLEDGE | School library | Reference books to look up |
| `history/` | **The Diary** | 2.KNOWLEDGE | Journal or diary | Past learnings and decisions |
| `_index.md` | **Table of Contents** | 2.KNOWLEDGE | Book's TOC | Find things quickly |
| `commands/` | **Buttons** | 3.EXECUTION | TV remote | Press button, one thing happens |
| `skills/` | **Recipe Books** | 3.EXECUTION | Cookbook | Multi-step instructions |
| `agents/` | **Expert Workers** | 3.EXECUTION | Plumber/electrician | Autonomous specialists |
| `Scripts/` | **Simple Machines** | 3.EXECUTION | Vending machine | Same input = same output |
| `orchestration/` | **Project Checklist** | 4.TRACKING | School project plan | Big jobs → small steps |
| `hooks/` | **Automatic Watchers** | 5.MONITORING | Smoke detector | React to events automatically |
| `logs/` | **Security Cameras** | 5.MONITORING | CCTV footage | Record everything |
| `_template*` | **Cookie Cutters** | +SCAFFOLDING | Cookie cutters | Make new things consistent |
| `external-sources/` | **Shortcuts** | +SCAFFOLDING | Doors to other rooms | Links to external resources |
| `MCP Servers` | **External Tools** | +SCAFFOLDING | Power tools | Capabilities from outside |

### How Domains Connect

```
┌─────────────────┐         ┌─────────────────────┐
│   1.STARTUP     │──reads──▶│    2.KNOWLEDGE     │
│  (Front Door)   │         │ (Memory & Reference)│
└────────┬────────┘         └─────────▲───────────┘
         │ configures                 │ reads/writes
         ▼                            │
┌─────────────────┐         ┌─────────┴───────────┐
│  5.MONITORING   │◀─observes─│    3.EXECUTION     │
│  (Watchers)     │         │   (Workshop)        │
└────────┬────────┘         └─────────┬───────────┘
         │ records                    │ tracks
         ▼                            ▼
┌─────────────────┐         ┌─────────────────────┐
│     LOGS        │         │    4.TRACKING       │
│   (Records)     │         │    (Planner)        │
└─────────────────┘         └─────────────────────┘

     ═══════════════════════════════════════
     + SCAFFOLDING supports all domains above
     ═══════════════════════════════════════
```

### Step-by-Step Flow

```
1. [STARTUP] Helper wakes up → reads RULEBOOK (CLAUDE.md)
2. [STARTUP] Checks PERMISSION SLIP (settings.json) for what's allowed
3. [KNOWLEDGE] Loads BRAIN (context/) to remember things
4. [EXECUTION] User presses a BUTTON (command)
5. [EXECUTION] If complicated → follows a RECIPE (skill)
6. [EXECUTION] If needs expert → calls a WORKER (agent)
7. [EXECUTION] Runs SIMPLE MACHINES (scripts) for repetitive stuff
8. [TRACKING] For big jobs → uses PROJECT CHECKLIST (orchestration)
9. [MONITORING] WATCHERS (hooks) monitor everything automatically
10. [MONITORING] SECURITY CAMERAS (logs) record what happened
11. [KNOWLEDGE] Writes in DIARY (history) what was learned
```

---

## Component Types

### 1. Skills (`.claude/skills/`)

> **Domain**: 3.EXECUTION (Recipe Books) | **Color**: 🟦 Blue

**What**: End-to-end workflow guides consolidating related commands, hooks, and patterns.

**When to Use**: Need guidance across MULTIPLE steps (not single actions).

**Structure**:
```
skill-name/
├── SKILL.md          # Main documentation
├── config.json       # Configuration
├── tools/            # TypeScript utilities
├── workflows/        # Procedure docs
└── templates/        # Reusable templates
```

**All Skills**:
| Skill | Purpose | Key Commands |
|-------|---------|--------------|
| `session-management` | Session lifecycle | `/checkpoint`, `/update-priorities` |
| `structured-planning` | Guided planning | `/plan`, `/plan:new`, `/plan:review` |
| `infrastructure-ops` | Health & discovery | `/check-health`, `/discover-docker` |
| `parallel-dev` | Worktree development | `/parallel-dev:plan`, `:start` |
| `orchestration` | Multi-phase tasks | `/orchestration:plan`, `:status` |
| `upgrade` | Self-improvement | `/upgrade` |
| `project-lifecycle` | Project management | `/new-code-project`, `/register-project` |
| `system-utilities` | Core utilities | `/backup-status`, `/link-external` |
| `fabric` | AI text processing | `/fabric`, `/fabric:analyze-logs` |
| `audio-tools` | Audio infrastructure | Audio management |
| `_template` | Skill creation | Template only |

---

### 2. Commands (`.claude/commands/`)

> **Domain**: 3.EXECUTION (Buttons) | **Color**: 🟩 Green

**What**: Slash commands invoking single actions. Usually delegate to Scripts.

**When to Use**: Need to do ONE specific thing.

**Frontmatter Schema**:
```yaml
description: Short description
argument-hint: [--arg value]
skill: parent-skill-name  # or standalone: true
allowed-tools:
  - Bash(~/Scripts/script.sh:*)
```

**Namespaces** (Sub-commands):
- `/orchestration:*` - Task orchestration (plan, status, resume, commit)
- `/parallel-dev:*` - Parallel development (plan, start, validate, merge)
- `/fabric:*` - AI text processing (analyze-logs, commit-msg, review-code)
- `/commits:*` - Cross-project commits (status, summary, push-all)
- `/plan:*` - Structured planning (new, review, feature)

**Standalone Commands** (no parent skill):
`/agent`, `/browser`, `/n8n`, `/creative`, `/memory-review`, `/telos`, `/checkpoint`, `/update-priorities`, `/audit-log`, `/design-review`, `/check-health`, `/check-services`, `/discover-docker`, `/register-service`, `/link-external`, `/sync-git`, `/upgrade`

---

### 3. Hooks (`.claude/hooks/`)

> **Domain**: 5.MONITORING (Automatic Watchers) | **Color**: 🟧 Orange

**What**: Automatic behaviors triggered by events. No user action needed.

**When Active**: Always running - respond to tool usage, prompts, sessions.

**Event Types**:
| Event | When Triggered |
|-------|----------------|
| `SessionStart` | Session begins |
| `UserPromptSubmit` | User sends message |
| `PreToolUse` | Before tool runs |
| `PostToolUse` | After tool completes |
| `PreCompact` | Before context compaction |
| `SubagentStop` | Agent finishes |
| `Stop` | Session ends |

**Active Hooks (16)**:

| Category | Hooks | Purpose |
|----------|-------|---------|
| **Lifecycle** | session-start, session-stop, subagent-stop, pre-compact, self-correction-capture | Context, notifications |
| **Core** | audit-logger, docker-health-check, file-access-tracker, cross-project-commit-tracker | Logging, monitoring |
| **Security** | secret-scanner, branch-protection | Prevent leaks, protect main |
| **Workflow** | prompt-enhancer, lsp-redirector, orchestration-detector, skill-router, fabric-suggester | Routing, suggestions |

**Pending Conversion (20)**: credential-guard, docker-validator, doc-sync-trigger, memory-maintenance, worktree-manager, priority-validator, and more...

---

### 4. Agents (`.claude/agents/`)

> **Domain**: 3.EXECUTION (Expert Workers) | **Color**: 🟪 Purple

**What**: Autonomous executors with persistent memory for complex independent tasks.

**When to Use**: Need autonomous COMPLEX task execution with memory.

**Invocation**: `/agent <name> [args]`

**Structure**:
```
agents/
├── <agent>.md         # Agent definition
├── memory/<agent>/    # Persistent knowledge
├── results/<agent>/   # Execution outputs
└── sessions/          # Session logs
```

**All Agents**:
| Agent | Purpose |
|-------|---------|
| `deep-research` | Multi-source web research |
| `service-troubleshooter` | Systematic diagnosis |
| `docker-deployer` | Guided deployment |
| `memory-bank-synchronizer` | Sync docs with code |
| `plex-troubleshoot` | Plex troubleshooting |
| `ollama-manager` | LLM management |
| `code-analyzer` | Code analysis |
| `code-implementer` | Implementation |
| `code-tester` | Testing |
| `project-plan-validator` | Plan validation |
| `creative-projects` | Creative work |
| `parallel-dev-*` (4) | Parallel dev support |

**Agent Chaining**: Agents can call other agents for sequential workflows.

---

### 5. Context Files (`.claude/context/`)

> **Domain**: 2.KNOWLEDGE (The Brain) | **Color**: 🟨 Yellow

**What**: Infrastructure documentation loaded at session start.

**When Used**: Automatically - provides session context.

**Subdirectories (18 categories, 171 files)**:

| Directory | Files | Purpose |
|-----------|-------|---------|
| `patterns/` | 19 | Reusable implementation patterns |
| `projects/` | 35 | Active work, priorities |
| `systems/` | 42 | Infrastructure docs |
| `integrations/` | 11 | MCP, third-party |
| `workflows/` | 8 | Repeatable procedures |
| `standards/` | 4 | Terminology, conventions |
| `designs/` | 10 | Architecture designs |
| `archive/` | 19 | Completed/old |
| `audits/` | 3 | Analysis docs |
| `coding/` | 4 | Language-specific |
| `ideas/` | 1 | Future features |
| `lessons/` | 1 | Learned corrections |
| `plans/` | 1 | Roadmap |
| `telos/` | 6 | Strategic goals |
| `tests/` | 1 | Testing docs |
| `tools/` | 1 | Tool integration |

**Key Files** (Session Loading):
- `_index.md` - Central discovery
- `session-state.md` - Current work (loaded at start)
- `compaction-essentials.md` - Survives compression
- `CLAUDE-troubleshooting.md` - Quick fixes

---

### 6. Knowledge Base (`knowledge/`)

> **Domain**: 2.KNOWLEDGE (The Library) | **Color**: 🟫 Brown/Tan

**What**: Public guides, references, research findings.

**When Used**: On-demand documentation lookup.

**Subdirectories (8, 70 files)**:

| Directory | Files | Purpose |
|-----------|-------|---------|
| `docs/` | 14 | Guides, tutorials |
| `reference/` | 16 | API refs, architecture |
| `notes/` | 28 | Session notes |
| `reports/` | 2 | Analysis reports |
| `n8n-workflows/` | 8 | Workflow docs |
| `templates/` | 0 | Placeholder |
| `obsidian-sync/` | 0 | Synced content |
| `archive/` | 1 | Archived |

**Key Files**:
- `docs/claude-code-best-practices.md` - Comprehensive guide
- `docs/quick-start.md` - Getting started
- `reference/mcp/*.md` - MCP server documentation

---

### 7. Scripts (`Scripts/`)

> **Domain**: 3.EXECUTION (Simple Machines) | **Color**: 🟥 Red

**What**: Bash scripts for deterministic operations.

**When to Use**: Commands delegate here for actual execution.

**Categories (28 scripts)**:

| Category | Scripts | Examples |
|----------|---------|----------|
| **Core Utilities** | 8 | checkpoint, update-priorities, sync-git |
| **Infrastructure** | 8 | check-all-services, discover-docker |
| **Fabric** | 4 | fabric-wrapper, fabric-analyze-logs |
| **Project** | 2 | consolidate-project, push-all-commits |
| **Scheduled** | 5 | weekly-context-analysis, weekly-docker-restart |
| **Other** | 3 | ollama-maintenance, sync-aifred-jarvis |

**Capability Layering Pattern**:
```
User → Command → Script → System
         ↓
      (delegate)
```

---

### 8. Orchestration (`.claude/orchestration/`)

> **Domain**: 4.TRACKING (Project Checklist) | **Color**: ⬜ White/Gray

**What**: YAML files tracking complex multi-phase tasks.

**When to Use**: Task requires multiple phases with dependencies.

**Plan Schema**:
```yaml
name: task-name
status: active | completed | paused
phases:
  - name: "Phase 1"
    tasks:
      - id: T1.1
        description: Task
        done_criteria: Acceptance
        status: pending | in_progress | completed
        depends_on: ["T1.0"]
        commits: ["abc123"]
```

**Workflow**:
1. `/orchestration:plan "complex task"` - Create plan
2. `/orchestration:status` - View progress
3. `/orchestration:commit T1.1 <hash>` - Link commits
4. `/orchestration:resume` - Continue after break

---

### 9. Logs (`.claude/logs/`)

> **Domain**: 5.MONITORING (Security Cameras) | **Color**: ⬛ Dark Gray

**What**: JSONL activity logs for audit, debugging, analytics.

**When Used**: Automatic - hooks write continuously.

**Log Files**:
| File | Purpose |
|------|---------|
| `audit.jsonl` | All tool executions |
| `agent-activity.jsonl` | Agent completions |
| `orchestration-detections.jsonl` | Complex task detections |
| `skill-routing.jsonl` | Command routing |
| `corrections.jsonl` | User corrections |
| `cross-project-commits.json` | Multi-project commits |
| `file-access.json` | Context file usage |

---

### 10. External Sources (`external-sources/`)

> **Domain**: +SCAFFOLDING (Shortcuts) | **Color**: 🔗 Cyan/Teal

**What**: Symlinks to data living elsewhere.

**When Used**: Access Docker configs, logs without full paths.

**Structure**:
```
external-sources/
├── docker/      # 12 docker-compose symlinks
├── logs/        # 10 log file symlinks
├── configs/     # App configurations
├── nas/         # NAS references
└── obsidian/    # Plugin development
```

**Management**: `/link-external` creates symlinks and updates `paths-registry.yaml`

---

### 11. Supporting Components

> **Domain**: +SCAFFOLDING (Various)

**Templates** (`.claude/templates/`):
- `docker-compose-monitored.yml` - Service template
- `health-endpoint.ts` - Health check template
- `systemd-monitored.service` - Systemd template
- `project-template/` - Full scaffold

**Jobs** (`.claude/jobs/`):
- `claude-scheduled.sh` - Autonomous job runner
- `daily-sync.sh`, cleanup scripts, logs

**Parallel Dev** (`.claude/parallel-dev/`):
- `plans/`, `executions/`, `registry.json`
- Git worktree tracking

---

## Claude Code Configuration System

This section explains how Claude Code loads and processes project instructions.

### 12. CLAUDE.md (Entry Point)

> **Domain**: 1.STARTUP (The Rulebook) | **Color**: 📄 White/Document

**What**: The primary instruction file that Claude Code loads at session start.

**Location**: `.claude/CLAUDE.md` (project root)

**Structure**:
```markdown
# Project Instructions

## Project Context
- Purpose, owner, environment, approach

## Key Principles
- Numbered rules for behavior

## Quick Links
- @references to important files

## Workflows
- Common task patterns

## Response Style
- Output formatting guidance
```

**How It Works**:
1. Claude Code automatically loads CLAUDE.md at session start
2. Instructions become the AI's "operating manual" for the project
3. `@` references point to files Claude can load on-demand
4. Project CLAUDE.md overrides global settings for project-specific behavior

**Key Sections in AIProjects**:
| Section | Purpose |
|---------|---------|
| Project Context | Hub role, owner, environment |
| Key Principles | 8 numbered rules (context-driven, solve-once, etc.) |
| Quick Links | 30+ `@` references to context files |
| Task Orchestration | Auto-detection of complex tasks |
| Skills System | Multi-step workflow guidance |
| MCP Tools | Server inventory and usage |
| Session Continuity | Start/exit procedures |

---

### 13. `@` Reference Syntax

> **Domain**: 1.STARTUP (Part of Rulebook) | **Color**: N/A (syntax, not file)

**What**: Claude Code's native file reference syntax for discovery and loading.

**Syntax**: `@path/to/file.md` or `@.claude/context/file.md`

**Behavior**:
- **Navigation Hint**: Claude sees `@` references as "files that exist and may be relevant"
- **Not Auto-Loaded**: Content is loaded when Claude decides to read the file
- **Enables Discovery**: Allows pointing to many files without context bloat

**Example in CLAUDE.md**:
```markdown
## Quick Links
- @.claude/context/_index.md - Find relevant context files
- @.claude/context/session-state.md - Current work status
- @paths-registry.yaml - Source of truth for external paths
```

**How Claude Uses Them**:
1. Sees the `@` reference during session
2. Decides if the referenced file is relevant to current task
3. Uses Read tool to load content when needed
4. Content becomes part of working context

**Benefits**:
- Point to 30+ files without loading all of them
- Claude learns file structure from references
- On-demand loading preserves context window

---

### 14. settings.json (Configuration)

> **Domain**: 1.STARTUP (Permission Slip) | **Color**: ⚙️ Steel

**What**: Project-level configuration for permissions, hooks, and behavior.

**Location**: `.claude/settings.json` (version controlled)

**Companion**: `.claude/settings.local.json` (accumulated permissions, gitignored)

**Structure**:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "description": "Permission configuration",
  "respectGitignore": true,

  "hooks": {
    "SessionStart": [...],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "UserPromptSubmit": [...],
    "PreCompact": [...]
  },

  "allow": [
    "Bash(git status:*)",
    "Bash(docker ps:*)"
  ],

  "deny": [
    "Read(~/.ssh/*)"
  ]
}
```

**Hook Configuration**:
| Event | When | Example Use |
|-------|------|-------------|
| `SessionStart` | Session begins | Load context, show status |
| `PreToolUse` | Before tool runs | Audit logging, secret scanning |
| `PostToolUse` | After tool completes | Health checks, tracking |
| `UserPromptSubmit` | User sends message | Prompt enhancement, routing |
| `PreCompact` | Before context compaction | Inject essential context |

**Permission Model**:
```
DENY (always blocked)
  ↓
BASELINE (settings.json - safe operations)
  ↓
ACCUMULATED (settings.local.json - user approved)
  ↓
PROMPT (new operations - requires approval)
```

---

### 15. `_index.md` Files (Navigation Hubs)

> **Domain**: 2.KNOWLEDGE (Table of Contents) | **Color**: 📑 Teal

**What**: Table-of-contents files for discovering related documentation.

**Pattern**: `_index.md` at the root of each major directory

**Locations (6 index files)**:
| Index | Location | Purpose |
|-------|----------|---------|
| Master | `.claude/context/_index.md` | All context organized |
| Docker | `.claude/context/systems/docker/_index.md` | 31 container docs |
| Patterns | `.claude/context/patterns/_index.md` | Reusable patterns |
| Standards | `.claude/context/standards/_index.md` | Conventions |
| Skills | `.claude/skills/_index.md` | All skills |
| Logging | `.claude/context/systems/logging/_index.md` | Loki/Grafana |

**Structure Pattern**:
```markdown
# [Category] Index

## Quick Access
- @most-important-file.md
- @second-most-important.md

## Full Directory
### Subcategory 1
- @file1.md - Description
- @file2.md - Description

### Subcategory 2
...

## Recent Updates
- 2026-01-22: Added X
- 2026-01-21: Updated Y
```

**Why They Exist**:
- Single entry point for each knowledge domain
- Enable `@` reference from CLAUDE.md without listing every file
- Maintain counts and freshness indicators
- Provide quick-access shortcuts to most-used files

---

## Template System

Templates ensure consistency when creating new components.

### 16. Component Templates (`_template*`)

> **Domain**: +SCAFFOLDING (Cookie Cutters) | **Color**: 📝 Pink

**What**: Starter files for creating new skills, agents, commands, etc.

**Pattern**: Files named `_template*.md` or `_template.yaml`

**Available Templates**:
| Template | Location | Creates |
|----------|----------|---------|
| Service | `.claude/context/systems/_template-service.md` | Docker service docs |
| Project | `.claude/context/projects/_template-project.md` | Project context files |
| Agent | `.claude/agents/_template-agent.md` | Custom agents |
| Workflow | `.claude/context/workflows/_template-workflow.md` | Repeatable procedures |
| Orchestration | `.claude/orchestration/_template.yaml` | Multi-phase task plans |
| Skill | `.claude/skills/_template/SKILL.md` | Full skill with tools |

**Template Variables**:
```
{{NAME}}      - Provided name
{{DATE}}      - Current date (YYYY-MM-DD)
{{SLUG}}      - lowercase-with-dashes
{{TIMESTAMP}} - Full ISO timestamp
```

**Usage Pattern**:
```bash
# Copy template
cp .claude/agents/_template-agent.md .claude/agents/my-new-agent.md

# Edit with your specifics
# - Update name and description
# - Add agent-specific instructions
# - Define memory structure
```

**Skill Template (Special)**:
The skill template at `.claude/skills/_template/` includes:
- `SKILL.md` - Skill documentation
- `config.json` - Configuration
- `tools/` - TypeScript deterministic tools
- `templates/` - Output templates

---

## History & Learnings System

Long-term knowledge capture that persists across sessions.

### 17. History Directory (`.claude/history/`)

> **Domain**: 2.KNOWLEDGE (The Diary) | **Color**: 📚 Indigo

**What**: Structured storage for decisions, learnings, research, and session summaries.

**Structure**:
```
.claude/history/
├── index.md              # Searchable master index
├── sessions/             # Session summaries
├── learnings/
│   ├── bugs/            # Bug patterns encountered
│   ├── patterns/        # Implementation patterns learned
│   ├── tools/           # Tool usage insights
│   └── workflows/       # Workflow improvements
├── decisions/
│   ├── architecture/    # Architecture decisions
│   ├── tools/           # Tool selection decisions
│   └── approaches/      # Approach decisions
├── research/
│   ├── technologies/    # Tech research
│   ├── approaches/      # Approach comparisons
│   └── references/      # External references
└── templates/           # Entry templates
```

**Commands**:
| Command | Purpose |
|---------|---------|
| `/capture learning "[insight]"` | Quick capture a learning |
| `/capture decision "[decision]"` | Record a decision |
| `/capture session "[summary]"` | Save session summary |
| `/capture research "[topic]"` | Start research doc |
| `/history search "[query]"` | Search all history |
| `/history recent [count]` | Show recent entries |

**Entry Format**:
```markdown
# [Title]

**Date**: 2026-01-22
**Category**: learning/patterns
**Tags**: [typescript, tools, skills]

## Context
What led to this learning

## Learning
The actual insight

## Application
How to apply going forward

## Related
- Links to other entries
```

**Integration**:
- `corrections.jsonl` in logs captures user corrections
- `self-correction-capture.js` hook detects correction patterns
- History feeds into session context for continuity

---

## Core Patterns

### PARC (Design Review)
**Prompt → Assess → Relate → Create**
Apply before implementing significant tasks.

### Capability Layering
**Code → CLI → Prompt**
Deterministic scripts first, AI judgment last.

### Autonomous Execution
**Permission Tiers**: Discovery (read) → Analyze (write data) → Implement (full)
Scheduled Claude jobs with safety model.

### Memory Storage
**When to store in Memory MCP**:
- Infrastructure facts, decisions, relationships
- Use bi-temporal timestamps (when happened, when recorded)

### MCP Loading Strategy
- **Always-On**: Docker, Filesystem, Git
- **On-Demand**: n8n, GitHub, SSH, Prometheus
- **Isolated**: Playwright (browser automation)

---

## Decision Tree: What to Use?

```
Need to do ONE thing?
├─ YES → Use a COMMAND (/checkpoint)
│
Need guidance across MULTIPLE steps?
├─ YES → Reference a SKILL (session-management)
│
Need autonomous COMPLEX task execution?
├─ YES → Invoke an AGENT (/agent deep-research)
│
Task is repetitive/deterministic?
├─ YES → Create a SCRIPT
│
Task requires multi-phase tracking?
└─ YES → Use ORCHESTRATION (/orchestration:plan)
```

---

## Relationship Flows

### Command Execution Flow
```
User types /command
       ↓
skill-router.js identifies parent skill
       ↓
Command loads instructions
       ↓
Delegates to Scripts/ (bash)
       ↓
audit-logger.js records execution
```

### Session Lifecycle Flow
```
Session starts
       ↓
session-start.js loads:
  - session-state.md
  - current-priorities.md
  - compaction-essentials.md
       ↓
Work happens (hooks fire on tool use)
       ↓
/checkpoint or session end
       ↓
session-stop.js saves state
```

### Complex Task Flow
```
User describes complex task
       ↓
orchestration-detector.js scores (>=9 auto-triggers)
       ↓
/orchestration:plan creates YAML
       ↓
Work progresses, commits linked
       ↓
/orchestration:status shows tree
```

### Agent Execution Flow
```
/agent <name> invoked
       ↓
Agent loads from .claude/agents/
       ↓
Executes with memory context
       ↓
subagent-stop.js logs completion
       ↓
Can chain to other agents
```

---

## Color Legend (for Canvas)

### Domain Colors

| Domain | Color | Components |
|--------|-------|------------|
| **1.STARTUP** | 🟢 Green | CLAUDE.md, settings.json |
| **2.KNOWLEDGE** | 🟣 Purple | context/, knowledge/, history/, _index.md |
| **3.EXECUTION** | 🔵 Blue | commands/, skills/, agents/, Scripts/ |
| **4.TRACKING** | 🟠 Orange | orchestration/ |
| **5.MONITORING** | 🔴 Red | hooks/, logs/ |
| **+SCAFFOLDING** | ⚪ Gray | _template*, external-sources/, MCP |

### Component Colors

| Color | Component | Domain | Role |
|-------|-----------|--------|------|
| 🟦 Blue | Skills | 3.EXECUTION | Workflow guides |
| 🟩 Green | Commands | 3.EXECUTION | Single actions |
| 🟧 Orange | Hooks | 5.MONITORING | Automatic behaviors |
| 🟪 Purple | Agents | 3.EXECUTION | Autonomous execution |
| 🟨 Yellow | Context | 2.KNOWLEDGE | Documentation |
| 🟫 Brown | Knowledge | 2.KNOWLEDGE | References/guides |
| 🟥 Red | Scripts | 3.EXECUTION | Bash operations |
| ⬜ Gray | Orchestration | 4.TRACKING | Task tracking |
| ⬛ Dark | Logs | 5.MONITORING | Activity records |
| 🔵 Cyan | External | +SCAFFOLDING | Symlinks |
| 📄 White | CLAUDE.md | 1.STARTUP | Entry point |
| 📑 Teal | Index Files | 2.KNOWLEDGE | Navigation hubs |
| 📝 Pink | Templates | +SCAFFOLDING | Component scaffolds |
| 📚 Indigo | History | 2.KNOWLEDGE | Learnings & decisions |
| ⚙️ Steel | Settings | 1.STARTUP | Configuration |

---

## File Format Summary

| Format | Used For | Location |
|--------|----------|----------|
| `.md` | Documentation, commands, agents, templates | Everywhere |
| `.js` | Hooks, automation | `.claude/hooks/` |
| `.yaml` | Orchestration, registries | `.claude/orchestration/`, root |
| `.json` | Config, settings, logs, tracking | `.claude/`, `.claude/logs/` |
| `.jsonl` | Audit logs, corrections | `.claude/logs/` |
| `.sh` | Scripts | `Scripts/` |
| `.ts` | Skill tools, templates | `.claude/skills/*/tools/` |

### Special File Patterns

| Pattern | Purpose | Example |
|---------|---------|---------|
| `CLAUDE.md` | Entry point for project | `.claude/CLAUDE.md` |
| `_index.md` | Navigation hub | `.claude/context/_index.md` |
| `_template*` | Component scaffolds | `_template-agent.md` |
| `settings.json` | Configuration | `.claude/settings.json` |
| `settings.local.json` | Accumulated permissions | `.claude/settings.local.json` |

---

## Maintenance

**When to Update**:
- New skill/command/hook added
- Component counts change significantly
- New patterns discovered
- Architecture relationships change

**Last Updated**: 2026-01-22 (Added 5-domain structure with domain tags on all components)
