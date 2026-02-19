# Headless Claude - Implementation Guide

**Status**: Ready for Implementation
**Created**: 2026-02-08
**Prerequisite**: [[Headless Claude - Design Specification]]
**Purpose**: Step-by-step build guide with gap analysis, migration plan, and exact commands

---

## Gap Analysis: Current State vs Design

### What Actually Exists (Reality Check)

#### Crontab (actual `crontab -l`)
```
# Only 2 entries are actually scheduled:
0 3 * * * claude-history-cleanup.sh       # History cleanup
0 * * * * openclaw health-check.sh        # OpenClaw health (hourly)
```

**Gap**: The README documents 4+ active cron jobs (daily-sync, cleanup-agent-sessions, weekly-context-analysis, upgrade-discover) but **none of these are in the actual crontab**. They exist as scripts but aren't scheduled.

#### Jobs Directory (actual files)
```
.claude/jobs/
  claude-scheduled.sh           # Exists, tested Jan 20-25
  cleanup-agent-sessions.sh     # Exists, NOT in crontab
  daily-sync.sh                 # Exists, NOT in crontab
  README.md                     # Comprehensive but out-of-date
```

**Gap**: No personas/ directory, no registry.yaml, no queue.json, no dispatcher.sh, no executor.sh.

#### Execution History
```
.claude/logs/scheduled/
  upgrade-discover ran: Jan 20 (3 attempts), Jan 25 (1 attempt via cron)
  health-summary ran: Jan 20 (1 test run)
  Last activity: Jan 25, 2026 — nothing since
```

**Gap**: The cron entry for upgrade-discover was apparently removed or never persisted. Only 4 total executions across all headless jobs ever.

#### Plex Troubleshooter
```
.claude/agents/plex-troubleshoot.md      # 509-line agent prompt (very detailed)
.claude/scripts/plex-troubleshoot.sh     # Wrapper: loads prompt, injects safety mode
knowledge/n8n-workflows/agents/infra--plex-troubleshoot/  # n8n workflow docs
```

**Gap**: This is the most mature headless pattern. Has safety modes (readonly/safe-fixes/full), detailed forbidden commands, memory system. But uses `--dangerously-skip-permissions` instead of `--allowedTools`. Not connected to Beads.

#### Fresh Context Loop
```
Scripts/fresh-context-loop.sh            # Full implementation (534 lines)
.claude/context/patterns/fresh-context-pattern.md  # Pattern documentation
.claude/commands/fresh-context.md        # Command docs
```

**Gap**: Exists but separate from the job system. Could become a Phase 4 execution mode.

---

### Gap Summary Table

| Component | Design Spec | Current State | Gap |
|-----------|-------------|---------------|-----|
| **Dispatcher** | `dispatcher.sh` — single cron, scans registry | Nothing | Build from scratch |
| **Executor** | `executor.sh` — persona-aware wrapper | `claude-scheduled.sh` — hardcoded jobs | Refactor into persona system |
| **Registry** | `registry.yaml` — all jobs + schedules | Jobs hardcoded in bash script | Create new |
| **Personas** | Folder-per-persona (prompt + perms + config) | Plex has safety modes; others have tiers | Extract into folder structure |
| **Queue** | `queue.json` — async questions | Nothing | Build from scratch |
| **Beads integration** | Per-persona bd access | No headless Beads interaction | Add to persona permissions |
| **n8n approval** | Queue watcher + Telegram | Plex webhook exists in n8n | Extend existing |
| **Cron** | Single dispatcher entry | 2 unrelated entries; documented entries missing | Replace with one entry |
| **Logging** | Unified under `.claude/logs/headless/` | Scattered across multiple dirs | Consolidate |
| **Doc updates** | 13 files identified | All reference old system | Update during implementation |

---

## Implementation Plan

### Phase 1: Foundation

**Goal**: Working dispatcher + personas + 3 jobs running via single cron entry.
**Estimated effort**: One focused session (3-5 hours).

---

