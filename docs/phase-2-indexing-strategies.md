# Phase 2: Code Indexing Strategies

**Status**: Planning
**Created**: 2026-01-30

---

## Phase 1 Learnings (Context/Prose)

### Key Finding: One Topic = One File

For prose/documentation, the winning strategy was:
- **Flat structure** (all files in one directory)
- **One topic per file** (cohesive content)
- **Descriptive filenames** (includes key entities)
- **Skip enhancement indexes at scale** (hurt accuracy at 600K+)

### Why It Works

| Principle | Benefit |
|-----------|---------|
| One topic per file | Claude can assess relevance from filename alone |
| Flat structure | All filenames visible in single directory listing |
| Descriptive names | Acts as implicit keyword index |
| No separate index | Avoids noise competing for context window |

### Architecture Recommendation (Prose)

```
context/
├── employees-leadership-bios.md      ← topic: leadership team
├── employees-engineering-team.md     ← topic: engineering staff
├── projects-prometheus-overview.md   ← topic: Prometheus project
├── projects-atlas-specifications.md  ← topic: Atlas project
├── financial-q3-2024-report.md       ← topic: Q3 financials
└── policies-ai-ethics.md             ← topic: ethics policy
```

**No _index.md needed** - filenames ARE the index.

---

## Phase 2 Challenge: Code Is Different

Code doesn't follow "one topic per file":

| Aspect | Prose | Code |
|--------|-------|------|
| File = topic? | Yes (usually) | No (multiple functions/classes) |
| Filename descriptive? | "employees-leadership.md" | "utils.ts", "helpers.py" |
| What you're finding | "Info about X" | "Where X is defined", "What calls X" |
| Relationships | Conceptual | Imports, calls, inheritance |

---

## Proposed Indexing Strategies

### Strategy A: Architecture-Only (Minimal)

High-level pointers, no function detail.

```markdown
# CLAUDE.md

## Architecture
- **Authentication**: src/auth/ - JWT validation, sessions, password hashing
- **API Layer**: src/api/ - Express routes, middleware, request handling
- **Data Layer**: src/repositories/ - Database queries, ORM models
- **Utilities**: src/utils/ - Shared helpers, logging, config

## Key Patterns
- All routes go through src/api/router.ts
- Database access only via repositories (never direct SQL in handlers)
- Auth middleware applied globally in src/api/middleware/auth.ts
```

**Pros**: Minimal maintenance, points Claude to right area
**Cons**: No function-level guidance, relies on Claude exploring

**Best for**: Well-structured codebases with clear naming conventions

---

### Strategy B: File + Keywords

Like Phase 1 prose approach, but for code files.

```markdown
# _index.md

## src/auth/
- validator.ts → JWT, token validation, expiry checking, authentication
- session.ts → session management, refresh tokens, logout
- crypto.ts → password hashing, bcrypt, encryption

## src/api/
- router.ts → route registration, middleware chain, request handling
- parser.ts → body parsing, JSON, multipart, validation
```

**Pros**: Familiar pattern from Phase 1, moderate maintenance
**Cons**: Keywords describe file, not individual functions

**Best for**: Codebases where files are topically cohesive

---

### Strategy C: File + Functions + Keywords

Granular index with function-level detail.

```markdown
# code-index.md

## src/auth/validator.ts
Functions:
- `validateToken(token)` → JWT verification, token expiry, auth check
- `refreshSession(user)` → session renewal, token refresh
- `isExpired(token)` → expiry checking, timestamp validation

Keywords: authentication, security, JWT, session management

## src/auth/crypto.ts
Functions:
- `hashPassword(plain)` → bcrypt hashing, salt generation
- `verifyPassword(plain, hash)` → password comparison, timing-safe
- `generateSalt(rounds)` → salt generation, bcrypt rounds

Keywords: cryptography, password security, hashing
```

**Pros**: Maximum precision, Claude knows exactly where to look
**Cons**: High maintenance, index can become huge, may add noise

**Best for**: Complex codebases, or when precision matters more than maintenance

---

### Strategy D: Entry Points Only

Index only the key starting points for common tasks.

