---
title: "Social Media Copy: 849 Tests on AI Context Files"
date: 2026-02-05
article: "I-Ran-849-Tests-on-AI-Context-Files-Heres-What-Actually-Works"
status: ready
tags:
  - social-media
  - ciso-expert
  - context-research
version: 1
version_history:
  - v1: "2026-02-10 - Backfill versioning (original content)"
---

# Social Media Copy: 849 Tests on AI Context Files

## Twitter/X (Thread)

### Tweet 1 (Hook)

I ran 849 tests to find out if folder structure matters for AI reference files.

The answer surprised me: the simplest approach — all files in one flat folder — beat every organized hierarchy at every scale.

Here's what the data actually shows:

### Tweet 2

Why flat wins: Claude doesn't read every file. It scans the filenames first and picks which ones look relevant.

With flat structure, it sees all your filenames at once — one list, one decision.

With nested folders, every level is a chance to take a wrong turn and miss the answer.

### Tweet 3

The most counterintuitive finding: "helper" files — keyword indexes, summaries, navigation docs — actually hurt accuracy at scale.

At 302K words: 100% with or without them.
At 622K words: 97.35% without → 92.74% with.

The index became noise competing for context window space.

### Tweet 4

The practical version:

- Flat folder, descriptive filenames
- One topic per file
- Skip enhancement indexes above 300K words
- Your filenames ARE the index

Tested across 120K, 302K, and 622K word corpora. The simplest approach won every time.

### Tweet 5 (CTA)

Full writeup with methodology, data tables, and practical recommendations:
https://cisoexpert.com/blog/i-ran-849-tests-on-ai-context-files-heres-what-actually-works

Test harness and data are open source — $20 in API costs, fully reproducible:
https://github.com/davidmoneil/context-structure-research

---

## LinkedIn (Single Post)

**I ran 849 tests to find the best way to organize AI reference files. The answer was simpler than I expected.**

If you use Claude Code with reference documentation — security playbooks, compliance frameworks, runbooks, architecture docs — how you organize those files directly affects the quality of answers you get back.

I assumed a well-organized folder hierarchy would outperform a flat directory. Clean categories, logical nesting, maybe an index file. That's just good practice, right?

The data said otherwise.

I built a synthetic knowledge base at three scales (120K, 302K, and 622K words), organized the same files in five different structures, and asked 23 known-answer questions across each combination.

**Results:**

- Flat structure (all files in one folder) hit 100% accuracy at 302K words
- Each level of folder nesting costs 1-2% accuracy
- At 622K words, adding "helper" indexes dropped accuracy from 97.35% to 92.74%

**Why?** Claude scans filenames first, then decides which files to read. With flat structure, it sees every filename at once — one list, one selection decision. With nested folders, every level is a chance to miss a relevant file.

**The practical takeaway:**

1. Put all reference files in one folder
2. Use descriptive filenames (they ARE the index)
3. One topic per file
4. Skip helper indexes above 300K words

If you're building security documentation or compliance libraries for AI-assisted workflows, the highest-performing approach is also the easiest to maintain.

Full writeup: https://cisoexpert.com/blog/i-ran-849-tests-on-ai-context-files-heres-what-actually-works

Test harness is open source ($20 in API costs, fully reproducible): https://github.com/davidmoneil/context-structure-research

#ClaudeCode #AI #DeveloperProductivity #Cybersecurity #DataDriven

---

## Links

- Article: https://cisoexpert.com/blog/i-ran-849-tests-on-ai-context-files-heres-what-actually-works
- GitHub: https://github.com/davidmoneil/context-structure-research