#### Task 1.1: Create Persona Folder Structure

Create the base directories and template:

```
.claude/jobs/personas/
  _template/
    prompt.md
    permissions.yaml
    config.yaml
  investigator/
    prompt.md
    permissions.yaml
    config.yaml
  analyst/
    prompt.md
    permissions.yaml
    config.yaml
  troubleshooter/
    prompt.md
    permissions.yaml
    config.yaml
```

**Investigator** — extract from current `TIER_DISCOVERY` in claude-scheduled.sh:
- prompt.md: "You are running in headless investigator mode. Observe, analyze, report. Never modify."
- permissions.yaml: Map current `TIER_DISCOVERY` tools list
- config.yaml: max_turns: 5, max_budget: 1.00, model: sonnet

**Analyst** — extract from current `TIER_ANALYZE`:
- prompt.md: "You are running in headless analyst mode. Research, discover, write findings to data files."
- permissions.yaml: Map `TIER_ANALYZE` + Beads create
- config.yaml: max_turns: 15, max_budget: 3.00, model: sonnet

**Troubleshooter** — extract from plex-troubleshoot.md agent prompt:
- prompt.md: Adapted from the 509-line agent prompt (keep the workflow phases, safety modes, forbidden commands)
- permissions.yaml: Custom toolset + SSH + Beads full access
- config.yaml: max_turns: 20, max_budget: 5.00, model: sonnet

**Done criteria**: Folders exist, `yq` or `cat` can read the YAML files, prompt.md is well-formed.

---

#### Task 1.2: Create Registry YAML

Create `.claude/jobs/registry.yaml`:

```yaml
version: 1
defaults:
  engine: claude-code
  model: sonnet
  max_turns: 10
  max_budget_usd: 2.00
  timeout_minutes: 10
  session_persist: false

jobs:
  health-summary:
    description: "Quick infrastructure health check"
    persona: investigator
    schedule:
      type: interval
      every_hours: 6
    enabled: true
    max_turns: 5
    max_budget_usd: 1.00
    prompt: |
      Check infrastructure health: Use Docker MCP tools to review container
      status. Check for failed or unhealthy services. Verify critical services
      are running (n8n, grafana, prometheus, caddy). Output a brief health
      summary with status for each service.

  upgrade-discover:
    description: "Check for Claude Code and MCP updates"
    persona: analyst
    schedule:
      type: weekly
      day: sunday
      hour: 6
    enabled: true
    max_turns: 15
    max_budget_usd: 3.00
    prompt: |
      Run the upgrade discovery workflow: Check external sources (GitHub releases
      at https://github.com/anthropics/claude-code/releases, documentation at
      https://docs.anthropic.com/en/docs/claude-code, Anthropic blog) for Claude
      Code and MCP updates. Compare findings against the baselines in
      .claude/skills/upgrade/data/baselines.json. Store any new discoveries in
      .claude/skills/upgrade/data/pending-upgrades.json. If you find new updates,
      create a Beads task: bd create "Upgrade: [what]" -t task -p 2 -l
      "domain:infrastructure,project:aiprojects,severity:medium,source:headless".
      Generate a discovery report.

  plex-troubleshoot:
    description: "Diagnose and fix Plex issues"
    persona: troubleshooter
    schedule:
      type: on-demand
    enabled: true
    max_turns: 20
    max_budget_usd: 5.00
    trigger:
      webhook: true
      parameters:
        - name: issue
          default: "full diagnostic"
        - name: safety_mode
          default: "readonly"

  doc-sync-check:
    description: "Check if docs need sync with code"
    persona: investigator
    schedule:
      type: interval
      every_hours: 24
    enabled: true
    max_turns: 5
    max_budget_usd: 1.00
    prompt: |
      Check if documentation needs synchronization. Read
      .claude/logs/doc-sync-tracker.json if it exists to see recent code changes.
      If significant changes have accumulated (5+ changes), report which
      documentation files may need updating. Do not modify any files.

  priority-review:
    description: "Review priorities and flag stale items"
    persona: investigator
    schedule:
      type: weekly
      day: monday
      hour: 7
    enabled: true
    max_turns: 5
    max_budget_usd: 1.00
    prompt: |
      Review current task state. Run bd list --status open to see all open tasks.
      Run bd list --status in_progress to check active work. Read
      .claude/context/session-state.md for current status. Identify tasks that
      look stale (in_progress for multiple days with no commits). Output
      recommendations only.
```