```markdown
# entry-points.md

## Common Tasks

### Add a new API endpoint
1. `src/api/routes/index.ts` → register route
2. `src/api/handlers/` → create handler function
3. `src/api/validators/` → add request validation

### Modify authentication
1. `src/auth/middleware.ts` → auth middleware (entry point)
2. `src/auth/validator.ts` → token validation
3. `src/config/auth.ts` → auth configuration

### Add a database model
1. `src/models/index.ts` → register model
2. `src/repositories/` → create repository
3. `src/migrations/` → add migration
```

**Pros**: Task-oriented (matches how developers think), minimal maintenance
**Cons**: Doesn't help with "where is X" questions, only "how do I do X"

**Best for**: Onboarding, task-oriented queries

---

### Strategy E: Semantic Grouping

Group by capability, not file location.

```markdown
# capabilities.md

## Authentication & Authorization
Files: src/auth/*, src/middleware/auth.ts
Key functions:
- validateToken() → src/auth/validator.ts:45
- checkPermission() → src/auth/permissions.ts:23
- authMiddleware() → src/middleware/auth.ts:12

## Data Persistence
Files: src/repositories/*, src/models/*
Key functions:
- UserRepository.findById() → src/repositories/user.ts:34
- OrderRepository.create() → src/repositories/order.ts:56

## API Surface
Files: src/api/*
Key functions:
- handleRequest() → src/api/router.ts:15
- validateBody() → src/api/validators/base.ts:8
```

**Pros**: Logical grouping, matches mental model
**Cons**: Requires understanding of codebase to create, overlapping categories

**Best for**: Large codebases with clear domain boundaries

---

## Combination Strategies

### Combo 1: Architecture + Entry Points (Low Maintenance)

```markdown
# CLAUDE.md

## Architecture
[Strategy A content]

## Common Tasks
[Strategy D content]
```

**Rationale**: High-level orientation + task guidance, no function-level maintenance.

---

### Combo 2: File Keywords + Semantic Groups (Medium Maintenance)

```markdown
# _index.md
[Strategy B - file-level keywords]

# capabilities.md
[Strategy E - semantic groupings for key domains]
```

**Rationale**: File index for navigation, capability groups for conceptual understanding.

---

### Combo 3: Full Index + Entry Points (High Precision)

```markdown
# code-index.md
[Strategy C - full function index]

# tasks.md
[Strategy D - entry points for common tasks]
```

**Rationale**: Maximum precision for "where is X" + task guidance for "how do I do X".

---

## Testing Plan

### Test Matrix

| Strategy | Index Size | Maintenance | Test Priority |
|----------|------------|-------------|---------------|
| A. Architecture-only | Small | Low | 1 (baseline) |
| B. File + keywords | Medium | Medium | 2 |
| C. File + functions + keywords | Large | High | 3 |
| D. Entry points | Small | Low | 4 |
| E. Semantic groups | Medium | Medium | 5 |
| Combo 1 (A+D) | Small | Low | 6 |
| Combo 2 (B+E) | Medium | Medium | 7 |

### Question Types to Test

1. **Location**: "Where is the authentication middleware?"
2. **Implementation**: "How does token validation work?"
3. **Dependency**: "What calls validateToken()?"
4. **Modification**: "What files change to add a new endpoint?"
5. **Cross-cutting**: "How do errors propagate to the frontend?"

### Candidate Test Codebases

| Repo | Size | Language | Why |
|------|------|----------|-----|
| AIProjects | ~10K | Mixed | Familiar, can create accurate ground truth |
| fastapi | ~30K | Python | Well-structured, good docs |
| express | ~20K | JavaScript | Ubiquitous, simple architecture |

---

## Open Questions

1. **Auto-generation**: Can we use AST parsing to auto-generate Strategy C indexes?
2. **Staleness**: How do we keep indexes updated as code changes?
3. **Threshold**: At what codebase size does each strategy break down?
4. **Language differences**: Do Python/TypeScript/Go need different strategies?

---

## Next Steps

1. [ ] Select test codebase (AIProjects recommended - familiar ground truth)
2. [ ] Create baseline (no index) questions and answers
3. [ ] Build Strategy A index (architecture-only)
4. [ ] Build Strategy B index (file + keywords)
5. [ ] Run comparison tests
6. [ ] Decide if Strategy C worth the effort based on B results

---

*Created: 2026-01-30*
