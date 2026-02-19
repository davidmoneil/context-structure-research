# Headless Claude: Reporting & Notification System

## Context

The Headless Claude system (Phase 1 complete) runs jobs autonomously via cron — but has no way to tell David what happened. There's no centralized view of "what ran, when, and what it found." Without reporting, headless jobs are a black box.

**Goal**: Build a 4-layer reporting system so David always knows what Headless Claude has done, with Telegram as the push notification channel and n8n as the notification relay.

**Approach**: Bottom-up — bash first (JSONL records + CLI), then n8n webhook (Telegram push), then daily digest, then approval flow.

---

## Phase 1: Notification Records + CLI History

**What**: Every job execution writes a structured notification record to JSONL. Add `--history` command to dispatcher.

### New Files

- **`.claude/jobs/notifications.jsonl`** — Append-only notification log

Record format:
```json
{
  "id": "health-summary-1707400800",
  "timestamp": "2026-02-08T18:00:00Z",
  "job": "health-summary",
  "severity": "info",
  "title": "Health check completed",
  "summary": "All 5 services healthy",
  "exit_code": 0,
  "cost_usd": "0.12",
  "duration_secs": 45,
  "output_file": "/path/to/execution.json",
  "notified": false,
  "acknowledged": false
}
```

### Modifications

- **`executor.sh`** (~lines 393-432) — After saving output, write notification record:
  - Determine severity from output: `critical` (CRITICAL/URGENT/SECURITY patterns or exit_code != 0), `warning` (WARN or QUESTION:), `info` (normal success)
  - Extract summary from Claude's response (first sentence or 100 chars)
  - Append JSON line to `notifications.jsonl`
  - New function: `write_notification()` — takes job, severity, title, summary, exit_code, cost, duration

- **`dispatcher.sh`** (~line 522) — Add `--history` command:
  - `--history` — Show last 20 notifications (default)
  - `--history N` — Show last N notifications
  - `--history --job <name>` — Filter by job
  - `--history --severity critical` — Filter by severity
  - `--history --unack` — Show unacknowledged only
  - `--ack <id>` — Mark notification as acknowledged
  - Colorized output: red for critical, yellow for warning, green for info

### Validation
```bash
# Manually run a job, verify notification.jsonl gets a record
dispatcher.sh --run health-summary
cat .claude/jobs/notifications.jsonl | jq .
dispatcher.sh --history
dispatcher.sh --history --severity critical
```

---

## Phase 2: Telegram Push via n8n

**What**: After writing the notification record, executor.sh POSTs to an n8n webhook. n8n formats and sends to Telegram. Includes deduplication to avoid spam.

### New Files

- **`.claude/jobs/lib/send-notification.sh`** — Notification dispatch library:
  - `send_notification()` — Writes JSONL record (from Phase 1) + POSTs to n8n webhook
  - `should_notify()` — Dedup logic:
    - `critical`: Always send immediately
    - `warning`: Max once per 6 hours per job (check notifications.jsonl for recent same-job warnings)
    - `info`: Never push — digest only
  - Uses `curl` to POST to n8n webhook URL
  - Webhook URL from env var `HEADLESS_NOTIFY_WEBHOOK` (set in cron environment or `.claude/jobs/.env`)

- **`.claude/jobs/.env`** — Environment config (git-ignored):
  ```
  HEADLESS_NOTIFY_WEBHOOK=http://localhost:5678/webhook/headless-notify
  HEADLESS_TELEGRAM_CHAT_ID=<david's chat id>
  ```

### n8n Workflow: "Headless Claude Notify"

Create via n8n UI (document the webhook URL):
1. **Webhook trigger** — Receives POST from executor
2. **Switch node** — Route by severity (critical/warning/info)
3. **Telegram node** — Send message to David's chat:
   - Critical: Bold title, full summary, link to output
   - Warning: Summary with job name
   - Info: Skip (digest only)
4. **Respond to webhook** — Return `{"ok": true}`

Telegram message format:
```
🔴 CRITICAL: health-summary
All services DOWN on AIServer

Cost: $0.12 | Duration: 45s
Output: /path/to/execution.json
```

### Modifications

- **`executor.sh`** — Replace inline notification logic with `source lib/send-notification.sh` and call `send_notification()`
- **`dispatcher.sh`** — Source `.env` if exists, pass webhook URL to executor via env

### Prerequisites (Manual Steps)
1. Create Telegram bot via @BotFather, save token
2. Get David's chat ID (send message to bot, check `/getUpdates`)
3. Add Telegram credentials in n8n (Settings > Credentials)
4. Create the n8n webhook workflow
5. Save webhook URL to `.claude/jobs/.env`

### Validation
```bash
# Test webhook manually
curl -X POST http://localhost:5678/webhook/headless-notify \
  -H "Content-Type: application/json" \
  -d '{"job":"test","severity":"warning","title":"Test notification","summary":"This is a test"}'

# Run a job and verify Telegram message arrives
dispatcher.sh --run health-summary
# Check Telegram for message
```

