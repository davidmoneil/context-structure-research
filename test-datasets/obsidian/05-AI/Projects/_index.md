---
tags:
  - artifact/session
  - domain/ai
  - domain/dnd
  - depth/quick
  - depth/standard
created: 2026-01-02T21:20
updated: 2026-01-24T10:34
---
# AI Sessions

Central workspace for Claude Code session collaboration.

**Purpose**: Rich feedback, decision recording, and session documentation

---

## Quick Links

- [[_inbox]] - **Response inbox** (write your responses here)
- [[_dashboard]] - Aggregated view of todos, decisions, open questions

---

## How This Works

1. **Claude creates artifacts** in session folders (questions, decisions, todos)
2. **You respond** in `_inbox.md` with rich formatting (tables, lists, etc.)
3. **You tell Claude** "I've responded" to continue the conversation
4. **Artifacts persist** as searchable, navigable knowledge

---

## Folder Structure

```
AI-Sessions/
├── _index.md          # This file
├── _inbox.md          # Your response location
├── _dashboard.md      # Aggregated view
├── _templates/        # File templates
└── YYYY/MM/DD-topic/  # Session folders
    ├── session-notes.md
    ├── questions/
    ├── decisions/
    └── todos.md
```

---

## Recent Sessions

- [[2026/01/02-ai-infrastructure-research/session-notes|2026-01-02: AI Infrastructure Research]] - Compared 10 GitHub projects, created improvement roadmap

---

## Related

- [[AI Infrastructure]] - Technical documentation
- Pattern docs in AIProjects: `.claude/context/patterns/obsidian-collaboration-pattern.md`
