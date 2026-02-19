# Headless Claude - Design Specification

**Status**: Draft
**Created**: 2026-02-08
**Author**: David Moneil + Claude Code planning session
**Planning Mode**: New Design
**Related**: [[Headless system idea]] (original brainstorm)

---

## Executive Summary

**Headless Claude** is a framework for running Claude Code autonomously — triggered by cron, n8n, scripts, or webhooks — with persona-based permissions, async human-in-the-loop approvals, a task/question queue, and pluggable execution engines. It unifies three existing patterns (`claude-scheduled.sh`, `plex-troubleshoot.sh`, `fresh-context-loop.sh`) into a cohesive, scalable system with explicit guardrails.

**Core principle**: Controlled autonomy. Every job runs within a named persona that defines exactly what it can do, what it can't, and when it needs to ask a human.

**Execution model**: Jobs run via **Claude Code CLI** (`claude -p`) in headless mode — not raw API calls. This means every headless job gets the full Claude Code experience: CLAUDE.md context, MCP servers, hooks, tool permissions, and settings.json. Claude Code handles the API billing internally.

---

## Problem Statement

### What exists today

| Pattern | What it does | Limitation |
|---------|-------------|------------|
| `claude-scheduled.sh` | Runs pre-defined jobs with permission tiers | Jobs hardcoded in script. No human-in-the-loop. No question queue. |
| `plex-troubleshoot.sh` | Agent-style execution with safety modes | One-off script. Not reusable for other agents. No approval flow. |
| `fresh-context-loop.sh` | Iterates tasks in fresh Claude instances | Only for task lists. No scheduling. No async questions. |

### What's missing

1. **Unified entry point**: No single way to add a new headless job
2. **Human-in-the-loop**: No mechanism for Claude to ask a question and wait for an answer
3. **Persona system**: Permission tiers exist but aren't tied to named profiles with specific objectives
4. **Job scheduling**: Each job needs its own crontab entry
5. **Question queue**: No way to park a question and resume later
6. **Engine flexibility**: Everything goes through Claude Code CLI — no routing to Ollama or scripts for lighter tasks
7. **Observability**: Logs exist but no unified view of all headless activity

---

## Architecture Overview

```
                        HEADLESS CLAUDE ARCHITECTURE

 TRIGGER LAYER                     CONTROL PLANE                    EXECUTION LAYER
 ─────────────                     ─────────────                    ───────────────

 ┌──────────┐                    ┌──────────────────┐
 │   Cron   │──┐                 │  MASTER          │             ┌────────────────┐
 │ (1 entry)│  │                 │  DISPATCHER       │────────────│ Claude Code CLI│
 └──────────┘  │                 │                    │            │ (claude -p)    │
               │  ┌────────────┐│  - Read registry   │            └────────────────┘
 ┌──────────┐  ├─▶│ dispatcher ││  - Check schedules │
 │   n8n    │──┤  │   .sh      ││  - Load persona    │            ┌────────────────┐
 │ webhook  │  │  └────────────┘│  - Route to engine │────────────│ Ollama         │
 └──────────┘  │        │       │  - Manage queue    │            │ (curl API)     │
               │        ▼       └──────────┬─────────┘            └────────────────┘
 ┌──────────┐  │  ┌────────────┐           │
 │  Script  │──┘  │  REGISTRY  │           │                      ┌────────────────┐
 │ (manual) │     │  .yaml     │           ├─────────────────────▶│ Script         │
 └──────────┘     └────────────┘           │                      │ (bash)         │
                                           │                      └────────────────┘
                  ┌────────────┐           │
                  │  PERSONAS  │◀──────────┘
                  │  (folders) │
                  │            │           ┌─────────────────────┐
                  │ prompt.md  │           │   QUESTION QUEUE    │
                  │ perms.yaml │           │                     │
                  │ config.yaml│           │  queue.json         │
                  └────────────┘           │  ├─ pending Qs      │
                                           │  ├─ answered Qs     │
                                           │  └─ expired Qs      │
                                           │                     │
                                           │  n8n watches ──────▶ Telegram
                                           │  human answers ────▶ queue.json
                                           └─────────────────────┘
```

