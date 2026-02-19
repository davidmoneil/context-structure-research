---
created: 2026-02-12T11:50
updated: 2026-02-12T11:50
tags:
  - project/aiprojects
  - project/aifred
  - depth/deep
  - domain/ai
  - domain/mechanics
  - type/diagram
---
# How AIfred Answers Questions — A Visual Story

> **Purpose**: Show the **runtime behavior** of Claude Code when answering questions in sequence
> **Complements**: [[AIProjects-Architecture-Canvas]] (static structure) | [[AIProjects-Architecture-Domains]] (5 domains) | [[Agent AIFred]] (AIfred components)
> **What's different here**: Those canvases show *what exists*. This document shows *what happens when you ask a question*.

---

## The Story in 30 Seconds

Two questions. Two completely different flows. Same system.

| | Question 1 | Question 2 |
|---|---|---|
| **Ask** | "What are the top priorities?" | "Plan the Document Guard community launch" |
| **Type** | Read State | Execute Work |
| **Hook response** | Pass-through (score: 2) | Intervenes (score: 8) |
| **Systems touched** | Hooks → Beads → Response | Hooks → PARC → Memory → Context → Beads → Skills → Agents → Cross-project |
| **Story told** | Where tasks come from (3 origin paths) | How the full stack orchestrates complex work |

---

## Act 0: Session Start — The Foundation

Before any question is asked, the system loads its operating context. This is what makes the first response instant rather than cold.

```mermaid
sequenceDiagram
    actor U as David
    participant CC as Claude Code
    participant H as Hooks
    participant K as Knowledge Layer
    participant MCP as MCP Servers

    U->>CC: Starts session (terminal)
    activate CC

    Note over CC: CLAUDE.md loads automatically<br/>~500 lines: rules, patterns, routing

    Note over CC: Auto-memory loads<br/>MEMORY.md: voice prefs, key decisions

    CC->>H: SessionStart event fires
    activate H
    H->>K: session-start.js gathers context
    K-->>H: Branch: main, 7 uncommitted<br/>Last session: ROCm investigation<br/>Status: IDLE<br/>Top priorities snapshot
    H-->>CC: Context injected
    deactivate H

    CC->>MCP: 7 servers connect
    Note over MCP: Docker | Filesystem | Git<br/>Memory | Fetch | Browser | GitHub
    MCP-->>CC: Ready

    Note over CC: Foundation loaded.<br/>16 hooks armed.<br/>11 skills available.<br/>Waiting for first question...
    deactivate CC
```

### What's Loaded at Startup

| Layer | Source | Content | Token Cost |
|-------|--------|---------|------------|
| **Rules** | `CLAUDE.md` | Project rules, patterns, routing logic, MCP config | ~2,000 |
| **Memory** | `MEMORY.md` (auto-memory) | Voice preferences, key decisions, value framework | ~200 |
| **Session Context** | `session-start.js` hook | Git branch, last session summary, current state | ~500 |
| **Skills Index** | `skills/_index.md` | 11 skills, 35+ commands available | Referenced on demand |
| **MCP Connections** | `settings.json` | 7 servers for Docker, Git, files, memory, GitHub, browser, SSH | Persistent |

**Key insight**: Claude Code doesn't start from zero. By the time you type your first question, it already knows what you were doing last session, what's pending, and what tools are available.

---

## Act 1: "What are the top priorities?"

A deceptively simple question. The hooks barely activate — but the answer reveals three completely different paths that feed tasks into the system.

