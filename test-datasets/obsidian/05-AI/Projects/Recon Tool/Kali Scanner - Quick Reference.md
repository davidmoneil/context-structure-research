---
tags:
  - project/kali-scanner
  - depth/standard
  - domain/security
  - depth/quick
created: 2026-01-13T14:15
updated: 2026-01-24T10:54
---
# Kali Scanner - Quick Reference

## Cache Management

```bash
# Check cache keys
docker exec kali-redis redis-cli KEYS "kali:*"

# Invalidate all caches
curl -X POST "http://localhost:8150/relationships/cache/invalidate?pattern=*"

# Get cache stats
curl http://localhost:8150/relationships/cache/stats
```

## Database Queries

```sql
-- Asset counts by type
SELECT finding_type, COUNT(*) as unique_count, SUM(discovery_count) as total_discoveries
FROM osint.assets
GROUP BY finding_type
ORDER BY unique_count DESC;

-- High risk assets
SELECT value, finding_type, max_risk_level, discovery_count
FROM osint.assets
WHERE max_risk_level >= 70
ORDER BY max_risk_level DESC;

-- Recent discoveries
SELECT a.value, a.finding_type, ai.discovered_at, s.source_name
FROM osint.asset_instances ai
JOIN osint.assets a ON ai.asset_id = a.id
JOIN osint.scan_sources s ON ai.source_id = s.id
ORDER BY ai.discovered_at DESC
LIMIT 20;

-- Relationship chain (parent → child)
SELECT 
    p.value as parent, p.finding_type as parent_type,
    c.value as child, c.finding_type as child_type,
    r.occurrence_count
FROM osint.asset_relationships r
JOIN osint.assets p ON r.parent_asset_id = p.id
JOIN osint.assets c ON r.child_asset_id = c.id
ORDER BY r.occurrence_count DESC
LIMIT 20;

-- Validation stats
SELECT validation_status, COUNT(*) as count
FROM osint.assets
GROUP BY validation_status;
```

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/relationships` | GET | Main relationships page |
| `/relationships/cache/invalidate` | POST | Clear caches |
| `/relationships/cache/stats` | GET | Cache statistics |
| `/review` | GET | Finding review page |
| `/review/bulk` | POST | Bulk review actions |

## Container Management

```bash
# Restart dashboard
docker compose restart dashboard

# View logs
docker compose logs -f dashboard

# Rebuild after code changes
docker compose build dashboard --no-cache && docker compose up -d dashboard

# Check Redis
docker exec kali-redis redis-cli INFO
```

## File Locations

| Component | Path |
|-----------|------|
| Dashboard app | `~/Code/kali-scanner/dashboard/app/` |
| Relationship service | `dashboard/app/services/relationship_service.py` |
| Cache module | `dashboard/app/cache.py` |
| Migrations | `~/Code/kali-scanner/database/migrations/` |
| Normalizer | `~/Code/kali-scanner/normalizer/src/` |

## Schema Summary

```
osint.assets (unique entities)
├── id, value, finding_type (unique)
├── max_risk_level, max_confidence, min_hop_distance
├── discovery_count, first/last_discovered_at
├── discovery_methods[], original_types[]
└── validation_status, false_positive

osint.asset_instances (discovery occurrences)
├── asset_id → assets.id
├── source_id → scan_sources.id
├── event_hash, source_event_hash
└── confidence, risk_level, hop_distance, metadata

osint.asset_relationships (aggregated edges)
├── parent_asset_id, child_asset_id
├── relationship_type
└── occurrence_count, first/last_seen_at
```

## Tags

#kali-scanner #reference #cheatsheet
