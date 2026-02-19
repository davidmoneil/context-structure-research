---
title: "Social Media Copy: Document Guard Launch"
date: 2026-02-10
article: "How-I-Made-Claude-Code-Safer-And-You-Can-Too"
status: draft
version: 3
version_history:
  - v1: "2026-02-10 - Initial social media copy (Twitter, LinkedIn, Reddit, HN)"
  - v2: "2026-02-10 - Reddit rewrite: crash story opening, v2 feedback framing, voice alignment"
  - v3: "2026-02-10 - LinkedIn updated to final published version"
tags:
  - social-media
  - ciso-expert
  - document-guard
---

# Social Media Copy: Document Guard Launch

## Twitter/X (Thread)

**Rules: No links in Tweet 1 (algorithm buries them). 280 chars per tweet. Links = 23 chars always.**

### Tweet 1 (Hook — No Link) ~230 chars

Stop Claude Code horror stories from happening to you.

Exposed AWS keys. Rewrote your CLAUDE.md. "Cleaned up" and deleted everything.

Document Guard.
- One install
- Zero config
A Claude Code plugin with logging that protects your files out of the box.

### Tweet 2 (What It Catches + Screenshot) ~270 chars

What it blocks immediately:

- .env and credential files — total write block
- 13 credential patterns (AWS, GitHub, Stripe, JWTs)
- Section/heading deletion in markdown
- YAML key removal during config rewrites
- Shebang lines stripped from scripts

[Attach: claude-md-override.png]

### Tweet 3 (The Surprise — The Quotable One) ~250 chars

Here's what I didn't expect.

When Document Guard blocks a bad edit, it tells Claude WHY — injects the reason right into the conversation.

Claude reads it. Adjusts. Stops making that mistake.

I built a safety net. It accidentally became a teacher.

### Tweet 4 (CTA — Link Goes Here) ~260 chars

Two commands to install:

claude plugin marketplace add davidmoneil/aifred-document-guard
claude plugin install document-guard@aifred-document-guard

https://github.com/davidmoneil/aifred-document-guard

Full writeup: https://cisoexpert.com/blog/how-i-made-claude-code-safer-and-you-can-too/

What has Claude Code broken on you? I want to hear it.

---

## LinkedIn (Single Post)

**Status**: published (2026-02-10)

Claude Code will overwrite your files, causing critical failures.

Claude Code does have permission rules for which tools can run, but not permissions for once an edit is approved, nothing validates *what gets written*.

That's the gap.

So I built Document Guard (open source)— a Claude Code plugin that inspects every file edit before it hits disk. One install command, zero config, 11 protection rules active immediately.

What it catches out of the box:
- Credentials written into source code (13 patterns: AWS keys, GitHub tokens, JWTs, database URLs)
- Sections silently removed from CLAUDE.md during full-file rewrites
- Top-level keys deleted from config files
- Shebang lines stripped from scripts

Not everything gets the same response. Critical violations (credential leaks, .env writes) get blocked. Medium violations get flagged as warnings. Everything is logged and auditable. Overrides are single-use and time-limited — same principle as break-glass in access management.

If your team is adopting AI coding assistants, this is the layer most people are missing. Permission rules are your firewall. Document Guard is your content inspection.

Full writeup: https://cisoexpert.com/blog/how-i-made-claude-code-safer-and-you-can-too/
GitHub: https://github.com/davidmoneil/aifred-document-guard
Part of the AIfred ecosystem: https://github.com/davidmoneil/AIfred

#ClaudeCode #AI #CyberSecurity #DeveloperTools #OpenSource

---

## Reddit

**Subreddit**: r/ClaudeAI (primary), cross-post to r/ChatGPTCoding, r/cybersecurity (retitled)
**Status**: ready
**Visual**: Include terminal screenshot of Document Guard blocking an edit (after "11 protection rules" line)

**Title: I built a Claude Code plugin that catches bad edits before they hit disk — looking for feedback before v2**

Claude can sometimes go off the rails, and do stupid things. It did this to me, and new Claude sessions wouldn't load, as it added JSON to a config file breaking the formatting. When I reviewed the damage, it had also stuffed in content that didn't belong there.  Claude is good at creating content, but not always understanding the context of where its putting it.  

That wasn't a one-off. Over the next few weeks it kept happening:

- Rewrote my `CLAUDE.md` and silently dropped entire sections — which meant Claude lost its own project instructions on the next load
- "Fixed" a YAML config by deleting top-level keys, breaking the app
- "Cleaned up" a shell script and stripped the shebang that CI depends on

