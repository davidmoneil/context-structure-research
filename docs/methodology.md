# Research Methodology

This document describes the methodology for testing how Claude Code handles different context structure organizations.

---

## Research Question

**How does the hierarchical structure of `@` file references affect Claude's ability to accurately answer questions about documented content?**

---

## Test Corpus

### Soong-Daystrom Industries

A fictional robotics and AI company providing realistic enterprise documentation across multiple domains.

| Version | Word Count | File Count | Purpose |
|---------|------------|------------|---------|
| V4 | ~120,000 | 80 | Baseline testing |
| V5 | ~302,000 | 121 | Scale testing |
| V6 | ~622,000 | 276 | Large corpus testing |

### Content Categories

- **Organization**: Executives, departments, facilities, employees
- **Products**: PCS series (companions), NIM series (neural interfaces), IAP platform, SCE
- **Projects**: Prometheus (AI consciousness), Atlas (industrial), Hermes (communication)
- **Financial**: Quarterly reports, budgets, forecasts
- **Operations**: Policies, procedures, meeting minutes
- **History**: Founding, acquisitions, milestones

---

## Structure Variants

Each corpus version is organized into multiple structure variants:

| Structure | Depth | Description | Example Path |
|-----------|-------|-------------|--------------|
| **Monolith** | 0 | Single concatenated file | `soong-daystrom.md` |
| **Flat** | 1 | All files in root directory | `executives.md`, `products.md` |
| **Shallow** | 2 | One level of category folders | `organization/executives.md` |
| **Deep** | 3-4 | Multiple nesting levels | `company/org/executives/maya-chen.md` |
| **Very Deep** | 5+ | Maximum practical nesting | `company/org/exec/c-suite/ceo/profile.md` |

### Loading Methods

- **Classic**: `cd` into directory, load with `@.`
- **Add-dir**: Use `--add-dir` flag to add context without changing directory

---

## Question Design

### Question Types

Questions are designed to test different retrieval and synthesis capabilities:

| Type | Count | Description | Files Required |
|------|-------|-------------|----------------|
| **Navigation** | 10 | Single fact lookup | 1 file |
| **Cross-reference** | 8 | Connect info across sources | 2-3 files |
| **Depth** | 5 | Synthesize complex relationships | 3-4 files |

### Difficulty Levels

| Difficulty | Count | Characteristics |
|------------|-------|-----------------|
| **Easy** | 8 | Direct lookup, single source |
| **Medium** | 8 | May require 2 files or inference |
| **Hard** | 7 | Multiple files, relationship synthesis |

### Question Complexity Matrix

| ID | Type | Difficulty | Files | Source Files |
|----|------|------------|-------|--------------|
| NAV-001 | navigation | easy | 1 | executives.md |
| NAV-002 | navigation | easy | 1 | founding.md |
| NAV-003 | navigation | easy | 1 | prometheus.md |
| NAV-004 | navigation | easy | 1 | departments.md |
| NAV-005 | navigation | easy | 1 | pcs-series.md |
| NAV-006 | navigation | medium | 2 | key-personnel.md, team-prometheus.md |
| NAV-007 | navigation | easy | 1 | quarterly-report-q3-2124.md |
| NAV-008 | navigation | medium | 2 | prometheus.md, prometheus-weekly.md |
| NAV-009 | navigation | easy | 1 | acquisition-neurosync.md |
| NAV-010 | navigation | medium | 2 | prometheus.md, facilities.md |
| XREF-001 | cross-reference | medium | 3 | prometheus.md, departments.md, executives.md |
| XREF-002 | cross-reference | medium | 2 | atlas.md, executives.md |
| XREF-003 | cross-reference | medium | 3 | key-personnel.md, acquisition-neurosync.md, nim-series.md |
| XREF-004 | cross-reference | medium | 1 | board-q3-2124.md |
| XREF-005 | cross-reference | easy | 2 | atlas.md, board-q3-2124.md |
| XREF-006 | cross-reference | hard | 2 | prometheus.md, hermes.md |
| XREF-007 | cross-reference | medium | 2 | executives.md, departments.md |
| XREF-008 | cross-reference | hard | 2 | acquisition-neurosync.md, nim-series.md |
| DEPTH-001 | depth | hard | 3 | budget.md, prometheus.md, atlas.md |
| DEPTH-002 | depth | hard | 3 | ai-ethics-policy.md, prometheus.md, board-q3-2124.md |
| DEPTH-003 | depth | hard | 4 | budget.md, quarterly-report.md, pcs-series.md, iap-platform.md |
| DEPTH-004 | depth | hard | 3 | prometheus.md, prometheus-weekly.md, ai-ethics-policy.md |
| DEPTH-005 | depth | hard | 3 | executives.md, acquisition-neurosync.md, prometheus.md |

