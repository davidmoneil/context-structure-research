---
type: claude-knowledge
source: aiprojects
source_path: ".claude/agent-output/results/plex-troubleshoot/2025-12-11_test.md"
source_category: "discovery-plex-troubleshoot"
synced: 2026-02-17
title: "Plex Troubleshooting Report"
tags:
  - claude-knowledge
  - discovery-plex-troubleshoot
---

# Plex Troubleshooting Report

**Date**: 2025-12-11 16:43:00
**Issue**: test (full diagnostic)
**Status**: Healthy (with minor warnings)

## Summary

Plex Media Server on MediaServer (Windows) is running normally. All core services are active, port 32400 is accessible, and external connectivity to plex.tv is working. Some non-critical errors were found related to an orphaned metadata item (ID 123289, "Zootopia").

## Findings

### Service Status
- **Plex Media Server**: Running (PID 23696, CPU: 3,079.86s, Memory: ~524MB)
- **Plex DLNA Server**: Running (PID 24492)
- **Plex Tuner Service**: Running (PID 23900)
- **Plex Update Service**: Running (PID 15940)
- **PlexScriptHost**: 3 instances running (PIDs 16392, 23400, 24404)

### Log Analysis
**Recent Errors Found**: 8 errors in the last ~10 minutes, all related to the same issue:
- `LPE: unknown item 123289`
- `Versions: failed to generate query for path library://858431ec-28b5-413e-a9b5-5df7589397cf/item/%2Flibrary%2Fmetadata%2F123289`
- `Versions: generator Zootopia has an empty version set query, assuming generator is no longer valid`

These errors occur every 5 minutes during background processing queue (BPQ) runs.

**Other Activity**:
- EPG purging working normally
- Client connections from 192.168.1.196 (AIServer) successful
- davidmoneil user token authentication working

### Resources
| Resource | Value | Status |
|----------|-------|--------|
| C: Drive Free | 234.2 GB | OK |
| C: Drive Used | 696.6 GB | OK |
| D: Drive Free | 299.2 GB | OK |
| D: Drive Used | 632.4 GB | OK |
| Plex Memory | ~524 MB | Normal |
| Transcode Cache | Present (Detection, Sessions folders) | OK |

### Database
| Database | Size | Last Modified | Status |
|----------|------|---------------|--------|
| library.db | 714.9 MB | 2025-12-11 16:09 | Active |
| library.blobs.db | 783.8 MB | 2025-12-11 02:01 | Active |
| dlna.db | 3.8 MB | 2025-12-04 | OK |
| epg.cloud.db | 55.8 MB | 2025-12-11 16:32 | Active |

**Lock Files Present**: Yes (db-shm and db-wal files exist)
- This is **normal** for active databases - indicates WAL mode is enabled
- Backups present from Dec 2, 5, 8, 11 (automatic rotation working)

### Network Connectivity
| Test | Result |
|------|--------|
| localhost:32400 | **Connected** (TCP test succeeded) |
| plex.tv:443 | **Connected** (external access working) |

### Centralized Logging (Loki)
- **Status**: Loki initializing ("Ingester not ready: waiting for 15s after being ready")
- **Note**: Plex job may not be configured in Alloy on MediaServer
- Labels present include: job, host, level, service_name, container

## Root Cause

**No critical issues found.** The recurring errors about item 123289 indicate an orphaned metadata reference for "Zootopia" in the library. This is a minor data inconsistency that doesn't affect Plex operation but generates log noise.

## Actions Taken

**Diagnostics Only** (readonly mode) - No changes made:
1. Verified all Plex services running
2. Confirmed port 32400 accessible
3. Reviewed recent logs for errors
4. Checked disk space and database health
5. Tested external connectivity

## Recommendations

### Low Priority
1. **Clean up orphaned metadata** (Optional):
   - Open Plex Web > Settings > Troubleshooting > Optimize Database
   - This may resolve the "unknown item 123289" errors
   - Alternatively, manually locate and remove the "Zootopia" item if it's corrupted

2. **Verify Plex log forwarding to Loki**:
   - Check Grafana Alloy configuration on MediaServer
   - Ensure `job="plex"` label is configured for Plex logs
   - Reference: `http://192.168.1.179:12345` (Alloy UI)

### Monitoring
- The BPQ errors repeat every 5 minutes but don't indicate a functional problem
- If "Zootopia" playback works, the errors can be safely ignored

## Prevention

- Run "Optimize Database" periodically (monthly) to clean orphaned references
- Monitor disk space on C: drive (currently 25% free)
- Keep Plex Media Server updated via Plex Update Service

## Related Resources

- Plex Support: https://support.plex.tv
- Plex Log Location: `C:\Users\MediaServer\AppData\Local\Plex Media Server\Logs\`
- Grafana Logs: https://log.theklyx.space (query: `{job="plex"}`)
- Alloy UI (MediaServer): http://192.168.1.179:12345