```mermaid
sequenceDiagram
    actor U as David
    participant CC as Claude Code
    participant H as Hooks
    participant BD as Beads (SQLite)
    participant AL as Audit Log

    U->>CC: "What are the top priorities?"
    activate CC

    rect rgba(255, 245, 230, 0.3)
        Note over CC,H: Hook Evaluation (3 hooks fire)
        CC->>H: UserPromptSubmit event
        activate H
        Note over H: project-detector → No URL detected<br/>orchestration-detector → Score: 2/20 (simple query)<br/>self-correction-capture → No correction
        H-->>CC: All clear — pass through
        deactivate H
    end

    rect rgba(230, 245, 255, 0.3)
        Note over CC,BD: Beads Query
        CC->>BD: bd list --status open
        activate BD
        Note over BD: SQLite query<br/>Filters, sorts by priority<br/>Applies label grouping
        BD-->>CC: 28 open tasks returned
        deactivate BD
    end

    CC->>AL: audit-logger.js → tool execution logged
    Note over AL: .claude/logs/audit.jsonl

    CC->>U: Formatted priority list<br/>2 HIGH | 8 MEDIUM | 18 LOW
    deactivate CC
```

### But Where Did Those 28 Tasks Come From?

This is where the story gets interesting. The unified Beads database contains tasks from **three completely different origin paths**:

```mermaid
flowchart TB
    subgraph pathA["Path A: Human Created"]
        direction TB
        A1["David runs command"]
        A2["bd create 'Review Document Guard<br/>monitoring approach'"]
        A3["Beads DB"]
        A1 --> A2 --> A3
    end

    subgraph pathB["Path B: Headless Dispatch (Autonomous)"]
        direction TB
        B1["System cron (every 5 min)"]
        B2["dispatcher.sh checks registry.yaml"]
        B3["abs-librarian job is due"]
        B4["Headless Claude session spawns"]
        B5["Scans AudioBookShelf library"]
        B6["bd create 'ABS naming: Malformed<br/>author folder - hawaii'"]
        B7["Beads DB"]
        B1 --> B2 --> B3 --> B4 --> B5 --> B6 --> B7
    end

    subgraph pathC["Path C: Orchestration Plan"]
        direction TB
        C1["Complex task decomposed"]
        C2["/orchestration:plan creates YAML"]
        C3["Each phase becomes a task"]
        C4["bd create 'Headless Claude<br/>Phase 3: Engine routing'"]
        C5["Beads DB"]
        C1 --> C2 --> C3 --> C4 --> C5
    end

    A3 --> Q["bd list → Unified view<br/>28 tasks from all 3 paths<br/>sorted by priority"]
    B7 --> Q
    C5 --> Q
    Q --> R["David sees one clean list"]

    style pathA fill:#fff5e6,stroke:#f0a030,color:#333
    style pathB fill:#e6f0ff,stroke:#3080f0,color:#333
    style pathC fill:#e6ffe6,stroke:#30a030,color:#333
    style Q fill:#f5f5f5,stroke:#666,color:#333
    style R fill:#fff,stroke:#333,color:#333
```

### What This Demonstrates

| Concept | How It Shows |
|---------|-------------|
| **Beads as unified task system** | All 28 tasks in one query, regardless of origin |
| **Headless dispatch autonomy** | Tasks appear without David doing anything (ABS librarian found 8 naming issues at 3 AM) |
| **Orchestration decomposition** | Complex plans auto-create trackable subtasks |
| **Hook intelligence** | orchestration-detector scored this 2/20 — correctly identified as a simple read query |
| **Audit trail** | Every tool call logged to JSONL (Loki-ready) |

---

## Act 2: "Plan the Document Guard community launch"

NOW the full system activates. This single question touches hooks, design patterns, memory, context files, the task system, skills, agents, and cross-project access.