### Answer Distribution Summary

| Files Required | Question Count | Percentage |
|----------------|----------------|------------|
| 1 file | 8 | 35% |
| 2 files | 8 | 35% |
| 3+ files | 7 | 30% |

---

## Enhancement Strategies

### Index-Based Enhancements

Testing whether adding metadata indexes improves retrieval accuracy:

| Variant | Description | Index Content |
|---------|-------------|---------------|
| **V5.1** | 2-sentence summaries | Brief factual summary per file |
| **V5.2** | 5-sentence summaries | Detailed summary per file |
| **V5.3** | 10 keywords | Entity/concept keywords per file |
| **V5.4** | 5-sentence + keywords | Combined approach |
| **V5.5** | 2-sentence + keywords | Minimal combined approach |

### Index Structure

Each enhancement creates a `_index.md` file with entries like:

```markdown
## @path/to/file.md
**Summary**: [Summary sentences here]
**Keywords**: [keyword1, keyword2, keyword3, ...]
```

---

## Test Execution

### Test Runner

```bash
./harness/run-test.sh \
    --structure <structure-name> \
    --question <question-id> \
    --loading <classic|adddir> \
    --results-dir <output-path>
```

### Matrix Tests

Full matrix tests run all combinations:
- Questions × Structures × Loading Methods

Example: 23 questions × 2 structures × 2 methods = 92 tests

### Output Format

Each test produces a JSON file containing:
- Question and expected answer
- Model response
- Token usage statistics
- Timing information
- Cost data

---

## Evaluation Criteria

### Correctness

Answers are evaluated against ground truth:

1. **Exact match**: Response contains expected answer exactly
2. **Partial credit**: Response contains key terms from acceptable variants
3. **Incorrect**: Neither exact nor partial match

### Metrics

- **Accuracy**: Percentage of correct answers
- **Token efficiency**: Input/output tokens per question
- **Cost**: USD per test run
- **Latency**: Response time in milliseconds

---

## Corpus Scaling

| Version | Words | Estimated Tokens | Haiku Limit (200K) | Sonnet Limit (200K) |
|---------|-------|------------------|--------------------|--------------------|
| V4 | 120K | ~160K | ✓ Fits | ✓ Fits |
| V5 | 302K | ~400K | ✗ Exceeds | ✗ Exceeds |
| V6 | 622K | ~830K | ✗ Exceeds | ✗ Exceeds |

**Note**: Monolith structure only viable for V4. V5/V6 require split structures.

---

## Reproduction

### Prerequisites

- Claude Code CLI
- jq for JSON processing
- Python 3.8+ for analysis scripts

### Running Tests

```bash
# Single question test
./harness/run-test.sh --structure flat-v5 --question NAV-001 --loading classic

# Full matrix for one variant
./harness/run-haiku-matrix-v5-no-monolith.sh

# Enhancement tests (failed questions only)
./harness/run-v5-enhancement-tests.sh v5.3 deep-v5

# Full enhancement matrix
./harness/run-v5.5-full-matrix.sh
```

### Analysis

```bash
# Cost analysis
python harness/cost-analyzer.py results/v5/raw --output results/v5/analysis

# Generate report
python harness/evaluator.py results/v5/raw --output results/v5/report.md
```

---

*Document created: 2026-01-30*
*Last updated: 2026-01-30*
