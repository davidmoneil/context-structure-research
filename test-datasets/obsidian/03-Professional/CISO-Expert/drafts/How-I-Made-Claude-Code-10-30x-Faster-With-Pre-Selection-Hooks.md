---
title: "How I Made Claude Code 50x Faster With Pre-Selection Hooks"
type: post
status: draft
date: 2026-02-04
source: cisoexpert.com
tags: [ai, claude-code, productivity, development, optimization, hooks]
version: 1
version_history:
  - v1: "2026-02-10 - Backfill versioning (original content)"
---

# How I Made Claude Code 50x Faster With Pre-Selection Hooks

Claude Code v2.1.31 added built-in tool guidance—instructions that tell Claude which tools to prefer for different tasks. After analyzing my own implementation, I discovered something interesting: **my hook-based approach outperforms the built-in feature**.

Here's why timing matters more than instructions.

## The Problem With Post-Selection Guidance

Claude Code's built-in tool guidance works like this: it embeds preferences in Claude's system prompt. "Use Grep for pattern matching." "Use Read for specific files." "Prefer Glob over Bash find."

This is *post-selection* guidance. Claude sees the instructions, but by the time it chooses a tool, those instructions are just background knowledge competing with the immediate task.

**Pre-selection guidance** works differently. It intercepts the decision *before* Claude commits to a tool choice, with full context about what's being asked.

## The Three-Layer Architecture

I built a multi-layer hook system that operates at different points in Claude's decision pipeline:

```
USER PROMPT: "Where is the validateDocker function defined?"
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: UserPromptSubmit (prompt-enhancer.js)            │
│  Detects "where...defined" pattern                         │
│  Injects: "Use LSP tool for code navigation (50ms vs 45s)" │
│  Status: SOFT GUIDANCE                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: PreToolUse (lsp-redirector.js)                   │
│  Claude chose Grep anyway? Intercept it.                   │
│  Returns: proceed: false + redirect message                │
│  Status: HARD BLOCK                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: PreToolUse (mcp-enforcer.js)                     │
│  Tracks bash vs MCP usage patterns                         │
│  Suggests alternatives with cooldown                       │
│  Status: ADVISORY                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
TOOL EXECUTION: LSP(operation: "goToDefinition", ...)
Result: 50ms instead of 45+ seconds
```

## Layer 1: Prompt Enhancement

The first hook fires on `UserPromptSubmit`—before Claude even starts reasoning about which tool to use.

```javascript
const ENHANCEMENT_RULES = [
  {
    id: 'lsp-navigation',
    patterns: [
      /\b(go\s*to|find|show|where)\s+(the\s+)?(definition|implementation)\s+(of|for)\b/i,
      /\bwhere\s+.{1,50}\s+(is\s+)?defined\b/i,
      /\b(find|show)\s+(all\s+)?(references?|usages?)\s+(of|to|for)\b/i,
    ],
    context: `**LSP Guidance**: For code navigation, use the LSP tool.
    LSP is ~50x faster (50ms vs seconds) and provides semantic accuracy.`
  }
]
```

When Claude receives the prompt "Where is validateDocker defined?", the hook:
1. Matches the pattern `/where\s+.{1,50}\s+defined/i`
2. Injects guidance via `additionalContext`
3. Claude sees the guidance *as part of the request context*

This is fundamentally different from buried system prompt instructions.

## Layer 2: Hard Redirect

Sometimes Claude ignores the guidance. Layer 2 catches these cases.

```javascript
// Only process Search and Grep tools
if (!['Search', 'Grep'].includes(toolName)) {
  return { proceed: true };
}

// Check if the pattern looks like navigation
const isNavigationQuery = NAVIGATION_PATTERNS.some(
  regex => regex.test(pattern)
);

if (isNavigationQuery && isLspSupportedPath) {
  return {
    proceed: false,  // BLOCK the Grep call
    message: `Use LSP instead. LSP is 50x faster (~50ms vs seconds).
    
    Example: LSP(operation: "goToDefinition", filePath: "...", line: X, character: Y)`
  };
}
```