---

## Phase 3: Daily Digest

**What**: n8n workflow runs daily at 8 AM, reads notifications.jsonl, summarizes last 24 hours, sends digest to Telegram.

### n8n Workflow: "Headless Claude Daily Digest"

1. **Cron trigger** — 8:00 AM daily
2. **Execute Command node** — Read last 24h from notifications.jsonl:
   ```bash
   jq -s '[.[] | select(.timestamp > (now - 86400 | todate))]' \
     /home/davidmoneil/AIProjects/.claude/jobs/notifications.jsonl
   ```
3. **Code node** — Format digest:
   - Group by severity, count by job
   - Include total cost for the period
   - List any unacknowledged critical/warning items
4. **IF node** — Skip if no notifications in period
5. **Telegram node** — Send digest message

Digest format:
```
📊 Headless Claude Daily Digest
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Jobs Run: 4 | Total Cost: $0.48
🔴 Critical: 0 | 🟡 Warning: 1 | 🟢 Info: 3

📋 Details:
  ✅ health-summary (x4) — All healthy
  ⚠️ upgrade-discover — 2 new updates found

💬 Pending Questions: 1
  → plex-troubleshoot: "Restart Plex service?"
```

### Validation
```bash
# Trigger the n8n workflow manually via n8n UI
# Verify Telegram receives formatted digest
# Verify empty days produce no message
```

---

## Phase 4: Telegram Approval Flow (Queue Integration)

**What**: When a headless job asks a QUESTION:, send it to Telegram with inline keyboard buttons (Approve/Deny/Skip). David taps a button, n8n writes the answer to queue.json, next dispatcher cycle picks it up.

### n8n Workflow: "Headless Claude Approvals"

1. **Triggered by Phase 2 notify workflow** — When severity contains a question
2. **Telegram node** — Send message with inline keyboard:
   ```
   🔔 Approval Required: plex-troubleshoot

   "Should I restart the Plex service? It appears hung."

   [✅ Approve] [❌ Deny] [⏭ Skip]
   ```
3. **Telegram Trigger node** — Listen for callback button press
4. **Execute Command node** — Write answer to queue.json:
   ```bash
   jq '.questions += [{"job":"plex-troubleshoot","question":"...","answer":"approve","status":"answered","answered_at":"2026-02-08T18:30:00Z","answered_by":"telegram"}]' \
     /home/davidmoneil/AIProjects/.claude/jobs/queue.json > tmp && mv tmp queue.json
   ```
5. **Telegram node** — Confirm: "Approved. Will execute on next cycle."

### Modifications

- **`executor.sh`** — When writing QUESTION to queue, also trigger notification with `severity: question`
- **`lib/send-notification.sh`** — Add `question` severity type that always sends

### Validation
```bash
# Simulate a question from a job
# Verify Telegram shows inline buttons
# Tap Approve, verify queue.json updated
# Run dispatcher, verify it picks up the answer
dispatcher.sh --check  # Should show "Queue answers waiting"
```

---

## Implementation Order

| # | Phase | Effort | Dependencies |
|---|-------|--------|--------------|
| 1 | Notification JSONL + --history CLI | ~1 hour | None |
| 2 | Telegram push via n8n | ~1 hour | Phase 1 + Telegram bot setup (manual) |
| 3 | Daily digest | ~30 min | Phase 2 (n8n + Telegram working) |
| 4 | Approval flow | ~1 hour | Phase 2 + Phase 3 |

**Total estimate**: ~3.5 hours of implementation across 1-2 sessions

## Files Summary

### New Files
| File | Purpose |
|------|---------|
| `.claude/jobs/notifications.jsonl` | Append-only notification records |
| `.claude/jobs/lib/send-notification.sh` | Notification dispatch + dedup library |
| `.claude/jobs/.env` | Webhook URL + Telegram chat ID (git-ignored) |

### Modified Files
| File | Changes |
|------|---------|
| `.claude/jobs/executor.sh` | Write notification records, source lib, call send_notification() |
| `.claude/jobs/dispatcher.sh` | Add --history/--ack commands, source .env |
| `.claude/jobs/.gitignore` | Add .env |

### n8n Workflows (created via UI)
| Workflow | Trigger |
|----------|---------|
| Headless Claude Notify | Webhook (POST from executor) |
| Headless Claude Daily Digest | Cron (8 AM daily) |
| Headless Claude Approvals | Telegram callback query |

## Verification (End-to-End)

1. Run `dispatcher.sh --run health-summary` with a test job
2. Verify `notifications.jsonl` has a record
3. Verify `dispatcher.sh --history` shows the record with color
4. Verify Telegram receives push notification (if critical/warning)
5. Verify daily digest arrives at 8 AM with correct summary
6. Simulate a QUESTION job, verify Telegram inline buttons work
7. Tap Approve, verify queue.json updated and next dispatcher cycle processes it
