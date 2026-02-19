---
title: "The Hidden Cost of AI Context: What 849 Tests Reveal About Token Efficiency"
type: post
status: draft
date: 2026-02-05
source: cisoexpert.com
tags: [ai, claude-code, productivity, development, research, context-management, tokens]
version: 1
version_history:
  - v1: "2026-02-10 - Backfill versioning (added frontmatter)"
---

# The Hidden Cost of AI Context: What 849 Tests Reveal About Token Efficiency

**Status**: DRAFT
**Type**: Follow-up to "I Ran 849 Tests on AI Context Files"
**Author**: David O'Neil
**Target**: cisoexpert.com blog

---

## Frontmatter (for Astro site)

```yaml
---
title: "The Hidden Cost of AI Context: What 849 Tests Reveal About Token Efficiency"
date: 2026-02-XX
description: "Flat structure wins on accuracy—but at what cost? I dug into the token consumption data from 849 tests and found a tradeoff nobody's talking about."
tags: [ai, claude-code, productivity, development, research, context-management, tokens]
author: "David O'Neil"
categories: ["Cybersecurity"]
image: "/images/blog-placeholder.png"
draft: true
---
```

---

## Draft Body

# The Hidden Cost of AI Context: What 849 Tests Reveal About Token Efficiency

Last month I published [I Ran 849 Tests on AI Context Files](/blog/i-ran-849-tests-on-ai-context-files-heres-what-actually-works). The conclusion was straightforward: flat folder structure beats nested hierarchies for AI accuracy. Put your files in one directory with descriptive names. Done.

But several readers asked the obvious follow-up question: **What does that cost?**

I'd been sitting on the token consumption data from those same 849 tests. When I finally dug in, I found a tradeoff that changes how you should think about organizing AI reference files—especially at scale.

## The Question Nobody Asked

The original study measured **accuracy**: did Claude find the right answer? Flat structure won at every scale, topping out at 100% accuracy for corpora under 300K words.

But accuracy isn't free. Every time Claude navigates your files, it consumes tokens—reading filenames, opening documents, processing content. Different folder structures force Claude through different navigation paths, which means different token costs.

The question I wanted to answer: **Does the most accurate structure also cost the most to run?**

## What I Measured

Each of the 849 test runs captured detailed token usage:

- **Cache creation tokens**: First-time processing of file content
- **Cache read tokens**: Re-reading previously cached content
- **Input/output tokens**: The question and answer themselves
- **Total cost in USD**: What Anthropic actually charged

I broke this down across the same five structures from the original study (flat, shallow, deep, very-deep, monolith) and the same three corpus sizes (120K, 302K, 622K words).

## The Finding: Accuracy Costs 3x the Tokens

Here's the data that surprised me. At 120K words (where all structures had complete token tracking):

| Structure | Avg Tokens/Test | Accuracy | Cost/Test |
|-----------|----------------:|---------:|----------:|
| **Flat** | 155,000 | 100% | $0.065 |
| Shallow | 108,000 | 100% | $0.057 |
| Monolith | 91,000 | 100% | $0.058 |
| Deep | 47,000 | 93% | $0.048 |
| Very-Deep | 49,000 | 96% | $0.046 |

**Flat structure uses 3x more tokens than deep or very-deep.** At 120K words, all three top structures hit perfect accuracy—but flat does it by consuming 155K tokens per query versus ~48K for deep nesting.

Why? Because flat structure gives Claude a complete view of every filename in one shot. It reads the entire directory listing upfront—a large token cost—then makes a single, well-informed selection decision. Deep structures let Claude navigate selectively, reading only the folder names at each level. Fewer tokens per step, but more chances to take a wrong turn.

## The Tradeoff Shifts at Scale

At 120K words, the tradeoff is clear: pay 3x the tokens, get 100% accuracy instead of 93%. Worth it.

But watch what happens at 622K words:

| Structure | Avg Tokens/Test | Accuracy | Cost/Test |
|-----------|----------------:|---------:|----------:|
| **Flat** | 45,000 | 93% | $0.057 |
| Shallow | 46,000 | 94% | $0.053 |
| Deep | 37,000 | 92% | $0.038 |
| Very-Deep | 47,000 | 96% | $0.053 |

At this scale, flat structure drops to 93% accuracy—while deep catches up at 92%. The token gap narrows. And very-deep actually **outperforms flat on accuracy** (96% vs 93%) at comparable token cost.

**The accuracy premium you're paying for with flat structure evaporates above 600K words.**

## The Efficiency Metric

To make this concrete, I calculated "tokens per accuracy point"—how many tokens does each structure need to achieve 1% of accuracy?

| Structure | Avg Accuracy | Avg Tokens | Tokens per 1% Accuracy |
|-----------|:------------:|----------:|-----------------------:|
| Very-Deep | 96.0% | 48K | **497** |
| Deep | 93.4% | 48K | 514 |
| Shallow | 98.6% | 122K | 1,233 |
| Monolith | 99.5% | 158K | 1,587 |
| Flat | 97.6% | 158K | 1,623 |

