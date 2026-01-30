# Phase 2: Real Codebase Testing

**Status**: Proposed
**Created**: 2026-01-30

---

## Why This Matters

Phase 1 tested synthetic prose (corporate documentation). But Claude Code's primary use case is **code navigation and modification**. Code has fundamentally different characteristics:

| Aspect | Prose (Phase 1) | Code (Phase 2) |
|--------|-----------------|----------------|
| Structure | Topic-based | Syntax-based (imports, classes, functions) |
| Relationships | Conceptual | Call hierarchies, dependencies |
| Navigation | "Find info about X" | "Where is X defined? What calls X?" |
| Answers | Text passages | File paths, line numbers, code snippets |

**Key Question**: Do the Phase 1 findings (flat structure wins, skip indexes) apply to code?

---

## Research Questions

### Primary Questions

1. **Structure validation**: Does flat structure outperform nested for code repos?
2. **Indexing strategies**: Can function/class indexes improve code navigation?
3. **Scale limits**: At what codebase size does accuracy degrade significantly?

### Secondary Questions

4. **Language differences**: Do Python, TypeScript, Go, etc. behave differently?
5. **Architecture awareness**: Does documenting high-level architecture help?
6. **CLAUDE.md optimization**: What should a CLAUDE.md contain for code repos?

---

## Proposed Indexing Strategies

### Strategy A: Function Index

Generate a file listing all function/method names with locations:

```markdown
# Function Index

## Authentication
- `validateToken(token)` → src/auth/validator.ts:45
- `refreshSession(user)` → src/auth/session.ts:102
- `hashPassword(plain)` → src/auth/crypto.ts:23

## API
- `handleRequest(req, res)` → src/api/router.ts:15
- `parseBody(raw)` → src/api/parser.ts:67
...
```

**Generation**: Use AST parsing (tree-sitter, TypeScript compiler API, etc.)

### Strategy B: Class/Type Map

Document class hierarchies and key types:

```markdown
# Type Map

## Core Models
- `User` (src/models/user.ts) - implements Serializable
  - `id: string`
  - `email: string`
  - `roles: Role[]`
  - `authenticate()`, `serialize()`

## Services
- `AuthService` (src/services/auth.ts)
  - depends on: UserRepository, TokenService
  - methods: `login()`, `logout()`, `verify()`
...
```

### Strategy C: Dependency Graph

Map import relationships:

```markdown
# Dependency Graph

## src/api/router.ts
imports:
  - src/auth/middleware.ts (authMiddleware)
  - src/services/user.ts (UserService)
  - src/utils/logger.ts (log)
imported by:
  - src/index.ts
  - tests/api.test.ts
```

### Strategy D: Architecture Summary

High-level component documentation:

```markdown
# Architecture Overview

## Layers
1. **API Layer** (src/api/) - Express routes, request handling
2. **Service Layer** (src/services/) - Business logic
3. **Data Layer** (src/repositories/) - Database access
4. **Utilities** (src/utils/) - Shared helpers

## Key Flows
- Authentication: router → authMiddleware → AuthService → UserRepository
- Order Processing: router → OrderService → PaymentService → OrderRepository
```

### Strategy E: Combined

All strategies together. Test if combination helps or creates noise (like Phase 1 showed).

---

## Proposed Test Codebases

### Selection Criteria

1. **Open source** - Publicly available, reproducible
2. **Well-architected** - Clear structure, good practices
3. **Documented** - Has existing docs (can create ground-truth questions)
4. **Active** - Recent commits, maintained
5. **Varied languages** - Test generalization

### Candidate Repos

| Repo | Size | Language | Why |
|------|------|----------|-----|
| **Small (~50K LOC)** | | | |
| express | ~20K | JavaScript | Ubiquitous, well-known |
| fastapi | ~30K | Python | Modern, typed |
| gin | ~25K | Go | Different paradigm |
| **Medium (~200K LOC)** | | | |
| next.js | ~150K | TypeScript | Complex build system |
| django | ~200K | Python | Batteries-included |
| **Large (~500K+ LOC)** | | | |
| vscode | ~1M+ | TypeScript | Massive, well-organized |
| kubernetes | ~2M+ | Go | Enterprise scale |

