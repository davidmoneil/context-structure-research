---
created: 2026-01-16T15:24
updated: 2026-01-24T10:39
tags:
  - project/kali-scanner
  - status/draft
  - depth/standard
  - domain/dnd
  - domain/ai
---

For Implementation into the CreativeProject 
## Overview

Build a tool for converting audio recordings to text with multi-speaker identification (diarization).

---

## Option A: Cloud API Approach

### Architecture

```
Audio File → Preprocessing → Transcription API → Diarization → Formatted Output
```

### Stack

- **Transcription**: OpenAI Whisper API ($0.006/min)
- **Diarization**: AssemblyAI ($0.008/min total) or Deepgram
- **Orchestration**: n8n workflow or Python script

### Pros

- No local compute needed
- Scales easily
- High accuracy out of the box

### Cons

- Ongoing costs
- Data leaves your network
- Vendor dependency

### Cost Estimate

|Volume|Whisper Only|With Diarization|
|---|---|---|
|10 hrs/month|$3.60|$4.80|
|50 hrs/month|$18|$24|
|100 hrs/month|$36|$48|

---

## Option B: Self-Hosted (Recommended for Home Lab)

### Architecture

```
Audio File → ffmpeg preprocessing → Whisper (local) → pyannote-audio → Output
```

### Stack

- **Transcription**: [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) (CTranslate2 optimized)
- **Diarization**: [pyannote-audio](https://github.com/pyannote/pyannote-audio)
- **Orchestration**: Python script or n8n with code nodes
- **Storage**: Local filesystem or Postgres for metadata

### Docker Compose Skeleton

```yaml
version: '3.8'
services:
  whisper:
    image: onerahmet/openai-whisper-asr-webservice:latest
    ports:
      - "9000:9000"
    environment:
      - ASR_MODEL=large-v3
    volumes:
      - whisper-models:/root/.cache/whisper
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]  # Optional: CUDA acceleration

  # Or use faster-whisper for better performance
  faster-whisper:
    image: fedirz/faster-whisper-server:latest
    ports:
      - "8000:8000"
    environment:
      - WHISPER__MODEL=large-v3
    volumes:
      - ./models:/models

volumes:
  whisper-models:
```

### Python Script Outline

```python
# transcribe_with_speakers.py
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
import torch

def transcribe_with_diarization(audio_path: str) -> dict:
    """
    Transcribe audio and identify speakers.
    
    Returns structured transcript with speaker labels.
    """
    # 1. Load models
    whisper_model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token="YOUR_HF_TOKEN"  # Requires HuggingFace token
    )
    
    # 2. Run diarization (who spoke when)
    diarization = diarization_pipeline(audio_path)
    
    # 3. Run transcription
    segments, info = whisper_model.transcribe(audio_path, beam_size=5)
    
    # 4. Align transcription segments with speaker labels
    transcript = []
    for segment in segments:
        # Find speaker for this time range
        speaker = get_speaker_at_time(diarization, segment.start, segment.end)
        transcript.append({
            "start": segment.start,
            "end": segment.end,
            "speaker": speaker,
            "text": segment.text
        })
    
    return {
        "audio_file": audio_path,
        "duration": info.duration,
        "speakers": list(set(t["speaker"] for t in transcript)),
        "transcript": transcript
    }

def get_speaker_at_time(diarization, start, end):
    """Map time segment to speaker label."""
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if turn.start <= start and turn.end >= end:
            return speaker
    return "UNKNOWN"

# Output format example:
# {
#   "transcript": [
#     {"start": 0.0, "end": 2.5, "speaker": "SPEAKER_00", "text": "Hello, how are you?"},
#     {"start": 2.7, "end": 5.1, "speaker": "SPEAKER_01", "text": "I'm doing well, thanks."},
#   ]
# }
```

### Pros

- Zero ongoing costs (just electricity)
- Data stays local
- Full control over models and processing
- Can run on existing home lab infrastructure

### Cons

- Initial setup complexity
- Requires GPU for reasonable speed (or patience with CPU)
- Model updates are manual

---

## Option C: Hybrid Approach

Use local Whisper for transcription (free), but call a cloud API only for diarization when needed.

---

## n8n Integration Ideas

### Workflow Trigger Options

- Webhook (API call from other apps)
- File watcher on a folder
- Manual trigger with file upload

### Basic n8n Flow

```
[Webhook/File Trigger]
    ↓
[HTTP Request to local Whisper container]
    ↓
[Code Node: Run pyannote or call diarization API]
    ↓
[Format Output (Markdown, JSON, SRT)]
    ↓
[Save to Obsidian vault / Send notification]
```

---

## Output Format Options

### Markdown (for Obsidian)

```markdown
# Meeting Transcript - 2026-01-16

**Duration**: 45:32
**Speakers**: Alice, Bob, Charlie

---

**[00:00:15] Alice:**
Let's get started with the quarterly review.

**[00:00:22] Bob:**
Sure, I've prepared the slides.
```

### SRT (for video subtitles)

```
1
00:00:15,000 --> 00:00:20,500
[Alice] Let's get started with the quarterly review.

2
00:00:22,000 --> 00:00:25,000
[Bob] Sure, I've prepared the slides.
```

### JSON (for programmatic use)

See Python script output above.

---

## Hardware Considerations

For your home lab:

- **CPU-only**: Works but slow (~10x realtime for large-v3)
- **GPU recommended**: NVIDIA with 8GB+ VRAM for large-v3 model
- **RAM**: 16GB+ recommended
- **Storage**: ~3GB for large-v3 model files

---

## Next Steps

1. [ ] Decide: Cloud vs Self-hosted vs Hybrid
2. [ ] If self-hosted: Check GPU availability on home lab servers
3. [ ] Get HuggingFace token for pyannote (free, just requires agreement to terms)
4. [ ] Set up Docker container for Whisper
5. [ ] Build n8n workflow or Python script
6. [ ] Create output template for Obsidian integration

---

## Resources

- [Faster-Whisper GitHub](https://github.com/guillaumekln/faster-whisper)
- [pyannote-audio](https://github.com/pyannote/pyannote-audio)
- [OpenAI Whisper API Docs](https://platform.openai.com/docs/guides/speech-to-text)
- [AssemblyAI Docs](https://www.assemblyai.com/docs)
- [Whisper Docker Images](https://github.com/ahmetoner/whisper-asr-webservice)