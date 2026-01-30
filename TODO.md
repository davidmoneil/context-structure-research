# Context Structure Research - TODO

Project deliverables and next steps.

---

## Current Status (2026-01-30)

### Completed
- [x] V4 corpus (120K words) - built and tested
- [x] V5 corpus (302K words) - built and tested
- [x] V6 corpus (622K words) - **built, NOT tested**
- [x] V5 enhancement variants (V5.1-V5.5) - built and tested
- [x] Methodology documentation (`docs/methodology.md`)
- [x] Question complexity analysis (23 questions documented)

### In Progress
- [ ] Context grading skill (`/context-grade`)
- [ ] Blog post (cisoexpert.com)
- [ ] GitHub repo cleanup

### Completed (This Session)
- [x] V5.5 full matrix test (92/92 complete)
- [x] V4 results analysis (230 tests evaluated)
- [x] V5 results analysis (191 tests evaluated)
- [x] V5-enhancements results analysis (60 tests evaluated)
- [x] V5.5 matrix results analysis (92 tests evaluated)
- [x] Cross-variant comparison report (`results/cross-variant-comparison.md`)
- [x] V6 structure variants (flat-v6, deep-v6, flat-v6-v5.5, deep-v6-v5.5)
- [x] V6 testing (184/184 tests complete)
- [x] V6 results analysis
- [x] **Final report** (`report/README.md`)
- [x] **Project charter** (`PROJECT-CHARTER.md`)
- [x] **Blog draft** (Obsidian: `AI-Sessions/Research/Context Structure Research - Blog Draft.md`)
- [x] **Phase 2 research plan** (`docs/phase-2-codebase-testing.md`)
- [x] Built shallow-v6 and very-deep-v6 structures

### Needs Debugging
- [ ] Run `./harness/run-v6-extended-matrix.sh` (script fixed, not yet run)
- [ ] Analyze extended V6 results (shallow-v6, very-deep-v6)

### Not Started
- [ ] Publish to GitHub
- [ ] Blog post publish to cisoexpert.com
- [ ] `/context-grade` skill
- [ ] Phase 2: Real codebase testing

---

## Deliverables

### 1. Final Report (Markdown)

**Target**: Publishable research for GitHub repo and blog

**Structure**:
```
report/
├── README.md           # Executive summary + key findings
├── methodology.md      # Full test methodology
├── findings.md         # Detailed results analysis
├── recommendations.md  # Practical guidance
├── cost-analysis.md    # Token/cost breakdown
└── reproduction.md     # How to replicate
```

**Executive Summary** (1 page):
- Key finding: "Keywords alone match combined approaches at 80% recovery"
- Quick recommendation: Use flat/shallow structure with keyword indexes
- Cost comparison: Tokens saved per configuration

**Findings to Include**:
1. Structure impact (flat/shallow 100% vs deep 92-97%)
2. Loading method comparison (adddir vs classic)
3. Enhancement strategies (keywords = best ROI)
4. Scale effects (V5 vs V4 performance)
5. Unsolved cases (XREF-006 analysis)

**Practical Recommendations**:
- Small projects (<100K words): Any structure works
- Medium projects (100-300K words): Flat + keyword index
- Large projects (300K+): Split structures required

### 2. Skill: `/context-grade`

**Purpose**: Audit and improve Claude Code context structure

**Phase 1 - Audit**:
- Scan project structure (depth, file counts, naming)
- Check for indexes, summaries, keyword metadata
- Measure file sizes, detect duplication
- Score against research-backed best practices

**Phase 2 - Report**:
- Overall grade (A-F) with rationale
- Specific issues found
- Prioritized recommendations with expected impact

**Phase 3 - Fix** (with permission):
- Create backup before changes
- Generate keyword index (`_index.md`)
- Flatten excessive nesting if needed
- Verify changes work correctly

**Skill Location**: `.claude/skills/context-grade/`

### 3. Blog Post (cisoexpert.com)

**Angles**:
- AI productivity gains: "How to get 40% better answers from Claude Code"
- Research methodology: "500+ configurations tested to find what works"

**Target Length**: 1500-2000 words

**Key Sections**:
1. The problem (context structure affects AI accuracy)
2. What we tested (methodology overview)
3. What we found (key results)
4. What you should do (actionable recommendations)
5. Try it yourself (link to skill/repo)

### 4. GitHub Repository

**Public repo structure**:
```
context-structure-research/
├── README.md           # Overview + quick start
├── docs/               # Full documentation
├── harness/            # Test runner and analysis tools
├── results/            # Raw and analyzed results
├── soong-daystrom/     # Test corpus (or sample)
└── skill/              # Exportable context-grade skill
```

**Reproducibility**: Include all scripts, raw data, and step-by-step reproduction instructions.

---

## V6 Testing Plan

V6 corpus is built (622K words, 276 files) but needs:

1. **Create V6 structure variants**:
   - flat-v6 (all files in root)
   - shallow-v6 (one level of folders)
   - deep-v6 (3-4 levels)
   - very-deep-v6 (5+ levels)
   - NO monolith (exceeds context limits)

2. **Run V6 matrix test**:
   - 23 questions × 4 structures × 2 loading methods = 184 tests
   - Model: Haiku (will fail on monolith due to 200K limit)
   - Consider Sonnet for comparison (if budget allows)

3. **Analyze scale effects**:
   - Compare V4 (120K) → V5 (302K) → V6 (622K)
   - Document accuracy degradation patterns
   - Identify scaling recommendations

---

## Priority Order

1. **Complete V5.5 matrix** (in progress, almost done)
2. **Analyze all V5 results** (V5 baseline + enhancements + V5.5)
3. **Draft report** (start with findings, then recommendations)
4. **Create `/context-grade` skill** (based on findings)
5. **V6 testing** (optional - validates scale effects)
6. **Publish** (blog + GitHub)

---

*Created: 2026-01-30*
*Last Updated: 2026-01-30*
