# Executive Summary: Context Structure Research

**One-page summary for busy readers**

---

## The Question

How should you organize context files for Claude Code to maximize answer accuracy?

---

## The Study

- **849 tests** across 5 structures, 6 enhancements, 3 corpus sizes
- **Corpus**: 120K → 302K → 622K words
- **Model**: Claude 3.5 Haiku
- **Ground-truth evaluation** against 23 known-answer questions

---

## Key Findings

### 1. Flat Structure Wins

| Structure | Accuracy |
|-----------|----------|
| **Flat** | **97-100%** |
| Shallow (1 level) | 94-100% |
| Deep (3 levels) | 92-96% |
| Very Deep (5 levels) | 95-96% |

**Use flat.** Every level of nesting costs ~1-2% accuracy.

### 2. One Topic Per File

Claude assesses relevance from filenames. If each file covers one topic with a descriptive name, Claude can select the right files without reading them all.

**Example**: `employees-leadership-bios.md` beats `docs/org/people/leaders.md`

### 3. Skip Enhancement Indexes at Scale

| Enhancement | At 302K | At 622K |
|-------------|---------|---------|
| None (flat) | 100% | 97.35% |
| With indexes | 100% | 92.74% |

**Indexes hurt at 622K words.** The overhead becomes noise.

### 4. Scale Is Manageable

First meaningful accuracy drop appears around 600K words, and it's only 2.65%. Structure matters more than size.

---

## Recommendations

| Project Size | Strategy |
|--------------|----------|
| <100K | Anything works |
| 100-300K | Flat, keyword index optional |
| 300-600K | Flat, skip indexes |
| 600K+ | Flat, consider splitting |

---

## The Bottom Line

**Put your files in one directory with clear, descriptive names.**

That's it. The simplest approach is the best approach.

---

## Links

- **Full Report**: [report/README.md](README.md)
- **GitHub**: [context-structure-research](https://github.com/YOUR-USERNAME/context-structure-research)
- **Blog Post**: [cisoexpert.com](https://cisoexpert.com)

---

*849 tests. $20 API cost. January 2026.*