---

## Core Components

### 1. Master Dispatcher (`dispatcher.sh`)

A single bash script that runs on a schedule (e.g., every 5 minutes via cron). **No LLM needed** — this is deterministic.

**What it does**:
1. Reads `registry.yaml` for all registered jobs
2. Checks each job's schedule against its `last_run` timestamp
3. For jobs that are due: loads the persona, builds the execution command, runs it
4. Handles locking (no parallel runs of the same job)
5. Updates `last_run` and writes execution log
6. Checks the question queue for answered questions → re-triggers waiting jobs

**Single crontab entry**:
```bash
*/5 * * * * /home/davidmoneil/AIProjects/.claude/jobs/dispatcher.sh >> /home/davidmoneil/AIProjects/.claude/logs/dispatcher.log 2>&1
```

**Why one cron entry**: Adding a new job = adding lines to `registry.yaml`. No crontab editing. No systemd files. The dispatcher handles all scheduling logic.

### 2. Job Registry (`registry.yaml`)

Central definition of all headless jobs. The dispatcher reads this every cycle.

```yaml
# .claude/jobs/registry.yaml
version: 1
defaults:
  engine: claude-code
  model: sonnet
  max_turns: 10
  max_budget_usd: 2.00
  timeout_minutes: 10

jobs:
  health-summary:
    description: "Quick infrastructure health check"
    persona: investigator
    schedule:
      type: interval
      every: 6h
    enabled: true
    # Override defaults if needed
    max_turns: 5
    max_budget_usd: 1.00

  upgrade-discover:
    description: "Check for Claude Code and MCP updates"
    persona: analyst
    schedule:
      type: cron
      expression: "0 6 * * 0"  # Sunday 6 AM
    enabled: true
    max_turns: 15
    max_budget_usd: 3.00

  plex-troubleshoot:
    description: "Diagnose and fix Plex issues"
    persona: troubleshooter
    schedule:
      type: on-demand  # Only via webhook/manual
    enabled: true
    trigger:
      webhook: true
      parameters:
        - name: issue
          required: false
          default: "full diagnostic"
        - name: safety_mode
          required: false
          default: "readonly"

  doc-sync-check:
    description: "Check if docs need sync with code"
    persona: investigator
    schedule:
      type: interval
      every: 24h
    enabled: true
    max_budget_usd: 1.00
```

### 3. Personas (Folder-per-Persona)

Each persona is a folder containing three files that define its identity, permissions, and configuration.

```
.claude/jobs/personas/
├── investigator/
│   ├── prompt.md          # Role description + instructions
│   ├── permissions.yaml   # What tools/actions are allowed
│   └── config.yaml        # Engine, model, cost settings
├── analyst/
│   ├── prompt.md
│   ├── permissions.yaml
│   └── config.yaml
├── troubleshooter/
│   ├── prompt.md
│   ├── permissions.yaml
│   └── config.yaml
└── _template/
    ├── prompt.md
    ├── permissions.yaml
    └── config.yaml
```

#### prompt.md (Role Identity)

```markdown
# Investigator Persona

You are running in **headless investigator mode**. Your job is to observe,
analyze, and report. You do NOT make changes.

## Behavior
- Read files, check status, query services
- Generate reports with findings
- Flag anything critical for human review
- If you need human input, write to the question queue

## Constraints
- NEVER modify files, configurations, or services
- NEVER run destructive commands
- If you discover something that needs action, recommend it — don't do it
```

#### permissions.yaml (Guardrails)