**Done criteria**: Valid YAML, parseable by `yq`, all 5 jobs defined with persona references.

---

#### Task 1.3: Build executor.sh

Replace `claude-scheduled.sh` with persona-aware executor. Core logic:

```bash
#!/bin/bash
# executor.sh - Persona-aware headless Claude execution
# Usage: executor.sh --job <job-name> [--param key=value] [--engine override]

# 1. Read registry.yaml to get job config
# 2. Load persona: read prompt.md, permissions.yaml, config.yaml
# 3. Build --allowedTools from permissions.yaml
# 4. Check queue.json for pending answers for this job
# 5. Compose full prompt: persona prompt + job prompt + queue context
# 6. Set BEADS_ACTOR="headless-${JOB_NAME}-$(date +%Y%m%d)"
# 7. Execute: claude -p "$PROMPT" --allowedTools "$TOOLS" --max-turns N --output-format json
# 8. Parse output for question indicators → write to queue.json if found
# 9. Log execution to .claude/logs/headless/
# 10. Exit
```

**Key differences from claude-scheduled.sh**:
- Reads persona files instead of hardcoded tiers
- Sets BEADS_ACTOR for audit trail
- Checks/writes to question queue
- Logs to `.claude/logs/headless/` (new unified location)
- Accepts `--param` for webhook parameters (plex issue, safety_mode)

**Migration**: Keep `claude-scheduled.sh` working. `executor.sh` is additive. Once validated, the dispatcher calls executor.sh. Old script remains as fallback.

**Done criteria**: Can run `executor.sh --job health-summary` and get valid JSON output.

---

#### Task 1.4: Build dispatcher.sh

The master scheduler. Pure bash, no LLM.

```bash
#!/bin/bash
# dispatcher.sh - Master headless scheduler
# Runs every 5 minutes via single cron entry

# 1. Read registry.yaml
# 2. Read .claude/jobs/state/last-run.json for timestamps
# 3. For each enabled job:
#    a. Parse schedule (interval, weekly, cron)
#    b. Compare with last_run + interval
#    c. If due: check lock file, acquire lock, run executor.sh, release lock
# 4. Check queue.json for answered questions → re-trigger waiting jobs
# 5. Update last-run.json
# 6. Log dispatcher activity
```

**Schedule parsing** (keep it simple):
- `type: interval, every_hours: 6` → last_run + 6h < now
- `type: weekly, day: sunday, hour: 6` → is it Sunday and past 6 AM and not run this week?
- `type: on-demand` → skip (only triggered via direct call or webhook)

**Locking**: Write PID to `.claude/jobs/state/locks/<job>.lock`. Check if PID is still running before acquiring. Prevents parallel runs of same job.

**Done criteria**: Can run `dispatcher.sh` manually, it correctly identifies which jobs are due, and runs them.

---

#### Task 1.5: Set Up Cron + State Files

Create state directory and single cron entry:

```bash
# Create state infrastructure
mkdir -p .claude/jobs/state/locks
mkdir -p .claude/logs/headless/executions
echo '{}' > .claude/jobs/state/last-run.json
echo '{"version":1,"questions":[]}' > .claude/jobs/queue.json

# Add single cron entry (replaces all existing headless entries)
# */5 * * * * /home/davidmoneil/AIProjects/.claude/jobs/dispatcher.sh >> /home/davidmoneil/AIProjects/.claude/logs/headless/dispatcher.log 2>&1
```

