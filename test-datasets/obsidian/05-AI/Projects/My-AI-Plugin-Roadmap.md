---
type: project-roadmap
project: my-ai-obsidian-plugin
status: complete
created: 2026-02-17
updated: 2026-02-17
version: 2
version_history:
  - v2: "2026-02-17 - All 4 phases complete. 13/13 tasks closed."
  - v1: "2026-02-17 - Initial roadmap defined. 4 phases, 13 tasks."
tags:
  - project/my-ai
  - type/roadmap
  - status/active
---

# My AI Plugin — Roadmap

**AI-powered workspace intelligence for Obsidian**
Context-aware, multi-provider, media-capable

---

## UX Vision

The side panel is the **command center**. It reacts to what you're doing:

- **Select text** → panel shows relevant actions (summarize, expand, classify, create from template)
- **Navigate to a folder** → panel shows persona/context info, available templates for that area
- **Run an action** → panel shows streaming results with options to refine, save, or chain
- **Keyboard shortcuts** → quick access to frequent operations without leaving the editor
- **Context menus** → right-click selected text for AI actions

**Pattern**: detect → suggest → execute → present options → act

---

## Phase 1: Foundation (v0.1.0) — COMPLETE

> Refactor into extensible architecture. No new features — make the code ready to receive them.

### 1.1 Provider Abstraction Layer `[!]` — DONE

Replace hardcoded OpenAI with pluggable providers.

- [x] `AIProvider` interface: `generateText()`, `streamText()`, `isAvailable()`, `getModels()`
- [x] `OpenAIProvider` — extract from current aiService.ts
- [x] `OllamaProvider` — local inference, no API key
- [x] `AnthropicProvider` — Claude API
- [x] `ProviderManager` — registry, routing, per-use-case selection
- [x] Templates can override provider per-file via frontmatter

**Beads**: `AIProjects-ycu` — CLOSED

### 1.2 Settings Overhaul `[!]` — DONE

Go from 1 setting (API key) to full configuration.

- [x] **Providers tab**: Per-provider config (API key, base URL, default model, enabled/disabled)
- [x] **Defaults tab**: Default provider per operation type
- [x] **Folders tab**: Persona mappings (folder path → persona config)
- [x] **Templates tab**: Template folder paths (multiple allowed)
- [x] **General tab**: Debug mode, hotkeys, panel behavior
- [x] **Media tab**: Image provider, Whisper endpoint, Chatterbox endpoint

**Beads**: `AIProjects-48k` — CLOSED

### 1.3 Code Cleanup `[~]` — DONE

- [x] Fix legacy `summarize()` and `generateText()` bypassing `_callOpenAI()`
- [x] Remove dead `createTitle()` method
- [x] Remove `build-template` duplicate stub
- [x] Fix version mismatch (manifest vs package.json)
- [x] Centralize API key validation
- [x] Make `AI_Templates` path configurable

**Beads**: `AIProjects-e85` — CLOSED

### 1.4 Modularize main.ts `[~]` — DONE

Break 654-line god-object into focused modules.

- [x] `src/commands/` — individual command files with consistent pattern
- [x] `src/services/template-manager.ts` — template discovery and parsing
- [x] `src/services/frontmatter-service.ts` — frontmatter operations
- [x] `src/plugin.ts` — slim entry: register commands, load settings

**Beads**: `AIProjects-bcf` — CLOSED

### 1.5 Side Panel v2 — Reactive Foundation `[!]` — DONE

Transform static panel into context-reactive hub.

- [x] Selection listener → panel updates with relevant action buttons
- [x] Action cards: icon, name, description, hotkey hint, cost tier (free/local/cloud)
- [x] Status bar: active persona, current provider, local service health
- [x] Streaming output area with markdown rendering
- [x] Result actions: copy, insert-at-cursor, create-new-note
- [x] Loading states: spinner + cancel button

**Beads**: `AIProjects-0sp` — CLOSED

---

## Phase 2: Intelligence Layer (v0.2.0) — COMPLETE

> Context-aware AI. Knows where you are, what you're working on, adapts accordingly.

### 2.1 Folder-Based Persona System `[!]` — DONE

- [x] Folder→persona mappings via glob patterns (e.g., `01-DnD/*` → Dungeon Master)
- [x] Persona config: name, systemPrompt, preferredProvider, model, temperature, description
- [x] Deepest-match resolution on file navigation
- [x] Side panel persona badge
- [x] Fallback: General Assistant

**Beads**: `AIProjects-6h3` — CLOSED

### 2.2 Context Retrieval `[~]` — DONE

- [x] "Gather Context" command (hotkey-able)
- [x] Scan current folder (configurable depth)
- [x] Extract: frontmatter, first N lines, wiki-links per file
- [x] Build context package: entities, relationships, constraints
- [x] Auto-attach to subsequent AI operations
- [x] Panel: loaded file count, collapsible list, toggle on/off, refresh

