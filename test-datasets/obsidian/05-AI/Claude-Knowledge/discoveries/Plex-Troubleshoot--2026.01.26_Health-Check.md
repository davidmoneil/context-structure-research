---
type: claude-knowledge
source: aiprojects
source_path: ".claude/agent-output/results/plex-troubleshoot/2026-01-26_health-check.md"
source_category: "discovery-plex-troubleshoot"
synced: 2026-02-17
title: "Plex Health Check Report"
tags:
  - claude-knowledge
  - discovery-plex-troubleshoot
---

# Plex Health Check Report

**Date**: 2026-01-26 16:48 UTC
**Issue**: General health check
**Status**: HEALTHY (with minor issues)

## Summary

Plex Media Server is running normally with active remote connections. A few minor issues were found: "LPE: unknown item" errors for orphaned metadata entries and a NAT-PMP warning (non-critical).

## Findings

### Service Status
- **Plex Update Service**: Running (Windows service)
- **Plex Media Server**: Running (PID 12652, 289 MB memory)
- **PlexScriptHost**: 3 instances running (handling plugins)
- **Plex DLNA Server**: Running (PID 24304, 32 MB)
- **Plex Tuner Service**: Running (PID 4888, 18 MB)

### Network
- **Port 32400**: Listening on all interfaces (0.0.0.0 and ::)
- **Active connections**: 4 external clients + 2 local connections
- **External connectivity**: plex.tv reachable (TCP test succeeded)
- **Remote access**: Working (connections from external IPs)

### Resources
- **Disk Space (C:)**: 223 GB free of 930 GB total (24% free)
- **Memory**: ~550 MB total for all Plex processes
- **Database size**: ~9.3 GB total

### Database Health
| Database | Size | Status |
|----------|------|--------|
| library.db | 754 MB | Active |
| library.blobs.db | 936 MB | Active |
| dlna.db | 4 MB | Active |
| epg.cloud.db | 56 MB | Active |

**Backups present**: 4 recent library backups (01-16 to 01-25)
**Lock files**: Present (normal during operation)
**Note**: Old corrupted database file exists (`library.db-CORRUPTED` from Dec 23, 2025)

### Log Analysis

**Recent Errors** (20 occurrences at 16:35:16):
- `LPE: unknown item XXXXX` - Orphaned metadata entries
- `Versions: skipping items for generator`: Version query failures
- Items affected: 123289, 119694, 156192, 156194, 156195, 156196

**Warnings**:
- `NAT: PMP, got an error: NATPMP_ERR_RECVFROM` - NAT-PMP not available (normal if using UPnP or manual port forwarding)

### Recent Activity (from logs)
- ViewStateSync: Syncing with plex.tv for 3 users
- EPG updates: Running normally
- Auto-update check: Completed, no updates available (v1.42.2.10156)
- SSDP discovery: Finding devices (Onkyo receiver, Synology NAS)
- Mapping state: "Mapped - Not Published" (expected with manual port forwarding)

## Root Cause

No critical issues found. The "LPE: unknown item" errors indicate orphaned metadata entries in the library database - items that were deleted from disk but still referenced in metadata. This is cosmetic and doesn't affect functionality.

## Actions Taken

- Diagnostics only (readonly mode)
- No modifications made

## Recommendations

### Optional Cleanup (LOW priority)

1. **Clean orphaned metadata**: Run "Empty Trash" in Plex settings or use library "Clean Bundles" to remove orphaned entries

2. **Remove old corrupted database**: Delete `com.plexapp.plugins.library.db-CORRUPTED` to free 764 MB
   ```powershell
   Remove-Item "C:\Users\MediaServer\AppData\Local\Plex Media Server\Plug-in Support\Databases\com.plexapp.plugins.library.db-CORRUPTED"
   ```

3. **Database optimization** (optional): If library becomes sluggish, consider running database optimization
   - Stop Plex
   - Run `Repair-PlexDatabase.exe` from Plex install directory
   - Restart Plex

### NAT Warning
The NAT-PMP error is normal if:
- Your router doesn't support NAT-PMP
- You're using manual port forwarding (recommended)
- UPnP is disabled for security

No action needed unless remote access is broken.

## Prevention

- Library appears healthy - current backup schedule (every 3 days) is appropriate
- Consider running "Empty Trash" after bulk media deletions

## Related Resources
- Plex Support: https://support.plex.tv
- Grafana Logs: https://log.theklyx.space (query: `{job="plex"}`)
- Plex Web UI: http://192.168.1.179:32400/web
