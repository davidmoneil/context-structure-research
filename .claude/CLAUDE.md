# Context Structure Research

A research project testing how Claude Code handles different `@` file reference hierarchies.

## Project Purpose

Empirically determine optimal context structure for Claude Code projects by testing:
- Navigation ability (find specific facts)
- Cross-reference synthesis (connect information across files)
- Depth understanding (complex reasoning)

## Test Corpus

**Soong-Daystrom Industries** - A fictional company with ~120K words of documentation.

Star Trek adjacent naming (potential hallucination bait for testing).

## Key Locations

- `soong-daystrom/` - Test corpus in 5 structure variants
- `soong-daystrom/_source/` - Canonical source content
- `harness/` - Test execution infrastructure
- `results/` - Raw outputs and analysis
- `research-notes/` - Internal tracking (not published)

## Structure Variants

Each variant has its own CLAUDE.md in `.claude/configs/<variant>/`:

| Variant | Description |
|---------|-------------|
| monolith | Single file with everything |
| flat | Many files, no folders |
| shallow | 2-level hierarchy |
| deep | 3-4 level hierarchy |
| very-deep | 5+ level hierarchy |

## Test Execution

Tests run via `claude -p` with symlinked CLAUDE.md:

```bash
# Swap to shallow config
ln -sf configs/shallow/CLAUDE.md .claude/CLAUDE.md

# Run test
claude -p "Question here" --print
```

## Content Categories

- History, Organization, Employees, Products
- Projects, Policies, Financial, Meetings

## Ground Truth

All facts defined in `research-notes/canon.md` - the authoritative source.
