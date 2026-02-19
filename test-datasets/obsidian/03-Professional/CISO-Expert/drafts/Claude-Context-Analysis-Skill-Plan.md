---
title: "Claude Context Analysis Skill - Development Plan"
type: project-plan
status: planning
date: 2026-01-31
related:
  - "[[How-I-Got-100-Percent-Accuracy-from-Claude-Code]]"
  - "[[LinkedIn-Context-Structure-Research]]"
github: https://github.com/davidmoneil/context-structure-research
tags: [claude-code, skill, product, ai-tools]
version: 1
version_history:
  - v1: "2026-02-10 - Backfill versioning (original content)"
---

# Claude Context Analysis Skill - Development Plan

**Purpose**: Create a Claude Code skill that analyzes users' context file setup and provides optimization recommendations based on the 849-test research study.

**Target**: Official Anthropic Skills Repo submission

---

## Market Gap Analysis

### Existing Tools (None Match Our Approach)

| Existing Tool | What It Does | Gap |
|--------------|--------------|-----|
| Claude Memory Optimizer | Compresses/refactors CLAUDE.md content | Doesn't analyze structure depth or apply research-based thresholds |
| ClaudeCodeOptimizer | Architecture review, code quality | Focused on code, not context file organization |
| claude-flow CLAUDE.md Optimizer | Generates tailored CLAUDE.md | Creates files, doesn't grade existing setup |

### Our Unique Value

- **Research-backed**: Based on 849 controlled tests (not opinions)
- **Data-driven thresholds**: 100K, 300K, 600K word boundaries validated
- **Structure analysis**: Measures depth, not just content
- **Quantified impact**: "-4.6% accuracy" vs vague "best practices"

---

## Anthropic Skills Repo Requirements

| Requirement | Our Skill | Status |
|-------------|-----------|--------|
| Self-contained folder | Yes | Ready |
| SKILL.md with YAML frontmatter | Yes | To create |
| Clear description | "Analyzes Claude Code context files and provides optimization recommendations based on 849-test research study" | Ready |
| Practical utility | Every Claude Code user could benefit | Strong |
| Unique contribution | Research-backed, data-driven | Differentiator |
| Non-harmful | Analysis only, optional fixes | Safe |

**Assessment**: Good candidate for official repo.

---

## Skill Specification

### Name
`claude-context-analysis`

### Commands

```
/context-analyze              # Run full analysis, output to terminal
/context-analyze --fix        # Analyze + offer to fix issues
/context-analyze --report     # Generate markdown report file
```

### Analysis Checks (Research-Based)

| Check | Threshold | Research Source |
|-------|-----------|-----------------|
| Max folder depth | Warn if >2 levels | Each level costs ~1-2% accuracy |
| Total word count | Warn >300K, Critical >600K | Enhancements hurt at 622K |
| Enhancement overhead | Warn if index files >10% | -4.6% at scale |
| Filename quality | Flag generic names | "Filenames ARE the index" |
| CLAUDE.md size | Warn if >500 words | Competes for context window |
| Topic cohesion | Flag multi-topic files | One topic = one file principle |

---

## Sample Output

```
📊 Claude Context Analysis
===========================
Based on: Context Structure Research (849 tests)
Methodology: github.com/davidmoneil/context-structure-research

Overall Grade: B (Good, room for improvement)

Structure Analysis
├─ Max depth: 2 levels ✅ (optimal: ≤2)
├─ Total files: 47 ✅
└─ Layout: SHALLOW (recommended: FLAT)

Scale Analysis
├─ Total words: 287,000 ⚠️ (approaching 300K threshold)
├─ CLAUDE.md: 1,847 words ⚠️ (recommended: <500)
└─ Index overhead: 3.2% ✅

Filename Quality
├─ Descriptive: 42/47 (89%) ✅
└─ Flagged: utils.md, misc.md, notes.md, temp.md, old.md

Recommendations (by impact):
1. [HIGH] Flatten structure - move files to single directory
   Research: Flat achieves 100% vs 94.42% at your scale

2. [MEDIUM] Trim CLAUDE.md from 1,847 to <500 words
   Move detailed content to dedicated files

3. [LOW] Rename generic files with descriptive names
   utils.md → what's actually in there?

Run `/context-analyze --fix` to apply recommendations
Full methodology: https://github.com/davidmoneil/context-structure-research
```