**Beads**: `AIProjects-3e9` — CLOSED

### 2.3 Enhanced AI Operations `[~]` — DONE

| Operation | Input | Output | UX |
|-----------|-------|--------|-----|
| Summarize | Selection/note | Concise summary | Replace or insert at top |
| Classify | Full note | Tags + category | Options in panel, click to apply |
| Think/Reason | Selection + question | Extended analysis | Stream to panel |
| Expand | Selection | Elaborated text | Replace selection |
| Suggest Title | Full note | 3 options | Click to apply in panel |

- [x] Context menu: right-click → "My AI" submenu
- [x] Hotkeys: `Ctrl+Shift+S/E/T/C` (configurable)
- [x] All operations use active persona + gathered context

**Beads**: `AIProjects-t68` — CLOSED

### 2.4 Frontmatter Queries `[-]` — DONE

- [x] "Query Notes" command → modal filter builder
- [x] Fields: type, status, tags, any custom key
- [x] Operators: equals, contains, greater than, exists
- [x] Results in panel as clickable list
- [x] "Use as Context" / "Open" buttons

**Beads**: `AIProjects-9si` — CLOSED

---

## Phase 3: Document Standards (v0.3.0) — COMPLETE

> Every document created or modified follows configurable standards.

### 3.1 Document Operations Framework `[~]` — DONE

- [x] Required frontmatter fields per document type
- [x] Naming conventions per folder
- [x] Default folder placement per content type
- [x] Version tracking (auto-increment)
- [x] Advisory warnings in panel (non-blocking)

**Beads**: `AIProjects-67q` — CLOSED

### 3.2 Template System Upgrade `[~]` — DONE

- [x] Multiple template folders
- [x] Template metadata: content type, applicable personas, required inputs
- [x] Smart suggestion by folder/persona
- [x] Preview in panel before creation
- [x] Per-template output config (save location, naming, required frontmatter)
- [x] Guided creation: multi-step input forms

**Beads**: `AIProjects-0ja` — CLOSED

---

## Phase 4: Media Integration (v0.4.0) — COMPLETE

> Image generation, voice synthesis, and audio transcription — all auto-embedded.

### 4.1 Image Generation `[-]` — DONE

DALL-E 3 via OpenAI. Select text/prompt → Generate → Preview in panel → Insert/Save/Regenerate.
Embed format: `![[filename.png|center|400]]`

**Beads**: `AIProjects-tzy` — CLOSED

### 4.2 Voice Generation `[-]` — DONE

Local Chatterbox TTS. Select text → Generate Voice → Configure params or use persona defaults → Preview/play → Embed.
Embed format: `![[filename.wav]]`

**Beads**: `AIProjects-3pa` — CLOSED

### 4.3 Audio Transcription `[-]` — DONE

Local Whisper. File picker → Model/language select → Progress → Timestamped result → Insert/Create Note.
Format: `**[HH:MM:SS]**` markdown

**Beads**: `AIProjects-7df` — CLOSED

---

## Architecture (Target)

```
my-ai/
├── main.ts                          # Slim entry
├── src/
│   ├── plugin.ts                    # Lifecycle, command registration
│   ├── providers/
│   │   ├── types.ts                 # AIProvider interface
│   │   ├── provider-manager.ts      # Registry and routing
│   │   ├── openai-provider.ts
│   │   ├── anthropic-provider.ts
│   │   └── ollama-provider.ts
│   ├── commands/                    # One file per command
│   ├── services/
│   │   ├── template-manager.ts
│   │   ├── frontmatter-service.ts
│   │   ├── context-retriever.ts
│   │   ├── persona-manager.ts
│   │   ├── document-standards.ts
│   │   └── query-engine.ts
│   ├── media/
│   │   ├── image-generator.ts
│   │   ├── voice-generator.ts
│   │   └── transcriber.ts
│   ├── ui/
│   │   ├── side-panel.ts
│   │   ├── action-cards.ts
│   │   ├── result-display.ts
│   │   ├── context-display.ts
│   │   ├── query-modal.ts
│   │   └── template-modal.ts
│   ├── settings.ts
│   └── constants.ts
├── styles.css
├── manifest.json
└── package.json
```

**Providers**: OpenAI, Anthropic, Ollama (pluggable)
**Media**: DALL-E 3 (images), Chatterbox TTS (voice), Whisper (transcription)
**Local-first**: Ollama and local services prioritized

---

## Links

- **Source**: `.obsidian/plugins/my-ai/`
- **GitHub**: [obsidian_my_ai](https://github.com/davidmoneil/obsidian_my_ai)
- **Feature Source**: [[CreativeProjects]] (patterns ported from there)
- **AIProjects Context**: `.claude/context/projects/my-ai-obsidian-plugin.md`