```yaml
# What this persona can do
persona: investigator
tier: discovery  # Maps to existing tier system

allowed_tools:
  - Read
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - mcp__git__git_status
  - mcp__git__git_log
  - mcp__filesystem__read_text_file
  - mcp__filesystem__list_directory
  - mcp__mcp-gateway__read_graph
  - mcp__mcp-gateway__search_nodes
  - mcp__mcp-gateway__docker  # Read container status

denied_actions:
  - Edit
  - Write
  - Bash  # No shell access
  - mcp__git__git_commit
  - mcp__git__git_add

# Action-specific approval requirements
approval_required:
  # These actions need human sign-off via the question queue
  - action: "restart any service"
    reason: "Service restarts affect availability"
  - action: "reboot any machine"
    reason: "Reboots are disruptive"
  - action: "delete any file or container"
    reason: "Destructive actions need human confirmation"

# What this persona can do WITHOUT asking
pre_approved:
  - "Read any file on the system"
  - "Query any Docker container status"
  - "Check service health endpoints"
  - "Search the web for documentation"
  - "Read the knowledge graph"
```

#### config.yaml (Execution Settings)

```yaml
persona: investigator

engine:
  default: claude-code       # Claude Code CLI (claude -p) — full context, MCP, hooks
  model: sonnet              # Which model Claude Code uses
  fallback: ollama/qwen2.5:7b-instruct  # If Claude Code unavailable or for cost savings
  # Future options: ollama/<model>, script (pure bash), openai/<model>

limits:
  max_turns: 10
  max_budget_usd: 2.00
  timeout_minutes: 10

output:
  format: json
  save_to: .claude/logs/headless/
  include_cost: true

session:
  persist: false  # --no-session-persistence
  # Set to true if you want to resume context across runs
```

### 4. Question Queue (`queue.json`)

The async human-in-the-loop mechanism. When a headless job needs human input, it writes to the queue. The next cycle picks up answers.

```json
{
  "version": 1,
  "questions": [
    {
      "id": "q-20260208-143022-plex",
      "created_at": "2026-02-08T14:30:22Z",
      "job": "plex-troubleshoot",
      "persona": "troubleshooter",
      "session_id": "headless-20260208-143000",
      "status": "pending",
      "priority": "high",
      "question": "Plex has been unresponsive for 10 minutes. Restart didn't help. Should I reboot MediaServer?",
      "context": "Tried: restart Plex service (failed), checked logs (OOM killer), checked CPU (98%)",
      "options": ["Approve reboot", "Wait and retry in 30 min", "Skip - I'll handle manually"],
      "default_after": "30m",
      "default_action": "Wait and retry in 30 min",
      "answer": null,
      "answered_at": null,
      "answered_by": null
    }
  ]
}
```

**Queue lifecycle**:
```
1. Job encounters decision point → writes question to queue.json
2. Job exits cleanly (no token burn while waiting)
3. n8n watches queue.json for new questions
4. n8n sends Telegram notification: "Headless Claude needs approval: [question]"
5. Human responds (Telegram reply → n8n → queue.json, OR n8n approval UI)
6. Next dispatcher cycle: sees answered question → re-runs the job with answer context
7. If no answer after default_after time → applies default_action
```

**Key design decisions**:
- Questions have a **timeout with default action** — the system doesn't block forever
- The queue is a flat JSON file — simple, git-trackable, no database needed
- n8n is the notification layer, not the queue itself — if n8n is down, the queue still works (just no notification)
- Questions include **options** so the human can make a quick choice (not open-ended)

### 5. Execution Wrapper (`executor.sh`)

Replaces the current `claude-scheduled.sh` with a persona-aware executor. This is what the dispatcher actually calls.

```bash
executor.sh --job health-summary
executor.sh --job plex-troubleshoot --param issue="won't start" --param safety_mode=safe-fixes
executor.sh --job upgrade-discover --engine ollama  # Override engine
```

**What it does**:
1. Loads persona (prompt.md + permissions.yaml + config.yaml)
2. Checks the question queue for any pending answers for this job
3. Builds the full prompt (persona prompt + job-specific context + queue answers)
4. Selects execution engine (claude-code, ollama, script)
5. Runs the job with configured limits
6. Captures output (JSON)
7. Checks output for question indicators → writes to queue if needed
8. Logs everything

### 6. n8n Integration Layer

n8n serves two roles:

**Role A: Trigger source** — n8n workflows can call `executor.sh` via webhook
```
n8n Schedule Trigger → Execute Command node → executor.sh --job health-summary
```

**Role B: Notification + approval** — n8n watches the queue and handles human interaction
```
n8n watches queue.json (file trigger or polling)
  → New question detected
  → Send Telegram message with approve/deny buttons
  → Wait for response
  → Write answer back to queue.json
```

This means the Plex troubleshooter from n8n would work like:
```
n8n detects Plex issue (or webhook from Plex)
  → calls executor.sh --job plex-troubleshoot --param issue="stream buffering"
  → troubleshooter persona runs, diagnoses issue
  → determines reboot needed → writes question to queue
  → executor exits
  → n8n picks up question → sends Telegram
  → you approve → n8n writes answer
  → next dispatcher cycle → re-runs with answer → executes reboot
```

---

## Personas — MVP Definitions

### Investigator (Read-Only)

**Purpose**: Observe, analyze, report. Never modify.
**Use cases**: Health checks, log analysis, status reports, doc-sync checks
**Tier**: Discovery
**Key constraint**: Zero write permissions. Can only read and report.

### Analyst (Read + Write Reports)

**Purpose**: Research, discover, and write findings to data files.
**Use cases**: Upgrade discovery, priority review, research tasks
**Tier**: Analyze
**Key constraint**: Can write to `.claude/logs/`, `.claude/skills/*/data/`, and report files. Cannot modify code or config.

### Troubleshooter (Read + Safe Fixes)

**Purpose**: Diagnose issues and apply safe, pre-approved fixes.
**Use cases**: Plex troubleshooting, service restart, container health
**Tier**: Custom (between Analyze and Implement)
**Key constraint**: Can restart services and clear caches. Cannot reboot machines, delete data, or modify configurations without approval.
**Approval required for**: Reboots, data deletion, config changes

### (Future) Implementer (Full Autonomy)

**Purpose**: Make code changes, commit, push.
**Use cases**: Automated dependency updates, lint fixes, doc generation
**Tier**: Implement
**Key constraint**: Must create git checkpoint before changes. Must pass tests. Must commit with `[headless]` prefix.
**Not in MVP**: Too risky to automate initially. Add after the framework proves stable.

---

## File Structure

```
.claude/jobs/
├── dispatcher.sh            # Master dispatcher (cron runs this)
├── executor.sh              # Persona-aware execution wrapper
├── registry.yaml            # All job definitions + schedules
├── queue.json               # Human-in-the-loop question queue
├── state/
│   ├── last-run.json        # Per-job last execution timestamps
│   └── locks/               # Per-job lock files (prevent parallel runs)
├── personas/
│   ├── _template/
│   │   ├── prompt.md
│   │   ├── permissions.yaml
│   │   └── config.yaml
│   ├── investigator/
│   │   ├── prompt.md
│   │   ├── permissions.yaml
│   │   └── config.yaml
│   ├── analyst/
│   │   ├── prompt.md
│   │   ├── permissions.yaml
│   │   └── config.yaml
│   └── troubleshooter/
│       ├── prompt.md
│       ├── permissions.yaml
│       └── config.yaml
├── claude-scheduled.sh      # (LEGACY - kept for backward compat)
└── README.md                # Documentation
```

**Logging**:
```
.claude/logs/headless/
├── dispatcher-YYYYMMDD.log      # Dispatcher activity
├── executions/
│   ├── health-summary-20260208-060000.json
│   ├── upgrade-discover-20260209-060000.json
│   └── plex-troubleshoot-20260208-143000.json
└── queue-history/
    └── answered-YYYYMM.jsonl   # Archive of answered questions
```

---

## Schedule Design

### Dispatcher Cycle

The dispatcher runs every 5 minutes. It's fast (pure bash, no LLM) — it only checks timestamps and launches jobs that are due.

```
*/5 * * * * → dispatcher.sh runs (~100ms)
  → health-summary due? (every 6h) → No, skip
  → upgrade-discover due? (Sunday 6 AM) → No, skip
  → queue has answered questions? → Yes! Re-run plex-troubleshoot
  → Done. Exit.
```

