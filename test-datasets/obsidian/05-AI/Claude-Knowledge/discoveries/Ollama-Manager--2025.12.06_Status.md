---
type: claude-knowledge
source: aiprojects
source_path: ".claude/agent-output/results/ollama-manager/2025-12-06_status.md"
source_category: "discovery-ollama-manager"
synced: 2026-02-17
title: "Ollama Service Status Report"
tags:
  - claude-knowledge
  - discovery-ollama-manager
---

# Ollama Service Status Report

**Generated**: 2025-12-06 21:23:26
**Session**: 2025-12-06_ollama-manager_212221
**Service**: ollama.service (systemd - NOT Docker container)

## Executive Summary

The Ollama systemd service on AIServer is **HEALTHY** and fully operational. The service has been running stably for 10 hours with GPU/ROCm support working perfectly. All 3 installed models are accessible, and the service is actively serving requests from OpenWebUI.

## Service Details

### Status
- **State**: Active (running)
- **Uptime**: 10 hours 10 minutes
- **Started**: 2025-12-06 11:12:47 MST
- **PID**: 2206
- **User**: ollama (system user)

### Version
- **Ollama Version**: 0.9.6
- **Binary Path**: /usr/local/bin/ollama
- **API Endpoint**: http://localhost:11434
- **API Status**: Responding (verified)

### Resource Usage
- **Memory**: 4.6 GB (current) / 5.0 GB (peak)
- **CPU Time**: 1 minute 14 seconds (over 10 hours)
- **System Load**: 0.39, 0.46, 0.41 (1/5/15 min)

## GPU/ROCm Status: WORKING

**Hardware**: AMD Radeon Graphics (Device 1586)

**GPU Configuration**:
- VRAM Available: 63.5 GiB
- ROCm Backend: Loaded successfully
- Library Path: /usr/local/lib/ollama/libggml-hip.so
- GPU Offloading: Enabled and working

**Last Model Load** (qwen2.5:7b-instruct at 13:57:05):
- GPU Layers Offloaded: 29/29 (100%)
- Model Buffer Size: 4.2 GB on GPU
- KV Cache Size: 448 MB on GPU
- Compute Buffer: 492 MB on GPU
- All tensors successfully offloaded to GPU

## Installed Models

| Model | ID | Size | Last Modified |
|-------|----|----- |---------------|
| qwen2.5:7b-instruct | 845dbda0ea48 | 4.7 GB | 4 weeks ago |
| llama2:latest | 78e26419b446 | 3.8 GB | 4 months ago |
| nomic-embed-text:latest | 0a109f422b47 | 274 MB | 4 months ago |

**Currently Loaded**: None (idle state - no models in memory)

## Recent Activity

### API Requests (Last 10 Hours)
- **Last Activity**: 21:18:00 (5 minutes ago)
  - 3 GET requests: /api/version, /api/tags, /api/ps
  - Sources: localhost (127.0.0.1, ::1)

- **Last Inference Session**: 13:58-13:59
  - Multiple POST /api/chat requests
  - Source: 172.18.0.6 (OpenWebUI container)
  - Response times: 4-24 seconds per request
  - All requests returned 200 OK

### Service Logs
- No errors in past 10 hours
- GPU/ROCm loading successfully on model requests
- Service responding normally to all API calls

## OpenWebUI Integration

**Status**: Connected and working

- OpenWebUI container IP: 172.18.0.6
- Connection method: host.docker.internal:11434
- Recent chat completions successful
- Model listing working (verified at 15:46:21)

## Health Assessment

| Component | Status | Details |
|-----------|--------|---------|
| Service | HEALTHY | Running for 10+ hours, no crashes |
| API | HEALTHY | Responding to requests correctly |
| GPU/ROCm | HEALTHY | All layers offloading successfully |
| Models | HEALTHY | All 3 models accessible |
| Memory | HEALTHY | 4.6 GB usage, within normal range |
| Integration | HEALTHY | OpenWebUI successfully using service |

## Recommendations

1. **No immediate action needed** - service is operating normally
2. Consider updating to latest Ollama version (currently on 0.9.6)
3. Monitor GPU memory usage if planning to load multiple models simultaneously
4. Review and potentially remove llama2:latest and nomic-embed-text if not in use (8 GB storage)

## Comparison: Systemd vs Docker Instance

**This Report (Systemd Service)**:
- Port: 11434
- GPU Support: YES (ROCm working)
- Status: Active production instance
- Integration: Connected to OpenWebUI

**Docker Container** (NOT covered in this report):
- Port: 11433
- GPU Support: NO
- Status: Secondary/backup instance
- Integration: None currently

---

**Next Check Recommended**: 7 days (or immediately if issues arise)
**Session Log**: /home/davidmoneil/AIProjects/.claude/agents/sessions/2025-12-06_ollama-manager_212221.md
