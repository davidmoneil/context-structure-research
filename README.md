# Context Structure Research

**Empirical testing of how Claude Code handles different `@` file reference structures.**

## Hypothesis

Different hierarchical structures of context files (monolith, flat, shallow, deep, very-deep) affect Claude's ability to:
1. **Navigate** - Locate specific information
2. **Cross-reference** - Synthesize information across multiple files
3. **Deeply understand** - Answer complex questions requiring inference

## Test Corpus: Soong-Daystrom Industries

A fictional company with ~120K words of documentation spanning:
- Company history and milestones
- Organizational structure and departments
- Employee profiles and relationships
- Products, services, and technical specifications
- Projects with teams, timelines, and dependencies
- Policies, procedures, and compliance
- Financial reports and metrics
- Meeting minutes and decisions

## Structure Variants

| Structure | Depth | Description |
|-----------|-------|-------------|
| Monolith | 0 | Single large file with all content |
| Flat | 1 | Many files in root, no hierarchy |
| Shallow | 2 | Category folders with files inside |
| Deep | 3-4 | Multiple nesting levels |
| Very Deep | 5+ | Maximum practical nesting |

## Test Dimensions

- **Structures**: 5 variants
- **Context Load**: 40%, 60%, 80%, 100%
- **Models**: Haiku, Sonnet, Opus
- **Questions**: ~50 per configuration

## Reproduction

See [docs/methodology.md](docs/methodology.md) for full methodology and reproduction instructions.

### Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd context-structure-research

# Run a single test
./harness/runner.sh --structure shallow --load 80 --model haiku --question 1

# Run full test suite
./harness/runner.sh --all

# Analyze results
python harness/evaluator.py results/raw/ --output results/analysis/
```

## Results

See [results/analysis/report.md](results/analysis/report.md) for findings.

## License

MIT

## Attribution

Research conducted using [Claude Code](https://claude.ai/claude-code) by Anthropic.
