# V1 vs V2 Comparison Analysis

## Corpus Sizes

| Version | Words | Tokens | Context % |
|---------|-------|--------|-----------|
| V1 | ~23K | ~32K | 16% |
| V2 | ~40K | ~56K | 28% |

## Overall Performance

| Metric | V1 (23K) | V2 (40K) | Change |
|--------|----------|----------|--------|
| Average Score | 97.68% | 98.41% | **+0.73%** |
| Exact Matches | 217 | 221 | +4 |

## Structure Performance Comparison

| Structure | V1 | V2 | Change |
|-----------|-----|-----|--------|
| flat | **100%** | **100%** | 0% |
| shallow | **100%** | **100%** | 0% |
| monolith | **100%** | 99.02% | **-0.98%** |
| deep | 92.93% | 96.29% | **+3.36%** |
| very-deep | 95.45% | 96.74% | **+1.29%** |

## Question Type Performance

| Type | V1 | V2 | Change |
|------|-----|-----|--------|
| navigation | **100%** | **100%** | 0% |
| cross-reference | 99.10% | 96.94% | **-2.16%** |
| depth | 90.75% | 97.59% | **+6.84%** |

## Key Findings

### 1. Overall Performance Improved
Counter-intuitively, performance at V2 (40K words) was slightly better than V1 (23K). This suggests:
- More context may actually help with complex reasoning questions
- 40K words is still well within comfortable context bounds

### 2. Monolith Showing Early Strain
The monolith structure dropped from 100% to 99.02% - the first sign of potential context pressure affecting single-file approaches.

### 3. Deep Structures Improved
Both `deep` and `very-deep` structures improved significantly (+3.36% and +1.29% respectively). More content may provide better context for navigating hierarchies.

### 4. Cross-Reference Questions Degraded
XREF questions showed a 2.16% drop, suggesting multi-file synthesis becomes harder with more content.

### 5. Depth Questions Improved Dramatically
DEPTH questions improved by 6.84%, indicating that more context actually helps with strategic inference.

## Implications

At 28% context utilization:
- **Structure still doesn't strongly differentiate** - flat, shallow, monolith all perform well
- **Deep structures are viable** - performance improved vs V1
- **Early warning signs for monolith** - first performance drop observed

## Next Steps

1. **Expand to V3 (80K/56% context)** - Test if structure divergence emerges
2. **Expand to V4 (150K+/100% context)** - Test truncation/overflow behavior
3. **Monitor monolith** - Watch for continued degradation

## Cost Summary

| Version | Cost |
|---------|------|
| V1 | $12.38 |
| V2 | $21.06 |
| Total | $33.44 |