### Alternative: Use AIProjects

Test on your own infrastructure:
- Already familiar with the codebase
- Can create accurate ground-truth questions
- Practical validation of findings

---

## Question Types for Code

### Location Questions (like NAV)
- "Where is the authentication middleware defined?"
- "What file contains the User model?"
- "Where are API routes configured?"

### Implementation Questions (like DEPTH)
- "How does the caching layer invalidate entries?"
- "What happens when a request fails authentication?"
- "How are database connections managed?"

### Dependency Questions (new type)
- "What functions call `validateToken`?"
- "What does `OrderService` depend on?"
- "What would break if I modify `User.serialize()`?"

### Cross-Cutting Questions (like XREF)
- "How do errors propagate from the API layer to the frontend?"
- "What's the data flow from user input to database storage?"
- "How is logging configured across the application?"

### Modification Questions (practical use case)
- "What files need to change to add a new API endpoint?"
- "How would I add a new field to the User model?"
- "What tests would I need to update if I change the auth flow?"

---

## Index Generation Approach

### Option 1: AST-Based (Accurate but Complex)

Use language-specific parsers:
- TypeScript: `ts-morph`, TypeScript compiler API
- Python: `ast` module, tree-sitter
- Go: `go/ast` package

**Pros**: Accurate, handles edge cases
**Cons**: Language-specific, complex setup

### Option 2: AI-Assisted (Simpler but Potentially Noisy)

Use Claude (Haiku) to analyze files and extract:
- Function signatures
- Class definitions
- Key relationships

**Pros**: Language-agnostic, handles patterns
**Cons**: May miss things, costs money

### Option 3: Hybrid

- AST for structure (function names, class names)
- AI for semantics (what does this function do?)

### Proposed Implementation

```bash
# Generate function index for a repo
./harness/generate-code-index.sh \
  --repo ~/Code/my-project \
  --strategy function-index \
  --output my-project-index.md

# Test different index strategies
./harness/run-code-matrix.sh \
  --repo ~/Code/my-project \
  --strategies "baseline,function-index,class-map,combined" \
  --questions harness/code-questions.json
```

---

## Ground Truth Generation

### Challenge
Unlike synthetic corpus, we can't pre-define "correct" answers for arbitrary codebases.

### Approaches

1. **Manual creation**: Write questions with known answers for specific repos
2. **AI-assisted verification**: Have Claude verify its own answers against code
3. **Automated checks**: For location questions, verify file/line exists
4. **Expert review**: Have someone familiar with repo validate answers

### Proposed Process

1. Select test repo
2. Manually create 20-30 ground-truth questions with verified answers
3. Run tests across index strategies
4. Score against ground truth
5. Qualitative review of failures

---

## Success Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Location accuracy** | Can find the right file | >95% |
| **Implementation accuracy** | Correctly describes how code works | >85% |
| **Dependency accuracy** | Correctly identifies relationships | >80% |
| **Modification accuracy** | Suggests correct files to change | >75% |

---

## Timeline (Proposed)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 2a. Complete V6 data | 1 day | shallow-v6, very-deep-v6 results |
| 2b. Select test repos | 1 day | 3 repos chosen, cloned |
| 2c. Create questions | 2 days | 20-30 questions per repo |
| 2d. Build index generators | 3 days | Scripts for strategies A-E |
| 2e. Run test matrix | 2 days | Results across all strategies |
| 2f. Analyze and report | 2 days | Phase 2 findings |

---

## Open Questions

1. **How many repos?** Start with 1-2 or go broad with 5+?
2. **Which languages?** Focus on TypeScript/Python or include Go/Rust?
3. **Index depth?** Just function names, or include docstrings/comments?
4. **Codebase familiarity?** Test on repos we know vs. unfamiliar ones?
5. **Cost budget?** How many tests can we run before $$$ becomes a factor?

---

## Next Steps

1. [ ] Complete V6 extended tests (shallow, very-deep)
2. [ ] Decide: proceed with Phase 2 or publish Phase 1 first?
3. [ ] If Phase 2: select first test repo
4. [ ] If Phase 2: build function index generator prototype

---

*Draft created: 2026-01-30*
