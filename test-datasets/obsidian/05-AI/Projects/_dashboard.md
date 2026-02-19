---
tags:
  - project/teenagers
  - status/draft
  - domain/ai
  - domain/dnd
  - depth/quick
created: 2026-01-02T15:34
updated: 2026-01-24T10:34
---
# AI Sessions Dashboard

Aggregated view of session artifacts.

---

## Active Todos

```tasks
not done
path includes AI-Sessions
sort by priority
sort by due
```

---

## Open Questions

```dataview
LIST
FROM "AI-Sessions"
WHERE type = "question" AND status = "open"
SORT file.ctime DESC
```

---

## Recent Decisions

```dataview
TABLE file.cday as "Date", file.link as "Decision"
FROM "AI-Sessions"
WHERE type = "decision"
SORT file.cday DESC
LIMIT 10
```

---

## Session Timeline

```dataview
TABLE file.cday as "Date", topic, status
FROM "AI-Sessions"
WHERE type = "session"
SORT file.cday DESC
LIMIT 15
```

---

## All Incomplete Tasks (Vault-wide)

```tasks
not done
group by filename
limit 50
```

---

## Task Status Reference

| Checkbox | Status | Meaning |
|----------|--------|---------|
| `[ ]` | Todo | Not started |
| `[/]` | In Progress | Currently working on |
| `[x]` | Done | Completed |
| `[-]` | Cancelled | Won't do |
| `[!]` | Important | High priority |
| `[?]` | Question | Needs clarification |

---

## Quick Add Task

To add a task anywhere in Obsidian:
```markdown
- [ ] Task description #ai-session 📅 2026-01-15
- [!] Important task #ai-session
- [ ] Task with priority 🔺 #ai-session
```

**Tags**: Use `#ai-session` to include in AI-Sessions queries
**Due dates**: 📅 YYYY-MM-DD (type `due` and autocomplete)
**Priority**: 🔺 high, 🔼 medium, 🔽 low
