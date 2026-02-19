---
created: 2026-01-16T15:33
updated: 2026-01-24T10:39
tags:
  - artifact/item
  - status/draft
  - depth/deep
  - domain/ai
  - domain/dnd
---


## Overview

Build a system that allows users to:

1. Define character profiles with personality, voice characteristics, and background
2. Auto-generate ElevenLabs voice descriptions from those profiles
3. Create and store voices via the ElevenLabs API
4. Generate dialogue/speech for characters on demand

---

## Phase 1: Core Infrastructure

### 1.1 Project Setup

- [ ] Initialize project (Node.js/TypeScript or Python - your preference)
- [ ] Set up environment configuration for API keys
- [ ] Create basic project structure
- [ ] Set up local database (SQLite for simplicity, or Postgres if you want to use your existing infrastructure)

### 1.2 ElevenLabs API Integration

- [ ] Install ElevenLabs SDK or set up REST client
- [ ] Implement authentication
- [ ] Create wrapper functions for:
    - Voice Design API (create voice from description)
    - Text-to-Speech API (generate audio)
    - Voice Library API (list/manage saved voices)
- [ ] Handle rate limiting and error responses
- [ ] Implement credit usage tracking

**Key API Endpoints:**

```
POST /v1/text-to-voice/create-previews  - Generate voice previews from description
POST /v1/text-to-voice/create-voice-from-preview - Save a preview as a voice
POST /v1/text-to-speech/{voice_id} - Generate speech
GET  /v1/voices - List available voices
```

---

## Phase 2: Character Management

### 2.1 Character Profile Schema

```yaml
Character:
  id: uuid
  name: string
  
  # Personality & Background (for dialogue generation)
  personality_traits: string[]      # e.g., ["nervous", "greedy", "cunning"]
  background: text                  # Brief backstory
  speech_patterns: string[]         # e.g., ["uses old-timey phrases", "stutters when lying"]
  vocabulary_level: enum            # simple, average, educated, archaic
  
  # Voice Characteristics (for ElevenLabs)
  voice_description:
    age: string                     # "elderly", "middle-aged", "young adult"
    gender: string
    accent: string                  # "thick Chinese accent", "mild Southern drawl"
    pitch: string                   # "high", "low", "gravelly"
    pace: string                    # "slow and deliberate", "quick and nervous"
    tone: string                    # "warm", "cold", "raspy", "smooth"
    quirks: string[]                # "occasional cough", "sighs frequently"
  
  # ElevenLabs Integration
  elevenlabs_voice_id: string       # Stored after voice creation
  voice_preview_ids: string[]       # The 3 previews generated
  
  # Metadata
  created_at: timestamp
  updated_at: timestamp
  tags: string[]                    # For organization: "npc", "villain", "shopkeeper"
```

### 2.2 Character CRUD Operations

- [ ] Create character with profile
- [ ] Update character details
- [ ] Delete character (and optionally the ElevenLabs voice)
- [ ] List/search characters by tags, name, etc.
- [ ] Import/export characters (JSON format for portability)

---

## Phase 3: Voice Description Generator

### 3.1 AI-Powered Description Builder

Use Claude API (or local LLM) to transform character profiles into optimized ElevenLabs voice descriptions.

**Input:** Character profile **Output:** 1-2 paragraph voice description optimized for ElevenLabs

**Example Prompt Template:**

```
Given this character profile, generate an ElevenLabs Voice Design description 
(100-300 characters) that captures their voice characteristics.

Character: {name}
Age: {age}
Gender: {gender}
Accent: {accent}
Personality: {personality_traits}
Speech patterns: {speech_patterns}

The description should focus on:
- Physical voice qualities (pitch, tone, texture)
- Accent and regional characteristics  
- Pace and rhythm of speech
- Any vocal quirks or distinctive features

Do NOT include personality or emotional traits - only physical voice characteristics.
```

### 3.2 Voice Creation Workflow

1. User creates/selects character
2. System generates voice description via AI
3. User can edit/refine the description
4. System calls ElevenLabs Voice Design API
5. System plays back 3 preview options
6. User selects preferred voice
7. System saves voice to ElevenLabs library and stores voice_id

---

## Phase 4: Dialogue Generation

### 4.1 Dialogue Generator

Use Claude API to generate in-character dialogue based on:

- Character profile (personality, speech patterns, vocabulary)
- Context/situation provided by user
- Optional: conversation history for multi-turn exchanges

**Example Prompt Template:**