**Done criteria**: Dispatcher runs on schedule. `tail -f .claude/logs/headless/dispatcher.log` shows it checking jobs.

---

#### Task 1.6: Migrate Existing Jobs

Map existing code to new structure:

| Old | New | Action |
|-----|-----|--------|
| claude-scheduled.sh `upgrade-discover` job definition | registry.yaml `upgrade-discover` entry + analyst persona | Extract prompt, map TIER_ANALYZE to permissions.yaml |
| claude-scheduled.sh `health-summary` job definition | registry.yaml `health-summary` entry + investigator persona | Extract prompt, map TIER_DISCOVERY to permissions.yaml |
| claude-scheduled.sh `priority-review` | registry.yaml `priority-review` + investigator persona | Extract, add Beads query to prompt |
| claude-scheduled.sh `doc-sync-check` | registry.yaml `doc-sync-check` + investigator persona | Direct mapping |
| plex-troubleshoot.sh + agent prompt | registry.yaml `plex-troubleshoot` + troubleshooter persona | Extract 509-line prompt into troubleshooter/prompt.md. Map safety modes to permissions.yaml. Remove `--dangerously-skip-permissions`. |

**Done criteria**: All 5 jobs run successfully through `executor.sh`. Output matches or improves on old system.

---

#### Task 1.7: Validate End-to-End

Test sequence:
1. `executor.sh --job health-summary` → valid JSON output, investigator persona loaded
2. `executor.sh --job upgrade-discover` → writes to pending-upgrades.json, creates Beads task if finds update
3. `executor.sh --job plex-troubleshoot --param issue="test" --param safety_mode=readonly` → connects to MediaServer, runs diagnostics
4. `dispatcher.sh` → correctly identifies due jobs, runs them
5. Wait for cron cycle → dispatcher runs automatically
6. Check `.claude/logs/headless/` → execution logs present
7. Check `bd list --label source:headless` → any tasks created by headless show up

---

### Phase 2: Question Queue + Approvals

**Goal**: Plex troubleshooter can ask for reboot approval via Telegram.
**Estimated effort**: One focused session (3-4 hours).
**Prerequisite**: Phase 1 complete and validated.

---

#### Task 2.1: Implement Queue Management Functions

Add to executor.sh (or separate `queue-manager.sh`):

```bash
# Write a question to the queue
write_question() {
  local job="$1" question="$2" options="$3" priority="${4:-medium}" default_after="${5:-30m}"
  local id="q-$(date +%Y%m%d-%H%M%S)-${job}"
  # Use jq to append to queue.json
  jq --arg id "$id" --arg job "$job" --arg q "$question" --arg opts "$options" \
     --arg pri "$priority" --arg da "$default_after" \
     '.questions += [{
       id: $id, created_at: (now | todate), job: $job,
       status: "pending", priority: $pri, question: $q,
       options: ($opts | split("|")), default_after: $da,
       answer: null, answered_at: null
     }]' .claude/jobs/queue.json > /tmp/queue.tmp && mv /tmp/queue.tmp .claude/jobs/queue.json
}

# Read answered questions for a job
read_answers() {
  local job="$1"
  jq --arg job "$job" '[.questions[] | select(.job == $job and .status == "answered")]' .claude/jobs/queue.json
}

# Expire old questions (apply default action)
expire_questions() {
  # Check each pending question's created_at + default_after against now
  # If expired: set status to "expired", apply default_action
}
```

**Done criteria**: Can write/read/expire questions. JSON stays valid after operations.

---

#### Task 2.2: Add Question Detection to Executor

After Claude runs, scan output for question patterns:

```bash
# After claude -p execution, check for approval requests
if echo "$RESULT" | jq -r '.result' | grep -qi "APPROVAL_NEEDED\|QUESTION:"; then
  # Extract question text
  QUESTION=$(echo "$RESULT" | jq -r '.result' | grep -oP 'QUESTION: \K.*')
  write_question "$JOB_NAME" "$QUESTION" "Approve|Deny|Skip" "high"
  log_info "Question written to queue: $QUESTION"
fi
```

