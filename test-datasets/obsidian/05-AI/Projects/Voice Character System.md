---
tags:
  - artifact/item
  - domain/dnd
  - depth/standard
  - domain/ai
  - artifact/character
created: 2026-01-18T14:07
updated: 2026-01-24T10:34
---
# Voice Character System

> D&D Voice Generation for NPCs, Villains, and Narration

## Quick Access

| Interface | URL |
|-----------|-----|
| **Web Dashboard** | [http://192.168.1.196:8200](http://192.168.1.196:8200) |
| **Chatterbox Web UI** | [http://192.168.1.196:8100](http://192.168.1.196:8100) |
| **API Documentation** | [http://192.168.1.196:8200/api](http://192.168.1.196:8200/api) |

## Current Characters

| Character | Role | Tags | Voice Reference |
|-----------|------|------|-----------------|
| **Test Innkeeper** | NPC | innkeeper | None |
| **Wise Elder Sage** | NPC | sage, elder | wise-elder-sage.mp3 |
| **Test Merchant** | NPC | merchant, npc | None |

---

## Role Templates

### Combat & Threats

#### Villain - Menacing
- **Use for**: BBEG, antagonists, threatening NPCs
- **Voice**: Adult, low pitch, slow pace, cold and calculating
- **Emotion**: 0.7 (intense)
- **Sample Lines**:
  - *"Did you really think you could stop me?"*
  - *"Everything proceeds exactly as I planned."*
  - *"[chuckle] How... disappointing."*

### Authority Figures

#### Guard - Gruff
- **Use for**: Town guards, soldiers, watchmen
- **Voice**: Adult male, low pitch, curt and authoritative
- **Emotion**: 0.4
- **Sample Lines**:
  - *"Move along. Nothing to see here."*
  - *"Papers. Now."*
  - *"No weapons in the temple district."*

#### Noble - Haughty
- **Use for**: Arrogant aristocrats, dismissive nobles
- **Voice**: Adult, high pitch, slow pace, condescending
- **Emotion**: 0.45
- **Sample Lines**:
  - *"Must I deal with commoners today?"*
  - *"How... quaint."*
  - *"You may approach... but do not touch anything."*

### Merchants & Services

#### Merchant - Friendly
- **Use for**: Shopkeepers, vendors, traders
- **Voice**: Middle-aged, medium pitch, warm and inviting
- **Emotion**: 0.55
- **Sample Lines**:
  - *"Welcome, welcome! Come see my wares!"*
  - *"For you, my friend, a special price."*

#### Merchant - Shady
- **Use for**: Black market dealers, fences
- **Voice**: Adult male, low pitch, hushed and suspicious
- **Emotion**: 0.4
- **Sample Lines**:
  - *"Looking for something... special?"*
  - *"We never had this conversation, understand?"*

#### Innkeeper - Jovial
- **Use for**: Tavern owners, barkeeps
- **Voice**: Middle-aged, medium pitch, boisterous
- **Emotion**: 0.6
- **Sample Lines**:
  - *"Adventurers! Come in, come in! What'll it be?"*
  - *"Heard the strangest thing the other day..."*

### Wisdom & Youth

#### Elder - Wise
- **Use for**: Sages, mentors, village elders
- **Voice**: Elderly, low pitch, slow pace, thoughtful
- **Emotion**: 0.3
- **Sample Lines**:
  - *"The path you seek... [pause] it is not without danger."*
  - *"Listen well, young ones. I will say this only once."*

#### Child - Excited
- **Use for**: Village children, young NPCs
- **Voice**: Child, high pitch, fast pace, curious
- **Emotion**: 0.7
- **Sample Lines**:
  - *"Wow! Are you a real adventurer?!"*
  - *"Can I hold your sword? Please please please?"*

---

## Narrator Voices

| Type | Use Case | Emotion | Sample |
|------|----------|---------|--------|
| **Dramatic** | Combat, reveals, villain speeches | 0.75 | *"The door creaks open, revealing only darkness..."* |
| **Calm** | Travel, exploration, peaceful | 0.3 | *"Morning sun casts long shadows across the village..."* |
| **Mysterious** | Foreshadowing, prophecies | 0.5 | *"Something stirs in the shadows, watching..."* |
| **Cheerful** | Victories, celebrations | 0.65 | *"The crowd erupts in cheers!"* |

---

## Creating Characters

### Via Web Dashboard
1. Open http://192.168.1.196:8200
2. Click **"+ New Character"** button
3. Fill in: name, background, voice attributes, tags
4. Click **Create Character**

### Via CLI
```bash
# List all characters
voice-char list

# Create new character (interactive)
voice-char create "Character Name"

# Generate voice clip
voice-char generate "Character Name" "Dialogue text" --emotion 0.5

# Check service health
voice-char status
```

## ElevenLabs Workflow

```bash
# Search for matching voice
cd ~/Code/voice-character-system
python3 scripts/generate-voice-reference.py search --gender male --age old

# Create reference from description
python3 scripts/generate-voice-reference.py create "gravelly old sage" \
  --name sage-voice --category male

# Register in voice-char
voice-char voice-ref "Character Name" ./voices/library/male/sage-voice.mp3

# Generate locally (free!)
voice-char generate "Character Name" "Your dialogue here"
```

---

## Audio Samples Location

Generated audio files are stored in:
- `~/Code/voice-character-system/output/`
- Per-project: `~/CreativeProjects/workspaces/{project}/voices/`

## Related Documentation

- [[Voice Registry]] - Full template definitions
- [[Audio Tools Guide]] - Infrastructure documentation
- [[Creative Audio Tools]] - CreativeProjects skill

---

*Last updated: 2026-01-18*