```
You are writing dialogue for this character:

Name: {name}
Personality: {personality_traits}
Background: {background}
Speech patterns: {speech_patterns}
Vocabulary level: {vocabulary_level}

Context: {user_provided_context}

Write a response (1-3 sentences) that this character would say in this situation.
Stay in character. Use their speech patterns and vocabulary level.
Output ONLY the dialogue, no quotation marks or attribution.
```

### 4.2 Text-to-Speech Pipeline

1. User provides context/prompt for what character should say
2. AI generates dialogue text
3. User can edit the dialogue if needed
4. System sends text to ElevenLabs TTS with character's voice_id
5. Audio is returned and played/saved

---

## Phase 5: User Interface Options

### Option A: CLI Tool (Simplest)

```bash
# Create a character
voice-gen character create --name "Grandmother Chen" --interactive

# Generate voice for character
voice-gen voice create --character "Grandmother Chen"

# Generate and speak dialogue
voice-gen speak --character "Grandmother Chen" --context "greeting a customer at her tea shop"
```

### Option B: Web Interface

- Character management dashboard
- Voice preview player
- Dialogue input with audio playback
- Audio file download/export

### Option C: Obsidian Plugin (for D&D integration)

- Read character profiles from Obsidian notes
- Generate voices from within Obsidian
- Play dialogue audio inline
- Store audio files in vault

### Option D: Discord Bot

- Commands to create characters
- Generate dialogue on demand in voice channels
- Great for live D&D sessions

---

## Phase 6: Advanced Features (Future)

### 6.1 Conversation Mode

- Multi-turn dialogue with memory
- Character-to-character conversations
- Scene generation with multiple speakers

### 6.2 Emotion/Mood Modifiers

- Adjust voice delivery based on emotional context
- ElevenLabs v3 supports audio tags: `[sighs]`, `[whispers]`, `[laughs]`
- AI can inject appropriate tags based on context

### 6.3 Batch Generation

- Generate multiple lines at once
- Create "dialogue packs" for common scenarios
- Pre-generate for session prep

### 6.4 Voice Library Management

- Track which voices are stored in ElevenLabs
- Sync local database with ElevenLabs library
- Handle voice slot limits per plan

---

## Technical Considerations

### API Keys Required

- ElevenLabs API key (get from elevenlabs.io dashboard)
- Anthropic API key (for Claude dialogue generation) - or use local LLM

### Cost Estimation

- **Voice Design:** ~100-300 characters per voice creation (minimal)
- **TTS:** ~50-500 characters per dialogue line
- **Starter plan ($5/mo):** ~30,000 credits = ~30,000 characters
- **Rough estimate:** 60-600 dialogue generations per month on Starter

### File Storage

- Audio files: Store locally or in cloud (S3, etc.)
- Consider cleanup policy for old audio files
- Format: MP3 (default) or WAV for higher quality

### Error Handling

- ElevenLabs API rate limits
- Voice generation failures
- Credit exhaustion alerts

---

## Suggested Implementation Order

1. **MVP (1-2 days)**
    
    - Basic ElevenLabs API wrapper
    - Hardcoded character -> voice description
    - Generate speech from text input
    - CLI interface
2. **Core Features (3-5 days)**
    
    - Character profile storage (SQLite)
    - AI-generated voice descriptions
    - AI-generated dialogue
    - Voice creation workflow with preview selection
3. **Polish (2-3 days)**
    
    - Better CLI or simple web UI
    - Audio file management
    - Character import/export
4. **Integration (optional)**
    
    - Obsidian plugin
    - Discord bot
    - Foundry VTT module

---

## Quick Start Commands for Claude Code

```bash
# Initialize the project
mkdir voice-character-system && cd voice-character-system
npm init -y
npm install typescript tsx @types/node dotenv

# Or for Python
python -m venv venv
source venv/bin/activate
pip install elevenlabs anthropic python-dotenv

# Create basic structure
mkdir -p src/{api,models,services,cli}
touch src/index.ts
touch .env.example
```

### Starter .env

```
ELEVENLABS_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

---

## Resources

- [ElevenLabs Voice Design Docs](https://elevenlabs.io/docs/creative-platform/voices/voice-design)
- [ElevenLabs API Reference](https://elevenlabs.io/docs/api-reference)
- [ElevenLabs Node SDK](https://github.com/elevenlabs/elevenlabs-js)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [Anthropic Claude API](https://docs.anthropic.com/en/docs)