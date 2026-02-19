---
tags:
  - project/kali-scanner
  - depth/standard
  - domain/security
created: 2026-01-13T14:15
updated: 2026-01-24T10:58
---
# Kali Scanner - Phase 2 Redis Caching

## Overview

Implemented Redis-based caching for expensive relationship service queries to reduce database load and improve page responsiveness.

**Date**: January 2026
**Status**: Complete and verified

## Implementation Details

### Cache Infrastructure

**File**: `dashboard/app/cache.py`

```python
from functools import wraps
from typing import Optional, Callable
import json
import hashlib

# Try to import redis, fall back to no-op if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

_redis_client: Optional[redis.Redis] = None

async def get_redis() -> Optional[redis.Redis]:
    """Get Redis client, creating if needed."""
    global _redis_client
    if not REDIS_AVAILABLE:
        return None
    if _redis_client is None:
        from .config import settings
        if settings.redis_url:
            _redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    return _redis_client

def cached(ttl: int = 300, prefix: str = ""):
    """Decorator to cache async function results in Redis."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client = await get_redis()
            if client is None:
                return await func(*args, **kwargs)
            
            # Build cache key from function name and arguments
            key_parts = [prefix or func.__name__]
            key_parts.extend(str(a) for a in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            full_key = f"kali:{prefix or func.__name__}:{cache_key}"
            
            # Try cache first
            try:
                cached_value = await client.get(full_key)
                if cached_value:
                    return json.loads(cached_value)
            except Exception:
                pass
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            try:
                await client.setex(full_key, ttl, json.dumps(result, default=str))
            except Exception:
                pass
            
            return result
        return wrapper
    return decorator
```

**File**: `dashboard/app/config.py`

```python
class Settings:
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
```

### Cached Functions

**File**: `dashboard/app/services/relationship_service.py`

| Function | TTL | Prefix | Purpose |
|----------|-----|--------|---------|
| `get_finding_types()` | 600s | `finding_types` | Distinct finding types for dropdowns |
| `get_discovery_methods()` | 600s | `discovery_methods` | Tool/module breakdown |
| `get_attack_surface_stats()` | 300s | `attack_surface_stats` | Dashboard stats (total, domains, IPs, etc.) |
| `get_recent_sources()` | 120s | `recent_sources` | Recent scan sources |
| `get_correlations_summary()` | 300s | `correlations_summary` | Correlation type counts |

### Cache Management Endpoints

**File**: `dashboard/app/routers/relationships.py`

```python
@router.post("/cache/invalidate")
async def invalidate_relationship_cache(
    pattern: str = Query("*", description="Cache pattern to invalidate")
):
    """Invalidate relationship caches by pattern."""
    count = await invalidate_cache(pattern)
    return JSONResponse(content={
        "status": "success",
        "invalidated_keys": count,
        "pattern": pattern
    })

@router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics for monitoring."""
    stats = await get_cache_stats()
    return JSONResponse(content=stats)
```

### Automatic Cache Invalidation

**File**: `dashboard/app/routers/review.py`

Cache is automatically invalidated after bulk review actions:

```python
# After bulk action completes:
await invalidate_cache("attack_surface_stats")
if action == 'reclassify':
    await invalidate_cache("finding_types")
```

## Docker Configuration

**File**: `docker-compose.yaml`

```yaml
services:
  redis:
    image: redis:alpine
    container_name: kali-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  dashboard:
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
```

**File**: `dashboard/requirements.txt`

```
redis>=5.0.0
```

## Verification

### Check Cache Keys

```bash
docker exec kali-redis redis-cli KEYS "kali:*"
```

### Check Cache Stats

```bash
curl http://localhost:8150/relationships/cache/stats
```

### Invalidate Cache

```bash
# Invalidate all
curl -X POST "http://localhost:8150/relationships/cache/invalidate?pattern=*"

# Invalidate specific prefix
curl -X POST "http://localhost:8150/relationships/cache/invalidate?pattern=attack_surface_stats"
```

## Cache Key Format

```
kali:{prefix}:{md5_hash_of_args}
```

Examples:
- `kali:finding_types:d41d8cd98f00b204e9800998ecf8427e`
- `kali:attack_surface_stats:a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6`

## Performance Impact

| Scenario | Before | After |
|----------|--------|-------|
| First page load | ~2-3s | ~2-3s (no change, populates cache) |
| Subsequent loads | ~2-3s | <100ms (cache hit) |
| After data changes | Stale | Fresh (auto-invalidation) |

## Related

- [[05-AI/Projects/Recon Tool/Kali Scanner Performance Optimization]]
- [[05-AI/Projects/Recon Tool/Kali Scanner - Phase 3 Database Normalization]]

## Tags

#kali-scanner #redis #caching #performance