---

## File Structure

```
claude-context-analysis/
├── SKILL.md                    # Core instructions + research summary
├── scripts/
│   ├── analyze.py              # Scan and measure context files
│   ├── grade.py                # Apply research thresholds
│   └── fix.py                  # Optional restructuring
├── references/
│   ├── research-summary.md     # Key findings from 849 tests
│   └── thresholds.md           # Detailed threshold explanations
└── templates/
    └── report-template.md      # Output format
```

---

## Technical Components

### 1. analyze.py - Directory Scanner

```python
# Core functions needed:
def scan_directory(path: str) -> dict:
    """Walk directory, collect metrics"""
    # - Count files
    # - Measure max depth
    # - Calculate word counts per file
    # - Identify file types

def analyze_filenames(files: list) -> dict:
    """Score filename quality"""
    # - Check for generic names (utils, misc, temp, etc.)
    # - Check for entity-rich descriptive names
    # - Flag problematic patterns

def calculate_enhancement_overhead(files: list) -> float:
    """Measure index vs content ratio"""
    # - Identify index/summary files
    # - Calculate percentage of total words
```

### 2. grade.py - Scoring Logic

```python
# Research-based thresholds
THRESHOLDS = {
    'max_depth': {'optimal': 0, 'warn': 2, 'critical': 4},
    'word_count': {'safe': 100000, 'warn': 300000, 'critical': 600000},
    'claude_md_words': {'optimal': 500, 'warn': 1000, 'critical': 2000},
    'enhancement_overhead': {'safe': 0.05, 'warn': 0.10, 'critical': 0.15},
    'filename_quality': {'good': 0.90, 'warn': 0.75, 'critical': 0.50}
}

def calculate_grade(metrics: dict) -> str:
    """Convert metrics to letter grade A-F"""

def generate_recommendations(metrics: dict) -> list:
    """Create prioritized recommendations"""
```

### 3. fix.py - Optional Restructuring

```python
def flatten_structure(source: str, target: str) -> None:
    """Move nested files to flat directory"""

def rename_generic_files(files: list) -> list:
    """Suggest better names for generic files"""

def trim_claude_md(path: str, target_words: int) -> str:
    """Extract content to separate files"""
```

---

## Development Tasks

- [ ] Create SKILL.md with research summary and instructions
- [ ] Build analyze.py (directory scanning)
- [ ] Build grade.py (threshold logic)
- [ ] Build fix.py (restructuring helpers)
- [ ] Create references/research-summary.md
- [ ] Create templates/report-template.md
- [ ] Test on AIProjects
- [ ] Test on 2-3 other projects
- [ ] Write README for GitHub
- [ ] Submit PR to anthropics/skills

---

## Publishing Strategy

### Step 1: Create in context-structure-research repo
Keep research + tool together in same repo

### Step 2: Test locally
- AIProjects (large, complex)
- A smaller project
- Edge cases (empty, monolith, very deep)

### Step 3: Publish to GitHub
- Ensure repo is public
- Add skill to repo structure
- Update README to mention skill

### Step 4: Submit to Anthropic
- PR to github.com/anthropics/skills
- Highlight research backing as differentiator

### Step 5: Auto-indexed by marketplaces
- SkillsMP (needs 2+ stars)
- SkillHub (auto-indexes)

---

## Effort Estimate

| Component | Hours |
|-----------|-------|
| SKILL.md definition | 1-2 |
| analyze.py | 2-3 |
| grade.py | 2-3 |
| fix.py | 2-3 |
| Testing/refinement | 2-4 |
| Documentation | 1-2 |
| **Total** | **10-17 hours** |

---

## Links

- **Research Repo**: https://github.com/davidmoneil/context-structure-research
- **Blog Article**: [[How-I-Got-100-Percent-Accuracy-from-Claude-Code]]
- **LinkedIn Post**: [[LinkedIn-Context-Structure-Research]]
- **Anthropic Skills**: https://github.com/anthropics/skills
- **SkillsMP**: https://skillsmp.com/
- **SkillHub**: https://www.skillhub.club/

---

*Created: 2026-01-31*