```mermaid
sequenceDiagram
    actor U as David
    participant CC as Claude Code
    participant H as Hooks
    participant M as Auto-Memory
    participant K as Context Files
    participant BD as Beads
    participant SK as Orchestration Skill
    participant AG as deep-research Agent
    participant EXT as ~/Code/AIfred

    U->>CC: "Plan the Document Guard community launch"
    activate CC

    rect rgba(255, 235, 220, 0.3)
        Note over CC,H: Phase 1: Hook Intelligence
        CC->>H: UserPromptSubmit event
        activate H
        Note over H: orchestration-detector scores: 7/20<br/>"plan" verb (+2) · "launch" scope (+2)<br/>"community" multi-component (+1)<br/>Score 4-8 = SUGGEST orchestration
        H-->>CC: Suggests: Consider /orchestration:plan
        deactivate H
    end

    rect rgba(235, 230, 255, 0.3)
        Note over CC,K: Phase 2: PARC Design Review
        CC->>K: Prompt — Parse the request
        CC->>K: Assess — Check context/patterns/
        K-->>CC: Orchestration pattern exists<br/>Community launch = multi-phase
        CC->>K: Relate — Scope and impact?
        K-->>CC: Touches: AIfred, Beads, external platforms
        Note over CC: Create → Apply orchestration pattern
    end

    rect rgba(220, 245, 220, 0.3)
        Note over CC,EXT: Phase 3: Knowledge Cascade
        CC->>M: Load auto-memory
        M-->>CC: "Document Guard = genuine plugin candidate"<br/>"Universal problem, nothing in marketplace"<br/>"Self-contained, works immediately"

        CC->>K: Load context/projects/aifred.md
        K-->>CC: Project context, Document Guard phases<br/>Phase 2 ready, Phase 3 planned

        CC->>BD: bd list --label project:aifred
        BD-->>CC: Found existing tasks:<br/>bes: Phase 2 Community Launch<br/>mqg: Phase 3 Content<br/>xfc: Phase 4 Sustain

        CC->>EXT: Read AIfred README + plugin source
        EXT-->>CC: Document Guard capabilities<br/>Installation instructions<br/>Supported editors
    end

    rect rgba(220, 235, 255, 0.3)
        Note over CC,AG: Phase 4: Orchestration & Execution
        CC->>SK: Activate orchestration skill
        activate SK
        SK-->>CC: Creates YAML plan:<br/>Phase 1: Content preparation<br/>Phase 2: Platform posts<br/>Phase 3: Engagement
        deactivate SK

        CC->>AG: Spawn deep-research agent
        activate AG
        Note over AG: Researches:<br/>- Claude Code plugin landscape<br/>- Community sentiment on doc protection<br/>- Competitive positioning
        AG-->>CC: Research findings
        deactivate AG
    end

    rect rgba(255, 245, 220, 0.3)
        Note over CC,BD: Phase 5: Task Lifecycle
        CC->>BD: bd update bes --status in_progress --claim
        CC->>BD: bd create subtasks for each phase
        CC->>BD: Link to orchestration YAML
        Note over BD: Full audit trail via events.jsonl
    end

    CC->>U: Orchestrated plan with:<br/>- Competitive analysis<br/>- Phased rollout schedule<br/>- Claimed & tracked tasks
    deactivate CC
```

### The Knowledge Cascade — What Loads and When

This is the core of how Claude Code "knows things." It's not one file — it's a cascade of increasingly specific knowledge:

```mermaid
flowchart TB
    subgraph L1["Layer 1: Always Loaded (Session Start)"]
        direction LR
        A1["CLAUDE.md<br/>~500 lines of rules"]
        A2["MEMORY.md<br/>Voice, decisions, values"]
        A3["Session context<br/>Branch, state, last session"]
    end

    subgraph L2["Layer 2: Pattern Matching (PARC)"]
        direction LR
        B1["context/patterns/<br/>18+ design patterns"]
        B2["Orchestration pattern<br/>matched for this request"]
    end

    subgraph L3["Layer 3: Project Knowledge"]
        direction LR
        C1["context/projects/aifred.md<br/>Project overview, phases"]
        C2["Auto-memory entries<br/>Document Guard = plugin candidate"]
        C3["Beads tasks<br/>bes, mqg, xfc found"]
    end

    subgraph L4["Layer 4: Cross-Project Source"]
        direction LR
        D1["~/Code/AIfred/README.md<br/>Feature details"]
        D2["~/Code/AIfred/src/<br/>Document Guard source"]
    end

    subgraph L5["Layer 5: External Research"]
        direction LR
        E1["deep-research agent<br/>Web search, competitive analysis"]
    end

    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5

    style L1 fill:#e8f5e9,stroke:#4caf50,color:#333
    style L2 fill:#e3f2fd,stroke:#2196f3,color:#333
    style L3 fill:#fff3e0,stroke:#ff9800,color:#333
    style L4 fill:#fce4ec,stroke:#e91e63,color:#333
    style L5 fill:#f3e5f5,stroke:#9c27b0,color:#333
```