Also update persona prompts to include queue instructions:

```markdown
## Asking for Human Input

If you encounter a situation requiring human approval (reboot, delete, config change):

1. Clearly state: "QUESTION: [your question here]"
2. Provide context for the human
3. List the options: "OPTIONS: Approve|Deny|Skip"
4. Then exit cleanly — do NOT wait or retry

The system will deliver your question and resume you with the answer.
```

**Done criteria**: When plex-troubleshoot determines a reboot is needed, it outputs the structured question format. Executor detects it and writes to queue.

---

#### Task 2.3: Add Queue Checking to Dispatcher

In dispatcher.sh, before running scheduled jobs:

```bash
# Check for answered questions
ANSWERS=$(jq '[.questions[] | select(.status == "answered")]' .claude/jobs/queue.json)
if [ "$(echo "$ANSWERS" | jq length)" -gt 0 ]; then
  # For each answered question, re-run the job with the answer context
  echo "$ANSWERS" | jq -c '.[]' | while read -r answer; do
    JOB=$(echo "$answer" | jq -r '.job')
    ANSWER_TEXT=$(echo "$answer" | jq -r '.answer')
    log_info "Re-running $JOB with answer: $ANSWER_TEXT"
    executor.sh --job "$JOB" --answer "$ANSWER_TEXT"
    # Mark question as processed
    # ...
  done
fi
```

**Done criteria**: When an answer appears in queue.json, dispatcher re-triggers the job.

---

#### Task 2.4: Build n8n Queue Watcher Workflow

Create n8n workflow:
1. **Schedule Trigger**: Every 2 minutes (or file watcher if available)
2. **Read File**: Read `.claude/jobs/queue.json`
3. **Filter**: Find questions with `status: "pending"`
4. **Telegram**: Send message with question text + inline keyboard buttons
5. **Wait for Reply**: Telegram callback or n8n Wait node
6. **Write Answer**: Update queue.json with answer + answered_at + answered_by

Alternative (simpler first pass):
1. Schedule Trigger → Read queue.json → Filter pending
2. Send email/Telegram with question
3. Separate webhook: `POST /webhook/headless-answer` with `{id, answer}`
4. Webhook workflow updates queue.json

**Done criteria**: New pending question → Telegram notification arrives within 2 minutes. Replying writes answer to queue.json.

---

#### Task 2.5: Set Up Telegram Bot

```bash
# Via n8n Telegram node:
# 1. Create bot via @BotFather
# 2. Get bot token
# 3. Add Telegram credential in n8n
# 4. Configure chat ID for your account
```

**Done criteria**: n8n can send you a Telegram message and receive your reply.

---

#### Task 2.6: End-to-End Approval Test

Full flow test:
1. Run `executor.sh --job plex-troubleshoot --param issue="test reboot" --param safety_mode=safe-fixes`
2. Troubleshooter determines reboot is needed → outputs QUESTION
3. Executor writes to queue.json
4. n8n detects question → sends Telegram message
5. You reply "Approve" in Telegram
6. n8n writes answer to queue.json
7. Next dispatcher cycle detects answer → re-runs plex-troubleshoot with answer context
8. Troubleshooter reads "Approve" → executes reboot command

**Done criteria**: Full cycle completes without manual intervention (except the Telegram reply).

---

### Phase 3: Engine Routing + Observability

**Prerequisite**: Phase 2 complete.
**Not detailed here** — design spec covers the scope. Key tasks:
- Add `engine` field handling to executor.sh (ollama curl path)
- Route health-summary to Ollama for cost savings
- Build observability dashboard (n8n workflow or simple HTML)
- Add Grafana/Prometheus metrics export

---

## AIProjects Files to Update (During Phase 1)

These updates ensure the rest of the system knows about Headless Claude:

### CLAUDE.md (~line 252, Automation Routing section)

Add after the existing decision tree:

