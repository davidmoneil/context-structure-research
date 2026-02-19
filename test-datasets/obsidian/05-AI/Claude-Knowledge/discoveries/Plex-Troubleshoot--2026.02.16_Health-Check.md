---
type: claude-knowledge
source: aiprojects
source_path: ".claude/agent-output/results/plex-troubleshoot/2026-02-16_health-check.md"
source_category: "discovery-plex-troubleshoot"
synced: 2026-02-17
title: "Plex Health Check Report"
tags:
  - claude-knowledge
  - discovery-plex-troubleshoot
---

# Plex Health Check Report

**Date**: 2026-02-16 16:42 MST
**Issue**: General health check (run #3 today)
**Status**: HEALTHY (with known minor issues)
**Mode**: Read-only diagnostics
**Session ID**: 2026-02-16_164028

## Summary

Plex Media Server v1.43.0.10492 is running and healthy on MediaServer. All 7 processes are active with ~4.5 days uptime since Feb 12. Active playback confirmed: user wchristian5 watching "Cars" on Xbox One S via WAN (direct play, ~66 min into 116 min movie). Two known non-critical error categories persist: Xbox client profile warnings (cosmetic, 430 entries) and orphaned metadata references for 6 removed items (156 LPE entries). No FATAL errors. No database corruption. No new issues since previous check.

## Findings

### Service Status
- **Plex Media Server**: Running (PID 23276, started 2/12/2026 5:05:20 AM)
- **Plex Version**: v1.43.0.10492-121068a07
- **Platform**: Windows 10, x64 (Gigabyte B660M DS3H DDR4)
- **Uptime**: ~4 days, 11 hours
- **PlexUpdateService**: Running (Windows service, Automatic start)

**All Processes**:

| Process | PID | CPU (s) | Memory (MB) |
|---------|-----|---------|-------------|
| Plex Media Server | 23276 | 1760.8 | 381.9 |
| PlexScriptHost | 23512 | 67.2 | 94.6 |
| PlexScriptHost | 6272 | 45.8 | 56.9 |
| PlexScriptHost | 23532 | 41.0 | 51.3 |
| Plex DLNA Server | 3736 | 62.7 | 31.1 |
| Plex Tuner Service | 3728 | 29.4 | 17.6 |
| Plex Update Service | 14976 | 0.0 | 10.4 |

**Total Plex memory**: ~644 MB (normal range)

### Network
- **Port 32400**: Listening on all interfaces (::)
- **Active connections**: 8 established + 1 FinWait2 (normal during active use)
- **External connectivity**: plex.tv reachable on TCP 443
- **Remote access**: Working (active WAN session from 50.83.32.53)
- **Local monitoring**: AIServer (192.168.1.196) connected

### Active Playback
- **User**: wchristian5 (account 67051534)
- **Content**: "Cars" (ratingKey 337985)
- **Progress**: 3,943s / 6,990s (~56%)
- **Device**: Xbox One S (platform 10.0.26100.6214)
- **Connection**: WAN from 50.83.32.53, TLS + GZIP
- **Type**: Direct play (transcode cache empty)
- **Timeline updates**: Every ~10 seconds, ~8ms response times

### Resources
- **Disk Space (C:)**: 241.6 GB free / 930.8 GB total (26.0% free)
- **Transcode Cache**: Empty (0 files)
- **Main process memory**: 381.9 MB (normal)
- **Database directory total**: ~10.3 GB (includes 4 backups + CORRUPTED file)

### Database Health

| Database | Size (MB) | WAL Size (MB) | Last Modified | Status |
|----------|-----------|---------------|---------------|--------|
| library.db | 720.1 | 727.5 | 2/16 4:40 PM | Active |
| blobs.db | 897.1 | 918.1 | 2/12 2:45 AM | Active |
| dlna.db | 4.0 | 0.0 | 2/12 5:05 AM | Active |
| epg.cloud.db | 53.9 | 1.1 | 2/16 4:31 PM | Active |
| library.db-CORRUPTED | 728.5 | -- | 12/23/2025 | Stale backup |

**Backups**: 4 recent automatic backups (Feb 6, 9, 12, 15) -- 3-day schedule working
**Lock files (.db-shm)**: Present (normal during active operation)
**WAL files**: Large (library: 727 MB, blobs: 918 MB). Will flush on next clean restart.
**Old corrupted backup**: Still consuming 728 MB -- can be safely deleted.

### Log Analysis

**Error counts in current log file**:
- **FATAL**: 0
- **ERROR total**: 878

**Error Breakdown**:

| Category | Count | Severity | Impact |
|----------|-------|----------|--------|
| Xbox client profile missing | 430 | `[-] LOW` | Cosmetic only |
| LPE unknown item / orphaned metadata | 156 | `[~] MEDIUM` | Cosmetic, cleanup recommended |
| Version query failures (tied to LPE) | ~292 | `[-] LOW` | Side effect of orphaned items |

**Xbox Client Profile** (430 entries):
```
ERROR - Unable to find client profile for device; platform=Xbox, platformVersion=10.0.26100.6214, device=Xbox, model=Xbox One S
```
Fires every ~10 seconds during Xbox playback. Does NOT affect direct play.

**Orphaned Metadata** (156 entries):
```
LPE: unknown item 119694
Versions: failed to generate query for path library://858431ec-.../item/.../119694
```
Affected item IDs: 119694, 123289, 156192, 156195, 156196

### Loki Integration
- **Status**: Operational (localhost:3100 responding)
- **Log flow**: ~295 entries per 5m (main stream), ~29 entries per 5m (secondary)
- **ERROR count (last hour)**: 50 (all Xbox profile errors)
- **Non-Xbox errors (last hour)**: 0
- **Known issue**: Use line filter `|~ "ERROR"` instead of label filter for accurate queries

## Root Cause

No critical issues found. Server is operating normally with active remote streaming.

**Persisting minor issues (unchanged from previous checks)**:
1. Xbox One S client profile -- Plex upstream issue, no local fix
2. Orphaned metadata for 6 removed items -- user needs to run cleanup
3. CORRUPTED database backup consuming 728 MB -- can be deleted
4. Alloy log level detection miscategorizes Plex log format

## Actions Taken

- Diagnostics only (readonly mode)
- No modifications made

## Recommendations

### [~] MEDIUM
1. **Clean orphaned metadata**: Run "Empty Trash" and "Clean Bundles" in Plex Web UI
   - Settings > Troubleshooting > Clean Bundles
   - Settings > Troubleshooting > Empty Trash
   - This will eliminate ~448 errors (156 LPE + ~292 version query failures) per log rotation

### [-] LOW
2. **Remove old corrupted database** (free 728 MB):
   ```powershell
   Remove-Item "C:\Users\MediaServer\AppData\Local\Plex Media Server\Plug-in Support\Databases\com.plexapp.plugins.library.db-CORRUPTED"
   ```

3. **Fix Alloy log level detection**: Update Alloy config with regex stage to parse Plex format:
   ```
   Plex format: Feb 16, 2026 15:55:28.321 [138024] ERROR - message
   Regex: \[\d+\]\s+(DEBUG|INFO|WARN|ERROR|FATAL)\s+-
   ```

4. **Xbox profile**: No action needed. Monitor for resolution in future Plex updates.

## Comparison with Previous Health Checks

| Metric | Jan 26 | Feb 16 (AM) | Feb 16 (PM run 2) | Feb 16 (PM run 3) | Trend |
|--------|--------|-------------|--------------------|--------------------|-------|
| Version | 1.42.2 | 1.43.0 | 1.43.0 | 1.43.0 | Stable |
| Disk Free | 223 GB | 241.6 GB | 241.6 GB | 241.6 GB | Stable |
| Plex Memory | 289 MB | 382 MB | 382 MB | 382 MB | Stable |
| library.db | 754 MB | 720 MB | 720 MB | 720 MB | Optimized |
| blobs.db | 936 MB | 897 MB | 897 MB | 897 MB | Optimized |
| Orphaned items | 6 | 6 | 6 | 6 | Not cleaned |
| CORRUPTED file | Present | Present | Present | Present | Not removed |

## Prevention

- Database backup schedule (every 3 days) is working correctly
- Run "Empty Trash" after bulk media changes
- Consider periodic Plex restart to flush WAL files and reset memory
- Remove stale CORRUPTED backup file

## Related Resources
- Plex Support: https://support.plex.tv
- Plex Web UI: http://192.168.1.179:32400/web
- Log Location: `C:\Users\MediaServer\AppData\Local\Plex Media Server\Logs\`
- Grafana Logs: https://log.theklyx.space (query: `{job="plex"}`)
- Alloy UI: http://192.168.1.179:12345
- Agent Memory: `.claude/agents/memory/plex-troubleshoot/learnings.json`