### What This Demonstrates

| Concept | How It Shows |
|---------|-------------|
| **Hook intelligence** | orchestration-detector scores complexity, suggests (not forces) orchestration |
| **PARC design review** | Checks existing patterns before acting — finds orchestration pattern applies |
| **Auto-memory persistence** | Value assessment from a previous session ("genuine plugin candidate") informs today's plan |
| **Beads awareness** | Finds 3 existing Document Guard tasks — doesn't create duplicates |
| **Cross-project architecture** | AIProjects is a hub — reads AIfred code from `~/Code/AIfred/` |
| **Skill activation** | Orchestration skill creates phased YAML plan with dependencies |
| **Agent delegation** | deep-research runs autonomously for competitive analysis |
| **Capability layering** | Content creation = AI-appropriate task (needs judgment, not scriptable) |
| **Full task lifecycle** | Find existing task → claim → create subtasks → link to plan → track |
| **Audit trail** | Every tool call logged, every Beads change tracked with actor provenance |

---

## Background: The Headless Dispatch

Running silently between sessions, the dispatch system extends Claude's presence into autonomous monitoring and task creation.

```mermaid
sequenceDiagram
    participant CRON as System Cron
    participant DISP as dispatcher.sh
    participant REG as registry.yaml
    participant EXEC as executor.sh
    participant CL as Headless Claude
    participant BD as Beads

    Note over CRON,BD: Runs every 5 minutes, independent of user sessions

    CRON->>DISP: */5 * * * *
    activate DISP
    DISP->>REG: Check 6 job schedules
    REG-->>DISP: abs-librarian due (6h interval)

    Note over DISP: Checks quiet hours:<br/>Weekday 10pm-7am = silent<br/>Weekend 11pm-9am = silent

    DISP->>EXEC: Run abs-librarian
    activate EXEC

    Note over EXEC: Safety constraints:<br/>Persona: librarian<br/>Budget: $2.00 max<br/>Timeout: 10 min<br/>Max turns: 10

    EXEC->>CL: Headless session + job prompt
    activate CL
    CL->>CL: Scan AudioBookShelf library
    CL->>CL: Detect naming anomalies

    CL->>BD: bd create "Malformed author folder"
    CL->>BD: bd create "Loose root file"
    CL->>BD: bd create "Reversed series-author format"

    Note over CL: 6 tasks created this run<br/>Labels: source:headless, action:rename-safe

    CL-->>EXEC: Job complete
    deactivate CL
    EXEC-->>DISP: Logged to last-run.json
    deactivate EXEC
    deactivate DISP

    Note over BD: These tasks sit quietly until...<br/>David asks "What are top priorities?"<br/>→ They appear in Act 1's unified list
```

### Active Headless Jobs

| Job | Schedule | Persona | What It Does |
|-----|----------|---------|-------------|
| `health-summary` | Every 6h | Investigator (read-only) | Quick infrastructure health check |
| `upgrade-discover` | Sunday 6 AM | Analyst (read + write) | Claude Code, MCP, watched task upgrades |
| `abs-librarian` | Every 6h | Librarian (permission-based) | AudioBookShelf naming cleanup |
| `doc-sync-check` | Every 24h | Investigator | Check if docs need sync with code |
| `priority-review` | Monday 7 AM | Investigator | Review Beads tasks, flag stale items |
| `plex-troubleshoot` | On-demand | Troubleshooter (safe fixes) | Diagnose Plex issues via webhook |

### What This Demonstrates

