---
type: claude-knowledge
source: aiprojects
source_path: ".claude/agent-output/results/plex-troubleshoot/2026-02-16_health-check-evening.md"
source_category: "discovery-plex-troubleshoot"
synced: 2026-02-17
title: "Plex Troubleshooting Report"
tags:
  - claude-knowledge
  - discovery-plex-troubleshoot
---

# Plex Troubleshooting Report

**Date**: 2026-02-16 20:03 MST
**Issue**: General health check (evening, automated via n8n)
**Status**: Healthy (minor maintenance recommended)
**Run**: #6

## Summary

Plex Media Server is running well with 2 active streams, good external connectivity, and stable resource usage. WAL files are growing due to 4.5 days of uptime (expected). Orphaned metadata errors persist from previous sessions and should be cleaned up via Empty Trash / Clean Bundles.

## Findings

### Service Status
- PlexUpdateService: Running (Automatic)
- All 7 Plex processes running (started 2/12/2026 5:05 AM)
- System uptime: ~4.5 days (last boot 2/12/2026 5:04 AM)
- Main process CPU: 1805.5 sec cumulative, Memory: 397 MB

### Active Streams (at time of check)
| User | Content | Device | Source |
|------|---------|--------|--------|
| angelad38 | Thunderbolts* (movie, 57min/128min) | Roku (50" Sharp Roku TV) | WAN (38.78.245.118) |
| Chrissy Silvester | The One with Joey's Porsche (S6E5, 11min/22min) | Android (Pixel 7 Pro) | WAN (67.186.201.146) |

### Log Analysis
- Errors (last 5000 lines): 50
- Warnings (last 5000 lines): 8
- **All non-Xbox errors are LPE/Versions orphaned metadata** (known pattern)
- Orphaned items: 119694, 123289, 156192, 156194, 156195, 156196
- No Xbox profile errors in this check (no Xbox clients active)

### Resources
- Disk Space: 242 GB free / 931 GB total (26% free)
- Main Process Memory: 397 MB
- Total Plex Memory: ~658 MB (across 7 processes)
- Transcode Cache: Empty (0 bytes)

### Database
- library.db: 720 MB (last written 7:57 PM today)
- library.db-wal: 728 MB (growing - 4.5 days since last checkpoint)
- blobs.db: 897 MB (last written 2/12 2:12 AM)
- blobs.db-wal: 918 MB (growing - 4.5 days since last checkpoint)
- DLNA db: 4 MB + 4 MB WAL
- EPG db: 54 MB + 1 MB WAL
- Automatic backups: 4 present (Feb 6, 9, 12, 15) - running every 3 days
- Old CORRUPTED db file still present (12/23/2025, 729 MB)
- Lock files (.db-shm): Present (normal for running instance)

### Network
- Port 32400: Listening (8 established connections + 1 FinWait2)
- plex.tv:443: Reachable
- Loki log flow: Active (1000+ entries in 5 minutes)

## Root Cause
N/A - no active issues affecting functionality.

## Actions Taken
- Diagnostics only - no changes made (readonly mode)

## Recommendations

1. **[~] Clean orphaned metadata** - Run Empty Trash and Clean Bundles in Plex Settings > Manage > Troubleshooting to clear LPE errors for items 119694, 123289, 156192, 156194, 156195, 156196

2. **[-] Schedule a restart** - WAL files at ~1.6 GB combined will checkpoint on clean restart. Not urgent but recommended within a few days to keep DB tidy. Last restart was 2/12.

3. **[-] Remove old CORRUPTED db** - `com.plexapp.plugins.library.db-CORRUPTED` (729 MB) from 12/23/2025 can be deleted to reclaim disk space. Verify no longer needed first.

4. **[-] Monitor disk space** - At 26% free (242 GB), adequate for now but worth watching if media library grows significantly.

## Comparison with Previous Checks (2/16)

| Metric | Check #4 (afternoon) | Check #6 (evening) | Trend |
|--------|----------------------|---------------------|-------|
| Memory (main) | ~381 MB | 397 MB | Slight increase (normal) |
| library.db-wal | ~727 MB | 728 MB | Stable |
| blobs.db-wal | ~918 MB | 918 MB | Stable |
| Error count (5k lines) | - | 50 | All orphaned metadata |
| Active streams | 1 (Xbox) | 2 (Roku + Android) | Normal variation |

## Prevention
- Consider weekly Plex restart schedule to keep WAL files in check
- Periodic Empty Trash / Clean Bundles (monthly)

## Related Resources
- Plex Support: https://support.plex.tv
- Log Location: C:\Users\MediaServer\AppData\Local\Plex Media Server\Logs\
- Grafana Logs: {job="plex"} in Loki
