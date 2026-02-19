---
title: "LinkedIn Post - Context Structure Research"
type: social
status: draft
date: 2026-01-31
platform: linkedin
related: "How-I-Got-100-Percent-Accuracy-from-Claude-Code.md"
version: 1
version_history:
  - v1: "2026-02-10 - Backfill versioning (original content)"
---

# LinkedIn Post - Context Structure Research

## Post Content

**I ran 849 tests to figure out why Claude Code kept missing information in my security documentation.**

The answer surprised me.

Quick context: Claude Code lets you point the AI at your own files using `@` references. Type `@docs/` and Claude can read your documentation when answering questions.

I've been using this for cybersecurity work—IR playbooks, configuration analysis, procedure docs. As my files grew to 600K+ words, Claude's answers got inconsistent.

Was it my folder structure? Did I need better organization?

Instead of guessing, I tested it. 849 times.

**The finding**: Put all your files in one flat folder.

- Flat folder: 100% accuracy at 302K words
- Each folder level costs ~1-2% accuracy
- Adding index files actually *hurt* at scale (-4.6%)

Why? When you use `@folder/`, Claude lists the filenames first and picks which to read based on names alone.

`incident-response-ransomware.md` in a flat folder beats `docs/security/playbooks/ransomware/response.md` every time.

Claude sees all your filenames at once → better selection → better answers.

I've open-sourced everything: test harness, all 849 results, methodology.

📎 Full write-up: [cisoexpert.com link - UPDATE WHEN PUBLISHED]
📎 GitHub: https://github.com/davidmoneil/context-structure-research

If you're building reference files for Claude Code, skip the folder hierarchy. Simplicity wins.

---

## Posting Notes

- Best times: Tuesday-Thursday, 8-10am or 12-1pm
- Add relevant hashtags: #ClaudeAI #AI #Productivity #CyberSecurity #Development
- Consider tagging Anthropic
