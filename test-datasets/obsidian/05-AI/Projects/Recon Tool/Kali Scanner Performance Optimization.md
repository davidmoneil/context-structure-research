---
tags:
  - project/kali-scanner
  - depth/standard
  - domain/security
  - depth/deep
created: 2026-01-13T14:15
updated: 2026-01-24T10:54
---
# Kali Scanner Performance Optimization

## Overview

This document covers the comprehensive performance optimization work completed on the Kali Scanner dashboard, specifically targeting the Relationships page and data storage efficiency.

**Dates**: January 2026
**Project**: Kali Scanner Dashboard (`~/Code/kali-scanner/dashboard`)

## Problem Statement

The Kali Scanner Relationships page was experiencing performance issues:

1. **Duplicate Queries**: Multiple components fetching the same data
2. **No Caching**: Every page load hit the database for expensive aggregate queries
3. **Data Duplication**: 58,002 findings with only 23,850 unique (value, type) pairs - 59% redundancy
4. **Expensive Aggregations**: Runtime MD5 hashing and GROUP BY operations on 58K rows

## Solution Phases

### [[05-AI/Projects/Recon Tool/Kali Scanner - Phase 2 Redis Caching|Phase 2: Redis Caching]]

Implemented TTL-based caching for expensive relationship queries:
- Finding types (600s TTL)
- Discovery methods (600s TTL)
- Attack surface stats (300s TTL)
- Recent sources (120s TTL)
- Correlations summary (300s TTL)

### [[05-AI/Projects/Recon Tool/Kali Scanner - Phase 3 Database Normalization|Phase 3: Database Normalization]]

Normalized the database schema to eliminate redundancy:
- Created `osint.assets` table (unique entities)
- Created `osint.asset_instances` table (discovery occurrences)
- Created `osint.asset_relationships` table (aggregated relationships)
- Achieved 59% deduplication: 58,014 findings → 23,850 unique assets

## Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Unique entities tracked | 58,014 (with duplicates) | 23,850 (deduplicated) | 59% reduction |
| Type count queries | Full table scan | Index scan on assets | ~60% faster |
| Graph node generation | MD5 at runtime | Asset ID direct | ~90% faster |
| Cold page load | ~2-3s | ~0.5s (cached) | ~80% faster |
| Repeat page load | ~2-3s | <100ms (cache hit) | ~95% faster |

## Key Files Modified

### Dashboard
- `app/services/relationship_service.py` - Caching decorators, normalized queries
- `app/routers/relationships.py` - Cache management endpoints
- `app/routers/review.py` - Cache invalidation on bulk actions
- `app/cache.py` - Redis caching infrastructure
- `app/config.py` - Redis configuration
- `requirements.txt` - Added redis package

### Database
- `database/migrations/010_normalize_assets.sql` - Complete normalization migration

### Normalizer
- `normalizer/src/models/normalized.py` - Normalized insert methods

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  relationship_service.py                                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ @cached decorators → Redis (TTL-based)                  ││
│  │ Queries → osint.assets (normalized)                     ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
├─────────────────────────────────────────────────────────────┤
│  osint.assets (23,850 unique)                                │
│    └── osint.asset_instances (58,014 occurrences)           │
│    └── osint.asset_relationships (42,775 relationships)     │
│    └── osint.asset_tags                                      │
│                                                              │
│  osint.findings (original, preserved for compatibility)      │
│  osint.findings_compat (view for backwards compatibility)    │
└─────────────────────────────────────────────────────────────┘
```

## Related Documentation

- [[05-AI/Projects/Recon Tool/Kali Scanner - Phase 2 Redis Caching]]
- [[05-AI/Projects/Recon Tool/Kali Scanner - Phase 3 Database Normalization]]

## Tags

#kali-scanner #performance #optimization #database #redis #caching
