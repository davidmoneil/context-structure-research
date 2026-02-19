---
title: "Social Media Copy: Pre-Selection Hooks + AIfred Launch"
date: 2026-02-05
article: "How-I-Made-Claude-Code-10-30x-Faster-With-Pre-Selection-Hooks"
status: ready
tags:
  - social-media
  - ciso-expert
  - aifred
version: 1
version_history:
  - v1: "2026-02-10 - Backfill versioning (original content)"
---

# Social Media Copy: Pre-Selection Hooks + AIfred Launch

## Twitter/X (Thread)

### Tweet 1 (Hook)

Every code navigation in Claude Code costs 250-350ms. Multiply that across hundreds of searches per day and you're losing hours.

I cut it to ~50ms with three hooks. Here's how pre-selection beats post-selection:

### Tweet 2

The insight: guidance buried in system prompts competes with task context. It's background noise.

Pre-selection hooks intercept the decision BEFORE Claude commits to a tool — with full context about what you're asking.

### Tweet 3

Three layers:

Layer 1: Soft guidance — pattern-match the prompt, inject "use LSP" as context
Layer 2: Hard redirect — if Claude picks Grep anyway, block it
Layer 3: Advisory — track patterns for continuous improvement

Total hook overhead: 5-15ms per layer.

### Tweet 4

I originally claimed 50x faster. Then I actually benchmarked it.

Real numbers: 5-7x typical, 10-30x on larger codebases.

Inflating numbers undermines credibility. Benchmark before you publish.

### Tweet 5 (CTA)

Full writeup with architecture diagrams and implementation details:
https://cisoexpert.com/blog/how-i-made-claude-code-10-30x-faster-with-pre-selection-hooks

The hooks are open source in AIfred — a configuration framework for Claude Code:
https://github.com/davidmoneil/AIfred

---

## LinkedIn (Single Post)

**I made Claude Code 10-30x faster at code navigation. Here's the principle behind it.**

Most AI tool guidance works like this: bury preferences in system prompts and hope the model follows them. That's post-selection — guidance that arrives after the decision is already being made.

Pre-selection works differently. You intercept the decision before the model commits, with full context about what the user is asking.

I built three hooks that operate at different points in Claude Code's decision pipeline:

1. **Soft guidance** — pattern-match the user's prompt and inject tool recommendations as request context
2. **Hard redirect** — if the model still picks the wrong tool, block it and redirect
3. **Advisory tracking** — log patterns for continuous improvement

The result: code navigation drops from 250-350ms (text search) to ~50ms (LSP). For security workflows like incident response and log analysis, where you're navigating code hundreds of times per day, this compounds fast.

I originally claimed 50x. Then I benchmarked it and corrected to 10-30x. Honest numbers matter more than impressive ones.

Full writeup: https://cisoexpert.com/blog/how-i-made-claude-code-10-30x-faster-with-pre-selection-hooks

The hooks are open source in AIfred, a configuration framework I built for Claude Code: https://github.com/davidmoneil/AIfred

#ClaudeCode #AI #DeveloperProductivity #OpenSource

---

## Links

- Article: https://cisoexpert.com/blog/how-i-made-claude-code-10-30x-faster-with-pre-selection-hooks
- AIfred: https://github.com/davidmoneil/AIfred