### Usage Projections (Claude Code CLI)

Since this runs through Claude Code CLI (not raw API), costs come from your Claude Code plan usage (turns, tokens). The `--max-turns` and `--max-budget-usd` flags control consumption per execution.

| Job | Frequency | Est. Turns/Run | Daily Turn Budget |
|-----|-----------|----------------|-------------------|
| health-summary | Every 6h (4/day) | ~5 | ~20 turns |
| upgrade-discover | Weekly | ~15 | ~2/day avg |
| doc-sync-check | Daily | ~5 | ~5 turns |
| plex-troubleshoot | On-demand (~2/week) | ~10 | ~3/day avg |
| **Total** | | | **~30 turns/day** |

> **Note**: Actual usage depends on turn count, context size, and model. Health-summary at 4x/day is the biggest consumer — could reduce to every 12h or route to Ollama.

### Usage Optimization Path (Future)

1. Route `health-summary` to Ollama (structured check, doesn't need frontier reasoning — zero Claude usage)
2. Route `doc-sync-check` to Ollama (file comparison, not complex)
3. Keep `upgrade-discover` and `plex-troubleshoot` on Claude Code (need web access and multi-step reasoning)
4. Use `--model` flag to run simpler jobs on Haiku instead of Sonnet where appropriate

---

## Implementation Phases

### Phase 1: Foundation (MVP)

**Goal**: Unified dispatcher + personas + 3 working jobs

| Task | Description | Effort |
|------|-------------|--------|
| Create persona folders | investigator, analyst, troubleshooter with prompt/perms/config | 1-2h |
| Build `executor.sh` | Persona-aware execution wrapper (replaces raw `claude -p` calls) | 2-3h |
| Build `dispatcher.sh` | Master scheduler that reads registry and runs due jobs | 2-3h |
| Create `registry.yaml` | Define health-summary, upgrade-discover, plex-troubleshoot | 30min |
| Migrate existing jobs | Port claude-scheduled.sh jobs to new persona format | 1h |
| Test end-to-end | Cron → dispatcher → executor → output | 1-2h |

**Deliverable**: Drop-in replacement for current `claude-scheduled.sh` with persona system.

### Phase 2: Question Queue + Approvals

**Goal**: Async human-in-the-loop via queue + n8n + Telegram

| Task | Description | Effort |
|------|-------------|--------|
| Implement `queue.json` management | Write/read/expire questions in bash | 1-2h |
| Add queue writing to executor | Detect when Claude asks a question, write to queue | 1-2h |
| Build n8n queue watcher workflow | Poll queue.json, send Telegram, capture answer | 2-3h |
| Set up Telegram bot integration | n8n Telegram node for send/receive | 1h |
| Add queue reader to dispatcher | Check for answered questions, re-trigger jobs | 1h |
| Test approval flow end-to-end | Plex troubleshoot → needs reboot → Telegram → approve → reboot | 2h |

**Deliverable**: Plex troubleshooter can ask for reboot permission and wait for your approval.

### Phase 3: Engine Routing + Observability

**Goal**: Route jobs to different engines, unified monitoring

| Task | Description | Effort |
|------|-------------|--------|
| Add Ollama engine to executor | `curl` to Ollama API as alternative to `claude -p` | 2h |
| Add engine selection logic | Per-persona defaults with per-job overrides | 1h |
| Create observability dashboard | n8n workflow or simple HTML page showing job history, costs, queue status | 3-4h |
| Add Grafana integration | Push headless metrics to Prometheus/Grafana | 2h |
| Cost tracking and alerts | Track per-job costs, alert when approaching budget | 1-2h |

**Deliverable**: Some jobs run on Ollama, you can see all headless activity in one place.

### Phase 4: Advanced Capabilities (Future)

| Capability | Description |
|------------|-------------|
| Implementer persona | Full autonomy with git checkpoints for trusted automation |
| Multi-step workflows | Chain personas (investigator → analyst → troubleshooter) |
| Fresh-context mode | Integrate fresh-context-loop.sh as an execution mode |
| Webhook API | REST endpoint for external systems to trigger any job |
| n8n visual orchestration | Complex multi-step flows managed entirely in n8n UI |

---

## Beads Integration (Task Management)

**This is a Phase 1 requirement**, not a future enhancement. Headless jobs must participate in the same task management system as interactive sessions.

### Why This Matters

The upgrade-discover job is a perfect example. Today it writes results to a JSON file and that's it. With Beads integration:

1. **Before execution**: The executor checks Beads for any open tasks related to this job
2. **During execution**: If the job finds something (e.g., new Claude Code version), it creates a Beads task
3. **After execution**: If it completed work tracked in Beads, it closes the task with evidence

This means your interactive sessions and headless jobs share a single view of what needs doing.

### How It Works

Since headless jobs run via `claude -p` in the AIProjects directory, they load CLAUDE.md which already describes the Beads system. Claude Code will know about `bd` commands. The key is **permissions** — each persona needs explicit access to `bd`.

#### Persona Permissions for Beads

```yaml
# In permissions.yaml for each persona

beads_access:
  investigator:
    - bd list       # Can read tasks
    - bd show       # Can view task details
    # Cannot create, update, or close tasks
    # Reports findings in output — interactive session creates tasks if needed

  analyst:
    - bd list       # Can read tasks
    - bd show       # Can view task details
    - bd create     # Can create new tasks from discoveries
    # Cannot close tasks — human reviews findings first

  troubleshooter:
    - bd list       # Can read tasks
    - bd show       # Can view task details
    - bd create     # Can create follow-up tasks
    - bd update     # Can update task status
    - bd close      # Can close tasks it completed (with evidence)
```

This translates to `--allowedTools` entries:
```bash
# Investigator: read-only Beads
--allowedTools "Bash(bd list:*),Bash(bd show:*)"

# Analyst: read + create
--allowedTools "Bash(bd list:*),Bash(bd show:*),Bash(bd create:*)"

# Troubleshooter: full Beads access
--allowedTools "Bash(bd list:*),Bash(bd show:*),Bash(bd create:*),Bash(bd update:*),Bash(bd close:*)"
```

#### Example: Upgrade Discover + Beads

```
Analyst persona runs upgrade-discover job:
  1. Reads current Beads tasks: bd list --label project:aiprojects
  2. Checks external sources for Claude Code updates
  3. Finds: Claude Code 2.3.0 released (current: 2.2.1)
  4. Creates Beads task:
     bd create "Upgrade Claude Code to 2.3.0" -t task -p 2 \
       -l "domain:infrastructure,project:aiprojects,severity:medium,source:headless" \
       -d "Discovered via headless upgrade-discover job on 2026-02-09. Release notes: [url]"
  5. Writes discovery report to .claude/logs/headless/
  6. Exits
```

Next interactive session: you see the task in `bd list` and decide when to upgrade.

#### Example: Plex Troubleshooter + Beads

```
Troubleshooter persona runs plex-troubleshoot job:
  1. Checks Beads for open Plex tasks: bd list --label project:plex
  2. Finds: existing task "Plex buffering on 4K streams"
  3. Claims it: bd update <id> --status in_progress --claim
  4. Diagnoses: transcode cache full, clears it
  5. Verifies: Plex streaming works
  6. Closes task: bd close <id> --reason "Cleared transcode cache, 4K streaming restored"
  7. If issue persists: creates new task with findings instead of closing
```

#### Beads Labels for Headless Jobs

All tasks created by headless jobs use `source:headless` label:
```bash
bd create "..." -l "...,source:headless,agent:claude"
```

This lets you filter headless-created tasks:
```bash
bd list --label source:headless           # All headless discoveries
bd list --label source:headless --status open  # Unaddressed findings
```

#### Actor Attribution

The `beads-actor.sh` hook already sets `BEADS_ACTOR` per session. For headless jobs, the executor sets:
```bash
export BEADS_ACTOR="headless-${JOB_NAME}-$(date +%Y%m%d)"
```

This gives you audit trail: "who created this task?" → "headless-upgrade-discover-20260209"

### Integration with Other Systems

Headless Claude participates in the same ecosystem as interactive sessions:

| System | Interactive Session | Headless Job | Shared? |
|--------|-------------------|--------------|---------|
| **Beads** | Full access | Persona-scoped access | Same database |
| **Git** | Full access | Persona-scoped | Same repo |
| **MCP servers** | All loaded | Per-persona selection | Same servers |
| **CLAUDE.md** | Full context | Full context | Same file |
| **Audit logs** | Via hooks | Via executor logging | Same log format |
| **Memory MCP** | Full access | Per-persona access | Same graph |
| **Orchestration** | Full | Can read/update tasks | Same YAML files |

---

## AIProjects Documentation Updates

When implementing Headless Claude, these AIProjects files need updating to keep the system consistent. This is a checklist for the implementation phase — **not done during design**.

### Priority 1: Critical (Must update during Phase 1)

| File | What to Update | Why |
|------|---------------|-----|
| **`.claude/CLAUDE.md`** | Add "Headless Claude" section under Automation Routing (~line 252). Reference new dispatcher, personas, registry. | This is what headless jobs read for context. Must know about itself. |
| **`.claude/context/compaction-essentials.md`** | Add Headless Claude summary to Scheduled Jobs section (~line 50). | Survives context compression. Headless must persist through compaction. |
| **`.claude/jobs/README.md`** | Rewrite Claude Autonomous Execution section (~line 59). Document new dispatcher + personas + registry. | Primary documentation for the jobs system. |
| **`.claude/context/patterns/autonomous-execution-pattern.md`** | Add "Superseded by Headless Claude" header. Keep as reference for the permission tier system (still used). Link to new design. | Don't delete — the permission tiers and CLI reference are still valid. |

### Priority 2: High (Update during Phase 1-2)

| File | What to Update | Why |
|------|---------------|-----|
| **`.claude/context/patterns/_index.md`** | Add Headless Claude entry. Update autonomous-execution entry with "see also" link. | Pattern discovery index. |
| **`.claude/context/_index.md`** | Add Headless Claude to the systems/integrations section. | Central context discovery file. |
| **`.claude/context/integrations/n8n-claude-integration.md`** | Add section on n8n's role in Headless Claude (queue watcher, approval flow, Telegram). | n8n integration docs. |
| **`.claude/context/patterns/fresh-context-pattern.md`** | Add note that fresh-context is a Phase 4 execution mode for Headless Claude. | Shows relationship. |

### Priority 3: Medium (Update during Phase 2-3)

| File | What to Update | Why |
|------|---------------|-----|
| **`.claude/skills/_index.md`** | Add Headless Claude if it becomes a skill (likely Phase 3). | Skill discovery. |
| **`paths-registry.yaml`** | Add `.claude/jobs/personas/`, `.claude/jobs/registry.yaml`, queue paths. | Path source of truth. |
| **`.claude/context/standards/severity-status-system.md`** | Ensure headless task severities align with existing system. | Consistency. |

### Priority 4: Low (Archive/reference only)

| File | Action | Why |
|------|--------|-----|
| **`.claude/context/designs/fresh-context-agent-mode.md`** | No change needed | Historical design doc |
| **`.claude/planning/specs/2026-01-20-autonomous-execution-deployment.md`** | No change needed | Deployment history |

### What NOT to Update

- **`claude-scheduled.sh`**: Keep as-is for backward compatibility during Phase 1. The executor will replace it, but it still works independently.
- **`plex-troubleshoot.sh`**: Keep as-is. Migrate to persona system as part of Phase 1, but don't delete the original until verified.
- **`fresh-context-loop.sh`**: Keep as-is. Phase 4 integration, not MVP.

---

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Single dispatcher cron entry | Yes | Simpler than per-job cron. Adding jobs = editing YAML, not crontab. |
| n8n for approval, Telegram for notification | Yes | n8n already running. Telegram adds mobile convenience. Queue file works even if both are down. |
| Folder-per-persona | Yes | Separates concerns. Each file has one purpose. Easy to audit permissions. |
| Claude Code CLI first, pluggable engines | Yes | Start with Claude Code CLI (gets full context, MCP, hooks). Config supports Ollama/other engines for lighter jobs later. |
| Question queue as JSON file | Yes | Simple, git-trackable, no database dependency. n8n watches it. |
| 5-minute dispatcher cycle | Yes | Fast enough for most use cases. On-demand jobs use direct webhook instead. |
| Implementer persona deferred | Yes | Too risky for MVP. Prove the framework with read/analyze/troubleshoot first. |
| Project name: Headless Claude | Yes | Clear, descriptive, matches the Obsidian project folder. |

---

## Open Questions (For Later Sessions)

1. **Telegram bot setup**: Create a dedicated bot? Or use n8n's built-in Telegram integration? Need to set up bot token.
2. **Queue expiry policy**: How long should unanswered questions wait? 30 min? 24h? Configurable per-question?
3. **Parallel execution**: Should the dispatcher allow multiple jobs to run simultaneously? Or strictly sequential?
4. **Health-summary frequency**: 4x/day at $60/mo or 2x/day at $30/mo? Or route to Ollama for ~$0?
5. **Fresh-context integration**: Should long-running jobs (upgrade-discover) use fresh-context mode? Or is that overkill?
6. **Webhook authentication**: How to secure the on-demand trigger endpoint? API key? n8n auth?

---

## Relationship to Existing Systems

```
┌────────────────────────────────────────────────────────────────────┐
│                        AIPROJECTS ECOSYSTEM                         │
│                                                                     │
│  ┌──────────────────┐     ┌──────────────────────────────────────┐ │
│  │  Interactive      │     │  HEADLESS CLAUDE (this design)       │ │
│  │  Claude Code      │     │                                      │ │
│  │                   │     │  dispatcher.sh ──▶ executor.sh       │ │
│  │  /commands        │     │       │                 │            │ │
│  │  /skills          │     │  registry.yaml    personas/         │ │
│  │  /agents          │     │       │                 │            │ │
│  │  hooks            │     │  queue.json ◀──── n8n ──── Telegram │ │
│  │                   │     │                                      │ │
│  └────────┬──────────┘     └──────────────┬───────────────────────┘ │
│           │                               │                         │
│           │  Shared infrastructure:        │                         │
│           ├── CLAUDE.md (context)──────────┤                         │
│           ├── .claude/settings.json ───────┤                         │
│           ├── Beads (task tracking) ───────┤                         │
│           ├── MCP servers ─────────────────┤                         │
│           ├── Git (version control) ───────┤                         │
│           └── .claude/logs/ (audit) ───────┘                         │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

**Key insight**: Headless Claude and Interactive Claude share the same infrastructure (CLAUDE.md, MCP servers, Beads, git). The headless system adds scheduling, personas, and async approval on top of the same foundation.

---

## Success Criteria

### MVP (Phase 1 + 2)

- [ ] One crontab entry runs the entire headless system
- [ ] Adding a new job = creating a persona folder + adding to registry.yaml
- [ ] 3 jobs running: health-summary, upgrade-discover, plex-troubleshoot
- [ ] Plex troubleshooter can ask for reboot approval via Telegram
- [ ] All executions logged with cost tracking
- [ ] No job can exceed its defined permission boundaries

### Full System (Phase 3+)

- [ ] Some jobs route to Ollama to minimize cost
- [ ] Observability dashboard shows all headless activity
- [ ] Daily Claude Code usage under 50 turns with health checks running
- [ ] System runs unattended for 30 days without intervention

---

## Next Steps

1. Review this design — any gaps or concerns?
2. Create a Beads task for Phase 1 implementation
3. Build the persona folders and dispatcher in a focused session
4. Test with health-summary as the first live job