```markdown
### Headless Claude Framework

For AI-powered scheduled/automated tasks, use the Headless Claude system:

| Component | Location | Purpose |
|-----------|----------|---------|
| Dispatcher | `.claude/jobs/dispatcher.sh` | Master scheduler (single cron entry) |
| Executor | `.claude/jobs/executor.sh` | Persona-aware execution wrapper |
| Registry | `.claude/jobs/registry.yaml` | Job definitions + schedules |
| Personas | `.claude/jobs/personas/<name>/` | Permission profiles (prompt + perms + config) |
| Queue | `.claude/jobs/queue.json` | Async human-in-the-loop questions |
| Logs | `.claude/logs/headless/` | Execution history |

**Adding a new headless job**:
1. Choose or create a persona in `.claude/jobs/personas/`
2. Add job entry to `.claude/jobs/registry.yaml`
3. Test: `executor.sh --job <name>`
4. The dispatcher picks it up automatically on next cycle

**Design**: See Obsidian `05-AI/Projects/Headless-Claude/` for full design spec.
```

### compaction-essentials.md (~line 50, Scheduled Jobs section)

Replace current section with:

```markdown
## Headless Claude

Automated Claude Code jobs run via `.claude/jobs/dispatcher.sh` (single cron entry).
- **Personas**: investigator (read-only), analyst (read+write), troubleshooter (safe fixes)
- **Registry**: `.claude/jobs/registry.yaml` (all jobs + schedules)
- **Queue**: `.claude/jobs/queue.json` (async approval via n8n/Telegram)
- **Beads integration**: Headless jobs use `source:headless` label
- **Design**: Obsidian `05-AI/Projects/Headless-Claude/`

Quick commands:
- `executor.sh --job health-summary` — run a job manually
- `bd list --label source:headless` — see headless-created tasks
```

### autonomous-execution-pattern.md (top of file)

Add deprecation notice:

```markdown
> **Note (2026-02-08)**: This pattern has been superseded by the **Headless Claude** framework.
> The permission tiers and CLI reference below are still valid and used by the new system.
> For the full framework (dispatcher, personas, queue, Beads integration), see:
> - Design: Obsidian `05-AI/Projects/Headless-Claude/Headless Claude - Design Specification.md`
> - Implementation: `.claude/jobs/` (dispatcher.sh, executor.sh, registry.yaml, personas/)
```

### jobs/README.md

Rewrite the "Claude Autonomous Execution Jobs" section to reference the new system. Keep existing daily-sync and cleanup-agent-sessions documentation as-is (those are pure bash jobs, not headless Claude).

### patterns/_index.md

Add entry:
```markdown
- **Headless Claude**: Automated Claude Code execution with personas, scheduling, approval queue
  - Design: Obsidian `05-AI/Projects/Headless-Claude/`
  - Components: `.claude/jobs/` (dispatcher, executor, registry, personas)
  - Extends: autonomous-execution-pattern.md (permission tiers)
```

### context/_index.md

Add under Systems/Integrations:
```markdown
- @.claude/jobs/registry.yaml - **Headless Claude** job registry and scheduling
```

---

## Migration Safety

### What We Keep Running
- `claude-scheduled.sh` — untouched, still works for manual execution
- `plex-troubleshoot.sh` — untouched, still works from n8n
- `fresh-context-loop.sh` — untouched, Phase 4 integration
- `daily-sync.sh`, `cleanup-agent-sessions.sh` — pure bash, no change needed

### What We Add
- `dispatcher.sh` — new, single cron entry
- `executor.sh` — new, persona-aware wrapper
- `registry.yaml` — new, job definitions
- `personas/` — new, permission profiles
- `queue.json` — new, question queue
- `state/` — new, last-run tracking and locks

### Rollback Plan
If anything breaks:
1. Remove the dispatcher cron entry (`crontab -e`)
2. All old scripts still work independently
3. No existing files are modified during Phase 1 (except documentation)

---

## Validation Checklist

### Phase 1 Complete When:

- [ ] `executor.sh --job health-summary` produces valid JSON output
- [ ] `executor.sh --job upgrade-discover` runs and logs to `.claude/logs/headless/`
- [ ] `executor.sh --job plex-troubleshoot --param issue=test --param safety_mode=readonly` connects to MediaServer
- [ ] `dispatcher.sh` correctly identifies due jobs from registry.yaml
- [ ] Single cron entry runs dispatcher every 5 minutes
- [ ] `bd list --label source:headless` returns results after analyst job creates a task
- [ ] CLAUDE.md, compaction-essentials.md, and jobs/README.md updated
- [ ] All 3 persona folders have valid prompt.md, permissions.yaml, config.yaml

### Phase 2 Complete When:

- [ ] Plex troubleshooter writes question to queue.json when reboot needed
- [ ] n8n detects queue question within 2 minutes
- [ ] Telegram notification arrives with question and options
- [ ] Replying in Telegram writes answer to queue.json
- [ ] Next dispatcher cycle re-triggers job with answer
- [ ] Full approval flow works end-to-end without manual file editing

---

## File Reference

All files created or modified, organized by implementation order:

### New Files (Phase 1)
```
.claude/jobs/
  dispatcher.sh                          # Master scheduler
  executor.sh                            # Persona-aware wrapper
  registry.yaml                          # Job definitions
  queue.json                             # Question queue (starts empty)
  state/
    last-run.json                        # Execution timestamps
    locks/                               # PID lock files
  personas/
    _template/prompt.md                  # Template persona
    _template/permissions.yaml
    _template/config.yaml
    investigator/prompt.md               # Read-only observer
    investigator/permissions.yaml
    investigator/config.yaml
    analyst/prompt.md                    # Research + write reports
    analyst/permissions.yaml
    analyst/config.yaml
    troubleshooter/prompt.md             # Diagnose + safe fixes
    troubleshooter/permissions.yaml
    troubleshooter/config.yaml

.claude/logs/headless/                   # New unified log directory
  executions/                            # Per-job execution logs
  queue-history/                         # Archived answered questions
```

### Modified Files (Phase 1)
```
.claude/CLAUDE.md                                    # Add Headless Claude section
.claude/context/compaction-essentials.md              # Update Scheduled Jobs section
.claude/context/patterns/autonomous-execution-pattern.md  # Add superseded notice
.claude/jobs/README.md                               # Rewrite autonomous section
.claude/context/patterns/_index.md                   # Add Headless Claude entry
.claude/context/_index.md                            # Add reference
```

### Untouched Files (kept for backward compatibility)
```
.claude/jobs/claude-scheduled.sh         # Still works independently
.claude/scripts/plex-troubleshoot.sh     # Still works from n8n
Scripts/fresh-context-loop.sh            # Phase 4 integration
.claude/jobs/daily-sync.sh              # Pure bash, no change
.claude/jobs/cleanup-agent-sessions.sh  # Pure bash, no change
```

---

## Quick Start (For Implementation Session)

When ready to build, run this in order:

```bash
# 1. Create directory structure
mkdir -p .claude/jobs/personas/{_template,investigator,analyst,troubleshooter}
mkdir -p .claude/jobs/state/locks
mkdir -p .claude/logs/headless/executions
mkdir -p .claude/logs/headless/queue-history

# 2. Initialize state files
echo '{}' > .claude/jobs/state/last-run.json
echo '{"version":1,"questions":[]}' > .claude/jobs/queue.json

# 3. Build persona files (Claude writes these)
# 4. Build registry.yaml (Claude writes this)
# 5. Build executor.sh (Claude writes this)
# 6. Build dispatcher.sh (Claude writes this)
# 7. Test each job manually
# 8. Add cron entry
# 9. Update documentation
# 10. Validate checklist
```

Tell Claude: "Let's implement Phase 1 of the Headless Claude system. The design spec and implementation guide are in Obsidian at 05-AI/Projects/Headless-Claude/. Start with Task 1.1."
