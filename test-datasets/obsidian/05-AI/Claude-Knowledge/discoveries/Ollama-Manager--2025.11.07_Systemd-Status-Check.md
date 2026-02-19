---
type: claude-knowledge
source: aiprojects
source_path: ".claude/agent-output/results/ollama-manager/2025-11-07_systemd_status_check.md"
source_category: "discovery-ollama-manager"
synced: 2026-02-17
title: "Ollama Systemd Service Status Check - Results"
tags:
  - claude-knowledge
  - discovery-ollama-manager
---

# Ollama Systemd Service Status Check - Results
**Date**: 2025-11-07  
**Time**: 12:56:08  
**Service**: ollama.service (systemd) on port 11434  
**Status**: BLOCKED - AIServer unreachable via SSH

## Executive Summary

**CRITICAL FINDING**: The previous agent session (2025-11-07 11:43:29) checked the wrong Ollama instance. It examined the Docker container (ollama_server on port 11433) instead of the production systemd service (ollama.service on port 11434).

This session identified the error and documented the correct service parameters. A full status check requires SSH connectivity to AIServer (192.168.1.196), which is currently unavailable.

## Current System Configuration

### Systemd Service Details (Correct Target)
- **Service Name**: ollama.service
- **API Port**: 11434 (localhost)
- **Binary Location**: /usr/local/bin/ollama
- **Service User**: ollama
- **Model Directory**: /usr/share/ollama/.ollama/models
- **GPU**: AMD Radeon (Device 1586) with ROCm support - DOCUMENTED AS WORKING
- **Status**: Production instance - ACTIVE
- **OpenWebUI Integration**: Connected via host.docker.internal:11434

### Comparison: Two Ollama Instances on AIServer

| Property | Systemd Service | Docker Container |
|----------|-----------------|------------------|
| Service Identifier | ollama.service | ollama_server |
| API Port | 11434 | 11433 |
| GPU Support | AMD ROCm - WORKING | Not working |
| Models | Present | None (per previous check) |
| Production Status | YES - Primary instance | NO - Unused |
| Service Type | systemd | Docker container |
| Binary | /usr/local/bin/ollama | Container image |

## Previous Session Data Analysis

The memory file contains data from Docker container check, NOT systemd service:
- **Container ID**: 4b35617606dc (Docker container hash)
- **Port Referenced**: 11433 (Docker mapped port)
- **GPU Status**: Not detected (Docker container limitation)
- **Models**: None installed (Docker container state)
- **Uptime**: 47 days (Docker container)

**This data is NOT applicable to the systemd service.**

## Connectivity Issue

**Current Blocker**: SSH connection to AIServer (192.168.1.196) failed
- Service may be down, network unavailable, or SSH not responding
- Cannot execute systemd commands or API checks remotely
- Requires investigation/restart of AIServer or network connectivity

## Required Actions for Next Session

When AIServer connectivity is restored, execute these commands:

### Service Status Commands
```bash
# Check systemd service status
systemctl status ollama --no-pager

# Get version
ollama --version

# Check process details
ps aux | grep ollama

# Get service metadata
systemctl show ollama --property=MainPID,MemoryCurrent
```

### API Connectivity Test
```bash
# Test API endpoint (CORRECT PORT: 11434)
curl http://localhost:11434/api/version

# Check if service responds
curl http://localhost:11434/api/tags
```

### Model and Storage Check
```bash
# Check installed models
du -sh /usr/share/ollama/.ollama/models

# List model details
ls -la /usr/share/ollama/.ollama/models/manifests/
```

### GPU and Resource Monitoring
```bash
# Check GPU detection
lspci | grep -i radeon
rocm-smi

# Check resource usage
systemctl show ollama --property=MemoryCurrent,CPUUsageNSec
```

### Recent Activity and Logs
```bash
# Check recent service logs
journalctl -u ollama.service -n 50 --no-pager

# Check for errors
journalctl -u ollama.service -p err --no-pager
```

## Data Correction Required

The memory file at `.claude/agents/memory/ollama-manager/learnings.json` must be updated with:

**Current (INCORRECT - Docker container data)**:
```json
{
  "service_info": {
    "container_id": "4b35617606dc",
    "container_name": "ollama_server",
    "api_endpoint": "http://localhost:11433"
  }
}
```

**Should be (CORRECT - Systemd service data)**:
```json
{
  "service_info": {
    "service_name": "ollama.service",
    "binary_path": "/usr/local/bin/ollama",
    "service_user": "ollama",
    "api_endpoint": "http://localhost:11434",
    "models_directory": "/usr/share/ollama/.ollama/models",
    "gpu_type": "AMD Radeon (Device 1586) with ROCm",
    "gpu_status": "WORKING"
  }
}
```

## Key Learnings

1. **Two Ollama Instances**: AIServer runs both systemd service (production) and Docker container (unused). Critical to distinguish them.

2. **Port Confusion**: Docker maps 11433 externally to 11434 internally. Systemd service runs directly on 11434. This caused previous confusion.

3. **GPU Status**: Systemd service HAS GPU support (AMD ROCm). Docker container does not. Previous session incorrectly concluded GPU was broken.

4. **Correct Monitoring**: Always use `systemctl` commands and port 11434 for this service, never Docker commands or port 11433.

## Recommendations

1. **Immediate**: Restore SSH connectivity to AIServer to complete status check
2. **Documentation**: Clear markers in code/configs distinguishing the two Ollama instances
3. **Monitoring**: Set up separate monitoring for systemd service (not Docker)
4. **Memory Update**: Replace entire memory file with systemd service data once connected
5. **Verification**: After connectivity restored, verify GPU is actually working with `rocm-smi`

## Next Steps

**Status**: BLOCKED pending AIServer connectivity  
**Resume**: When SSH to 192.168.1.196:22 becomes available  
**Action**: Execute all commands listed in "Required Actions" section  
**Deliverable**: Full status report with current model inventory, GPU metrics, and service health
