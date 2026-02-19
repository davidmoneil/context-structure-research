---
tags:
  - project/kali-scanner
  - depth/standard
  - domain/security
  - domain/mechanics
created: 2026-01-06T07:51
updated: 2026-01-24T10:59
---
# Kali Scanner - OSINT Normalization Pipeline

**Last Updated**: 2026-01-06
**Status**: Operational

## Overview

The Kali Scanner stack normalizes OSINT data from SpiderFoot into a unified PostgreSQL schema for analysis and correlation.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   SpiderFoot    │     │    Normalizer    │     │   PostgreSQL    │
│  (Web UI :5002) │     │   (Python ETL)   │     │ (osint schema)  │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                        │
         │ Run scan via UI       │                        │
         │ ──────────►           │                        │
         │                       │                        │
         │ spiderfoot.db         │                        │
         │ (tbl_scan_instance,   │                        │
         │  tbl_scan_results)    │                        │
         │                       │                        │
         │                       │ Poll every 5 min       │
         │◄──────────────────────│                        │
         │                       │                        │
         │                       │ Normalize + Insert     │
         │                       │ ───────────────────────►
         │                       │                        │
         │                       │   scan_sources,        │
         │                       │   findings,            │
         │                       │   finding_relationships│
```

## Components

| Component | Container | Port | Purpose |
|-----------|-----------|------|---------|
| SpiderFoot | `spiderfoot` | 5002 | OSINT automation tool |
| PostgreSQL | `kali_scanner_db` | 5435 | Normalized findings storage |
| Normalizer | `kali_scanner_normalizer` | - | ETL service (polls every 5 min) |

## Quick Commands

### Start/Stop Stack

```bash
# Start all services
cd ~/Docker/mydocker/kali-scanner
docker compose up -d

# Start only SpiderFoot
docker compose up -d spiderfoot

# Stop all
docker compose down

# View logs
docker logs kali_scanner_normalizer --tail 50 -f
```

### Check Scan Status

```bash
# View recent scans
docker exec kali_scanner_db psql -U kali_scanner -d kali_scanner -c \
  "SELECT * FROM osint.recent_scans;"

# Count findings by type
docker exec kali_scanner_db psql -U kali_scanner -d kali_scanner -c \
  "SELECT finding_type, COUNT(*) FROM osint.findings GROUP BY finding_type ORDER BY COUNT(*) DESC;"

# View high-risk findings (threats)
docker exec kali_scanner_db psql -U kali_scanner -d kali_scanner -c \
  "SELECT * FROM osint.threat_findings LIMIT 10;"

# Check type mappings
docker exec kali_scanner_db psql -U kali_scanner -d kali_scanner -c \
  "SELECT COUNT(*) FROM osint.finding_type_mappings WHERE tool_name = 'spiderfoot';"
```

### SpiderFoot Database (SQLite)

```bash
# Check SpiderFoot tables
docker exec spiderfoot python3 -c "
import sqlite3
conn = sqlite3.connect('/home/spiderfoot/.spiderfoot/spiderfoot.db')
c = conn.cursor()
c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
for t in c.fetchall(): print(t[0])
"

# View configured API keys
docker exec spiderfoot python3 -c "
import sqlite3
conn = sqlite3.connect('/home/spiderfoot/.spiderfoot/spiderfoot.db')
c = conn.cursor()
c.execute('SELECT opt, val FROM tbl_config WHERE opt LIKE \"%api_key%\"')
for row in c.fetchall():
    val = row[1][:20] + '...' if len(row[1]) > 20 else row[1]
    print(f'{row[0]}: {val}')
"
```

## Data Flow

1. **Run Scan**: Access SpiderFoot at `http://AIServer:5002`, create and run a scan
2. **Automatic Sync**: Normalizer polls every 5 minutes for completed scans
3. **Type Mapping**: SpiderFoot types (e.g., `IP_ADDRESS`, `MALICIOUS_IPADDR`) are mapped to normalized types
4. **PostgreSQL Storage**: Findings stored in `osint.findings` with relationships in `osint.finding_relationships`

## PostgreSQL Schema

### Tables

| Table | Purpose |
|-------|---------|
| `osint.scan_sources` | Records each scan run |
| `osint.findings` | Normalized discoveries |
| `osint.finding_relationships` | Parent-child links between findings |
| `osint.finding_type_mappings` | Tool type → normalized type mappings |
| `osint.finding_types` | Reference list of normalized types |

### Views

| View | Purpose |
|------|---------|
| `osint.threat_findings` | Findings with risk_level >= 40 |
| `osint.recent_scans` | Scans with finding counts |

## API Keys Configured

Stored in SpiderFoot SQLite (`tbl_config`):
- VirusTotal
- AbuseIPDB
- AlienVault OTX

## File Locations

| What | Where |
|------|-------|
| Docker Compose | `~/Docker/mydocker/kali-scanner/docker-compose.yml` |
| Normalizer Source | `~/Code/kali-scanner/normalizer/src/` |
| PostgreSQL Schema | `~/Code/kali-scanner/database/init.sql` |
| SpiderFoot Data | `~/Docker/mydocker/kali-scanner/spiderfoot/data/` |

## Troubleshooting

### "no such table: tbl_scan_instance"

**Normal** - SpiderFoot creates tables only when scans run through the web UI. Start a scan first.

### Normalizer not syncing

1. Check logs: `docker logs kali_scanner_normalizer --tail 50`
2. Verify scan completed: Look for status `FINISHED` in SpiderFoot UI
3. Wait for next poll cycle (every 5 minutes)

### PostgreSQL connection issues

```bash
# Test connection
docker exec kali_scanner_db psql -U kali_scanner -d kali_scanner -c "\conninfo"

# Check schema exists
docker exec kali_scanner_db psql -U kali_scanner -d kali_scanner -c "\dn"
```

---

*Created by Claude Code session - 2026-01-06*