When a hook returns `proceed: false`, Claude Code stops the tool execution and shows Claude the redirect message. Claude then retries with the recommended approach.

## Layer 3: Advisory Tracking

The third layer handles MCP (Model Context Protocol) optimization—encouraging structured API calls over raw bash commands:

```javascript
const MCP_ALTERNATIVES = {
  'docker ps': { mcp: 'mcp__docker-mcp__list-containers' },
  'docker logs': { mcp: 'mcp__docker-mcp__get-logs' },
  'git status': { mcp: 'mcp__git__git_status' },
  'cat ': { mcp: 'mcp__filesystem__read_text_file' },
};
```

This layer is advisory—it suggests MCP alternatives but doesn't block execution. It tracks usage patterns for later analysis.

## Performance Impact

| Scenario | Built-in Guidance | Hook-Based |
|----------|------------------|------------|
| Code navigation | May use Grep (45+ sec) | LSP (50ms) |
| Reference lookup | Text search | Semantic search |
| Docker status | Bash parsing | Structured JSON |

The 50x improvement for code navigation isn't theoretical. LSP (Language Server Protocol) provides semantic understanding of code—it knows where functions are defined, not just where the text "validateDocker" appears.

## Why This Matters for Security Teams

If you're building AI-assisted security workflows—threat hunting, log analysis, configuration review—tool selection directly impacts both speed and accuracy.

**Speed**: A 45-second search that becomes 50ms means your analysts aren't waiting. At scale, these delays compound.

**Accuracy**: LSP finds where `validateToken` is *defined*, not every file that mentions it. Grep finds the string "validateToken" everywhere—definitions, calls, comments, documentation.

For incident response, the difference between semantic search and text search can be critical.

## Implementation Details

### Fail-Open Design

Every hook uses fail-open error handling:

```javascript
main().catch(err => {
  console.error(`[hook] Error: ${err.message}`);
  console.log(JSON.stringify({ proceed: true }));  // Allow on error
});
```

If a hook crashes, Claude continues normally. No workflow interruption.

### Cooldown Mechanism

To prevent suggestion fatigue, the MCP enforcer throttles advice:

```javascript
const SUGGESTION_COOLDOWN = 60000; // 1 minute

function shouldSuggest() {
  const now = Date.now();
  if (now - lastSuggestionTime > SUGGESTION_COOLDOWN) {
    lastSuggestionTime = now;
    return true;
  }
  return false;
}
```

### Hook Registration

Hooks are registered in Claude Code's settings:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "node .claude/hooks/prompt-enhancer.js"
      }]
    }],
    "PreToolUse": [{
      "matcher": "Grep",
      "hooks": [{
        "type": "command", 
        "command": "node .claude/hooks/lsp-redirector.js"
      }]
    }]
  }
}
```

## Comparison: Built-in vs Hook-Based

| Capability | Built-In | Hook-Based |
|------------|----------|------------|
| Timing | System prompt (static) | Per-request injection |
| Blocking | Cannot block | Can block suboptimal choices |
| Context | Generic | Knows which LSP/MCPs are active |
| Learning | None | Tracks usage patterns |
| Customization | Limited | Fully configurable |

The key insight: **pre-selection guidance with blocking capability** beats **post-selection suggestions**.

## What to Do

1. **Enable hooks** in your Claude Code setup (available since v2.0)
2. **Identify patterns** in your workflow where tool selection matters
3. **Start with soft guidance** (UserPromptSubmit context injection)
4. **Add hard blocks** for high-impact redirects (PreToolUse interception)
5. **Track and iterate** based on actual usage patterns

The hooks are simple JavaScript—pattern matching and JSON responses. Total execution time per hook: 5-15ms.

## The Bottom Line

Claude Code's built-in tool guidance is a good default. But if you're running workflows where tool selection impacts performance or accuracy, consider implementing pre-selection hooks.

The difference between "here's a suggestion buried in your instructions" and "I'm intercepting your choice before you commit" is the difference between guidance and enforcement.

For code navigation specifically, enforcement means 50ms instead of 45 seconds.

---

*Analysis conducted February 2026. Hook implementations available in the AIProjects repository.*