Claude didn't *mean* to break anything. But Claude Code only validates *which tools* can run — not *what gets written*. That's the gap. If you think about it in security terms: permission rules are your firewall, but once traffic is allowed through, nothing inspects the payload.

So I built Document Guard — a Claude Code plugin that intercepts every Edit and Write and validates it against configurable rules *before* it hits disk. One install command. Zero config. 11 protection rules active immediately.

What it catches out of the box:

- **Credential scanning**: 13 patterns (AWS keys, GitHub tokens, JWTs, etc.) with placeholder detection to avoid false positives
- **Structure preservation**: Catches when sections, headings, or YAML keys get silently removed during rewrites
- **Frontmatter locking**: Protects identity fields in skill/config files
- **Shebang preservation**: Catches when `#!/...` lines get stripped

Four response tiers (critical/high/medium/low) so not everything gets the same reaction — same principle behind alert fatigue management in a SOC. Credentials get blocked. A suspicious shebang removal gets a warning. Everything is logged and auditable. Overrides are single-use and time-limited — no permanent bypasses.

The part I'm most proud of: when Document Guard blocks a bad edit, it injects context back to Claude explaining *why* the edit was blocked. Claude reads that feedback and adjusts its behavior for the rest of the session. The guardrails don't just protect your files — they teach the AI in real-time.

Fully customizable with project-specific configs if you want to protect migration files, API schemas, or anything else specific to your stack.

This is v1 — 11 rules, 7 structural checks, and one opt-in semantic check using local Ollama. It's been running on my projects for weeks and catching real problems.

For v2 I'm considering:
- **Git-aware rules** — different protection levels for staged vs unstaged files
- **Team config sharing** — shareable rule sets so your whole team gets the same guardrails
- **Multi-model semantic checks** — expand beyond Ollama to support other local models

Which of those would be most useful to you? And what has Claude Code broken on you that Document Guard doesn't catch yet? I want to build for real problems.

Open source (MIT): https://github.com/davidmoneil/aifred-document-guard
Full writeup: https://cisoexpert.com/blog/how-i-made-claude-code-safer-and-you-can-too/

---

## Hacker News

**Title: Document Guard – A Claude Code plugin that teaches Claude what not to touch**

**URL: https://github.com/davidmoneil/aifred-document-guard**

**First Comment:**

Author here. I've been running Claude Code on real projects for months. It's great at writing code — but it doesn't always understand the consequences of what it writes. Config files get malformed, sections get silently dropped from markdown, credentials end up in tracked files.

Claude Code has access controls (which tools can run) but nothing validates the content of approved edits. Document Guard fills that gap as a PreToolUse hook — inspects every Edit/Write before it hits disk.

The part I find most interesting: when Document Guard blocks an edit, it injects context back to Claude explaining why. Claude reads that feedback and adjusts its behavior for the rest of the session. The guardrails teach the AI in real-time.

Technical details:
- 7 structural checks + 1 opt-in semantic check (local Ollama)
- Glob-based rule matching with specificity ranking
- Four response tiers: critical (block) / high (block) / medium (warn) / low (log)
- Single-use time-limited overrides (break-glass model)
- JSONL audit logging
- Two-tier config (project override > plugin default)

~700 lines of vanilla Node.js, no dependencies. One install command, zero config, 11 rules active immediately.

Config is plain JS (not JSON) so you get comments and logic. Copy the default, add your rules, done.

Full writeup: https://cisoexpert.com/blog/how-i-made-claude-code-safer-and-you-can-too/

Part of AIfred (https://github.com/davidmoneil/AIfred), a larger Claude Code configuration framework.

---

## Cross-posting Schedule (suggested)

| Day | Platform | Content |
|-----|----------|---------|
| Day 1 | Twitter/X thread | Full thread |
| Day 1 | LinkedIn | Single post |
| Day 2 | Reddit r/ClaudeAI | Reddit post |
| Day 2 | Hacker News | Show HN submission |
| Day 3 | Twitter reminder | Quote-tweet thread with the demo video/GIF |
| Day 5 | Blog post | Full article on cisoexpert.com |
| Day 7 | LinkedIn follow-up | Key insight from the blog + link |

---

## Links

- Article: https://cisoexpert.com/blog/how-i-made-claude-code-safer-and-you-can-too/
- Document Guard: https://github.com/davidmoneil/aifred-document-guard
- AIfred: https://github.com/davidmoneil/AIfred
- Pre-selection hooks article: https://cisoexpert.com/blog/how-i-made-claude-code-10-30x-faster-with-pre-selection-hooks