| Concept | How It Shows |
|---------|-------------|
| **Autonomous operation** | System works when David is asleep — abs-librarian runs at 3 AM |
| **Persona safety model** | Each job has permission boundaries (investigator can't modify, troubleshooter can only do safe fixes) |
| **Budget control** | Max $2/run, max 10 min, max 10 turns — prevents runaway costs |
| **Quiet hours** | Respects DND schedule — batches notifications for morning |
| **Beads integration** | Headless jobs create tasks with `source:headless` label — full provenance |
| **Capability layering** | Dispatch is bash (deterministic), jobs use Claude (judgment needed) |

---

## The Complete Picture — Q1 vs Q2

```mermaid
flowchart LR
    subgraph Q1["Q1: 'What are the top priorities?'"]
        direction TB
        Q1A["Hooks evaluate<br/>Score: 2 → pass through"] --> Q1B["Beads query<br/>28 tasks returned"]
        Q1B --> Q1C["Format & respond"]
    end

    subgraph Q2["Q2: 'Plan the Document Guard launch'"]
        direction TB
        Q2A["Hooks evaluate<br/>Score: 7 → suggest orchestration"]
        Q2A --> Q2B["PARC design review<br/>Pattern match: orchestration"]
        Q2B --> Q2C["Knowledge cascade<br/>Memory + Context + Beads + Cross-project"]
        Q2C --> Q2D["Skill activation<br/>Orchestration creates YAML plan"]
        Q2D --> Q2E["Agent spawn<br/>deep-research: competitive analysis"]
        Q2E --> Q2F["Beads lifecycle<br/>Claim → subtasks → track"]
        Q2F --> Q2G["Respond with<br/>orchestrated plan"]
    end

    U["David"] --> Q1
    Q1 --> U2["David"]
    U2 --> Q2
    Q2 --> U3["David"]

    style Q1 fill:#fff5e6,stroke:#f0a030,color:#333
    style Q2 fill:#e6f0ff,stroke:#3080f0,color:#333
```

---

## Component Legend

Maps diagram participants back to actual files and tools.

| Diagram Label | Actual Component | Location |
|---------------|-----------------|----------|
| **Claude Code** | Claude Code CLI (Opus 4.6) | Terminal session |
| **Hooks** | 16 active JavaScript hooks | `.claude/hooks/*.js` |
| **Auto-Memory** | Persistent memory files | `~/.claude/projects/.../memory/` |
| **Context Files** | 171 infrastructure docs | `.claude/context/` |
| **Beads** | SQLite task database + CLI | `.beads/beads.db`, `bd` command |
| **Orchestration Skill** | Skill + YAML plans | `.claude/skills/orchestration/`, `.claude/orchestration/*.yaml` |
| **Agents** | 17 autonomous task executors | `.claude/agents/*.md` |
| **External Projects** | Code repositories | `~/Code/AIfred/`, `~/Code/...` |
| **MCP Servers** | 7 connected servers | `settings.json` MCP config |
| **Headless Dispatch** | Cron-based job system | `.claude/jobs/dispatcher.sh`, `.claude/jobs/registry.yaml` |
| **Audit Log** | JSONL event stream | `.claude/logs/audit.jsonl` |

---

## How This Relates to Other Diagrams

| Canvas | Shows | This Document Adds |
|--------|-------|-------------------|
| [[AIProjects-Architecture-Canvas]] | All 171+ components and their connections | **When** and **why** those connections activate |
| [[AIProjects-Architecture-Simple]] | Friendly analogies (house, cookbook, etc.) | **Real execution flow** through those analogies |
| [[AIProjects-Architecture-Domains]] | 5 functional domains (Startup → Monitoring) | **How domains hand off** during question processing |
| [[Agent AIFred]] | AIfred-specific components and profiles | **Runtime behavior** of those components |

This is the **dynamic complement** to those static views. Together they tell the complete story: what exists, how it's organized, and how it responds.

---

*Last updated: 2026-02-12 | Tracks AIProjects architecture as of session date*
