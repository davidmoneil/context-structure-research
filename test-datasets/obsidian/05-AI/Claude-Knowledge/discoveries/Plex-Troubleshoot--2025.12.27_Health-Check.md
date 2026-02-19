---
type: claude-knowledge
source: aiprojects
source_path: ".claude/agent-output/results/plex-troubleshoot/2025-12-27_health-check.md"
source_category: "discovery-plex-troubleshoot"
synced: 2026-02-17
title: "Plex Troubleshooting Report"
tags:
  - claude-knowledge
  - discovery-plex-troubleshoot
---

# Plex Troubleshooting Report

**Date**: 2025-12-27
**Issue**: General health check
**Status**: Healthy with Minor Issues

## Summary

Plex Media Server is running and functional. All core services are operational, port 32400 is accessible, and external connectivity to plex.tv is working. However, there are orphaned metadata references ("unknown item" errors) related to recently removed media items that should be cleaned up.

## Findings

### Service Status
- **Plex Update Service**: Running (Automatic)
- **Plex Media Server**: Running (274 MB memory, started 12/26/2025 10:09 AM)
- **Plex DLNA Server**: Running (31 MB memory)
- **Plex Tuner Service**: Running (18 MB memory)
- **PlexScriptHost**: 3 instances running

### Log Analysis
- **Recent Errors**: 30 errors in last 200 log lines
- **Error Type**: "LPE: unknown item" and "Versions: failed to generate query"
- **Affected Items**:
  - Santa Claus Is Comin' to Town
  - Frosty the Snowman
  - The Little Drummer Boy
  - Rudolph the Red-Nosed Reindeer
  - Zootopia
  - Wallace & Gromit: The Curse of the Were-Rabbit
- **Cause**: Orphaned metadata references - these items were likely removed from the library but metadata references remain

### Resources
- **Disk Space**: 199.29 GB free (731.51 GB used on C:)
- **Transcode Cache**: 2 files (minimal size)
- **Memory Usage**: ~274 MB for main Plex process (normal)

### Database
- **Main Database**: 721.41 MB (last write: 12/27/2025 9:46 AM) - Healthy
- **Blobs Database**: 924.44 MB - Healthy
- **WAL Files**: Present and actively used (normal during operation)
- **Lock Files (.db-shm)**: Present - Normal for running server
- **Backups**: Automatic backups from 12/17, 12/20, 12/23, 12/26 present
- **Note**: CORRUPTED database file exists from 12/23 - appears to be a previous issue that was resolved via restore

### Network
- **Port 32400**: Open and accessible
- **External Connectivity**: plex.tv reachable on port 443

## Root Cause

The "unknown item" errors are caused by orphaned version set generators in Plex. This typically happens when:
1. Media files were removed from the library
2. The library was scanned but the version generators were not cleaned up
3. Plex tries to reference items that no longer exist

This is a cosmetic issue that doesn't affect playback or core functionality.

## Actions Taken
- Diagnostic checks only (read-only mode)
- No modifications made

## Recommendations

### Low Priority - Database Cleanup
Run "Empty Trash" and "Clean Bundles" from Plex settings to remove orphaned metadata:

1. Open Plex Web UI → Settings → Troubleshooting
2. Click "Empty Trash" for all libraries
3. Click "Clean Bundles"
4. Optionally run "Optimize Database"

### Medium Priority - Database Optimization
The library database has accumulated ~728 MB of WAL. Consider:
1. Restart Plex service to commit WAL to main database
2. Run "Optimize Database" from Plex settings

### Housekeeping
The `com.plexapp.plugins.library.db-CORRUPTED` file from 12/23 can be deleted if no longer needed for investigation.

## Prevention
- Run "Empty Trash" after removing media from libraries
- Schedule periodic database optimization (monthly)
- Monitor disk space on C: drive (currently ~21% free)

## Related Resources
- Plex Support: https://support.plex.tv
- Log Location: `C:\Users\MediaServer\AppData\Local\Plex Media Server\Logs\`
- Grafana Logs: https://log.theklyx.space (query: `{job="plex"}`)