Deep and very-deep structures are **3x more token-efficient** than flat. They extract more accuracy per token spent.

Does that mean you should switch to deep nesting? Not necessarily. It depends on what you're optimizing for.

## What This Means for Your Workflow

### If you're optimizing for accuracy (and you probably should be):

Stick with the original recommendation. Flat structure delivers the highest accuracy up to 300K words. The token premium is real but manageable—roughly $0.02 per query more than nested structures.

For most security workflows—incident response lookups, compliance checks, policy queries—an extra two cents per question is invisible. A missed document during an active incident is not.

### If you're running high-volume automated queries:

The cost difference matters. If you're processing hundreds of queries per day against a large corpus—automated compliance scanning, bulk documentation review, CI/CD pipeline checks—the token premium adds up.

At 100 queries/day:
- Flat: ~$6.50/day
- Deep: ~$3.80/day
- **Savings: ~$80/month**

For automated, high-volume use cases against large corpora (600K+ words), deep structure with descriptive path names may be the better tradeoff—slightly lower accuracy, significantly lower cost.

### If your corpus is over 600K words:

The original recommendation to split into sub-corpora gets even stronger. Not only does accuracy degrade at this scale, but the token efficiency advantage of flat structure disappears entirely. Split your files into domain-specific folders, keep each one flat internally, and point Claude at the relevant subset.

## The Bigger Picture

This data reveals something fundamental about how AI navigates your files:

**Flat structure front-loads the cost.** Claude reads everything upfront—big token hit—then makes one informed decision. High cost, high accuracy.

**Nested structure distributes the cost.** Claude navigates level by level—small token hits—but makes multiple sequential decisions. Lower cost, lower accuracy.

It's the classic breadth-vs-depth search tradeoff, playing out in your file system. And like most engineering tradeoffs, the right answer depends on your constraints.

## Updated Recommendations

My recommendations from the original study still hold, with one addition:

| Your Situation | Strategy |
|---------------|----------|
| Under 300K words, accuracy matters | **Flat** (original recommendation stands) |
| Under 300K words, high volume queries | **Flat** (cost difference is negligible at this scale) |
| 300-600K words, accuracy matters | **Flat**, skip enhancement indexes |
| 300-600K words, high volume queries | Consider **shallow** (1 level) as a compromise |
| 600K+ words | **Split into flat sub-corpora** (best of both worlds) |

The new insight: if you're building automated pipelines that query your documentation hundreds of times per day, the token cost of flat structure is a real line item. Factor it into your architecture decisions.

## The Bottom Line

Flat structure is still the right default. The accuracy advantage is real and meaningful, especially under 300K words. But it's not free—you're paying a 3x token premium for that accuracy.

For most use cases, that premium is worth paying. For high-volume automated workflows against large corpora, it's worth knowing about so you can make an informed tradeoff.

**The best engineering decisions come from understanding the costs, not just the benefits.** Now you know both.

---

*This analysis uses the same 849-test dataset from the [original study](/blog/i-ran-849-tests-on-ai-context-files-heres-what-actually-works). Token consumption data was extracted from raw API response logs. All data and analysis tools are available in the [GitHub repository](https://github.com/davidmoneil/context-structure-research).*

---

## DRAFT NOTES (remove before publishing)

### Data gaps to address before publishing
- V4/V5 flat, monolith, and shallow structures have **zero token data** in the raw files — the harness wasn't capturing usage for these configs. V1-V3 and V6 have complete data.
- The averages in this article use data points where token tracking was active. Consider re-running V4/V5 flat tests to fill the gap, or note the limitation explicitly.

### Visual assets ready to use
- **Interactive JSX visualization**: `06-Sessions/2026/02-Feb/context-structure-analysis.jsx`
  - Recharts-based React component with 3 tabbed views:
    1. **Tokens vs Accuracy scatter plot** — shows the 3x gap between flat/monolith and deep/very-deep clusters
    2. **Efficiency bars** — tokens per 1% accuracy, total consumption, and accuracy side-by-side
    3. **V1 Cost Comparison cards** — 5-column card layout with accuracy, tokens, and cost per structure
  - Dark theme, polished UI — can be embedded directly in an Astro blog post or rendered as static screenshots
  - Already has the key data points baked in (STRUCTURES and V1_DATA constants)
  - Callout boxes with the "3x more tokens" and "497 vs 1,623 efficiency" insights pre-written

### Potential additions
- Per-question-type breakdown (navigation vs cross-reference vs depth queries) and token cost
- Cache efficiency analysis — how much reuse saved across sequential runs
- Comparison with other models (Sonnet, Opus) if data becomes available
- Render the JSX component to static PNG/SVG for social media cards

### Promotion ideas
- LinkedIn post tying back to original article
- Dev.to cross-post
- Reddit r/ClaudeAI, r/ChatGPT threads about context management
