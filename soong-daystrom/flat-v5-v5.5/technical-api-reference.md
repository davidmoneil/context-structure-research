# Soong-Daystrom API Reference

## Overview

The Soong-Daystrom Developer Platform provides comprehensive APIs for integrating with all SDI products. This reference documents the complete API surface across REST, WebSocket, and gRPC interfaces.

**API Version**: 3.2
**Base URL**: `https://api.soong-daystrom.com/v3/`
**Documentation Portal**: developer.soong-daystrom.com
**Support**: api-support@soong-daystrom.com

---

## Authentication

### API Key Authentication

All API requests require authentication via API key:

```http
GET /v3/devices HTTP/1.1
Host: api.soong-daystrom.com
Authorization: Bearer sk_live_abc123xyz789
X-API-Key: pk_live_def456uvw012
```

**Key Types**:
- `sk_live_*`: Secret key (server-side only)
- `pk_live_*`: Public key (client-safe)
- `sk_test_*`: Test secret key
- `pk_test_*`: Test public key

### OAuth 2.0

For user-context operations, OAuth 2.0 is required:

**Authorization Endpoint**: `https://auth.soong-daystrom.com/oauth/authorize`
**Token Endpoint**: `https://auth.soong-daystrom.com/oauth/token`

**Supported Flows**:
- Authorization Code (web apps)
- Authorization Code + PKCE (mobile/SPA)
- Client Credentials (machine-to-machine)
- Device Authorization (IoT devices)

**Scopes**:

| Scope | Description | Access Level |
|-------|-------------|--------------|
| `device:read` | Read device status | Basic |
| `device:write` | Control devices | Standard |
| `device:admin` | Full device management | Admin |
| `cognitive:read` | Query AI systems | Basic |
| `cognitive:write` | Submit AI tasks | Standard |
| `memory:read` | Access memories | Sensitive |
| `memory:write` | Modify memories | Sensitive |
| `analytics:read` | View analytics | Basic |
| `admin:full` | Full administrative | Admin |

---

## Rate Limits

| Tier | Requests/Hour | Burst | Price |
|------|---------------|-------|-------|
| Free | 100 | 10/sec | $0 |
| Developer | 10,000 | 100/sec | $49/mo |
| Professional | 100,000 | 500/sec | $299/mo |
| Enterprise | 1,000,000 | 2000/sec | Custom |
| Unlimited | Unlimited | 10000/sec | Custom |

**Rate Limit Headers**:
```http
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9847
X-RateLimit-Reset: 1698451200
```

---

## Device API

### List Devices

```http
GET /v3/devices
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (online, offline, maintenance) |
| `model` | string | Filter by model (PCS-400, IAP-Standard, etc.) |
| `location` | string | Filter by location ID |
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Items per page (default: 20, max: 100) |

**Response**:
```json
{
  "data": [
    {
      "id": "dev_abc123",
      "model": "PCS-400",
      "serial_number": "SDI-2024-847291",
      "name": "Kitchen Companion",
      "status": "online",
      "firmware_version": "3.2.1",
      "last_seen": "2024-10-21T14:30:00Z",
      "location": {
        "id": "loc_xyz789",
        "name": "Main House",
        "timezone": "America/Los_Angeles"
      },
      "capabilities": ["conversation", "household", "health_monitoring"],
      "created_at": "2023-03-15T10:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 47,
    "total_pages": 3
  }
}
```

### Get Device

```http
GET /v3/devices/{device_id}
```

**Response**:
```json
{
  "id": "dev_abc123",
  "model": "PCS-400",
  "serial_number": "SDI-2024-847291",
  "name": "Kitchen Companion",
  "status": "online",
  "firmware_version": "3.2.1",
  "hardware_revision": "Rev C",
  "manufacture_date": "2024-01-15",
  "warranty_expires": "2027-01-15",
  "sce_version": "3.2.0",
  "positronic_nodes": 12000000000,
  "battery": {
    "level": 87,
    "charging": false,
    "time_remaining": "14h 23m",
    "health": 98
  },
  "sensors": {
    "camera": "operational",
    "microphone": "operational",
    "lidar": "operational",
    "temperature": "operational",
    "touch": "operational"
  },
  "network": {
    "wifi_ssid": "HomeNetwork",
    "wifi_strength": -42,
    "ip_address": "192.168.1.47",
    "mac_address": "A4:C3:F0:47:89:2B"
  },
  "statistics": {
    "uptime_hours": 8472,
    "interactions_total": 147823,
    "tasks_completed": 89471,
    "errors_last_30d": 3
  }
}
```

### Update Device

```http
PATCH /v3/devices/{device_id}
```

**Request Body**:
```json
{
  "name": "New Device Name",
  "location_id": "loc_newlocation",
  "settings": {
    "volume": 75,
    "personality_mode": "professional",
    "wake_word": "custom_wake_word",
    "language": "en-US"
  }
}
```

### Device Commands

```http
POST /v3/devices/{device_id}/commands
```

**Request Body**:
```json
{
  "command": "navigate",
  "parameters": {
    "destination": "kitchen",
    "speed": "normal",
    "avoid_obstacles": true
  },
  "priority": "normal",
  "timeout_seconds": 300
}
```

**Available Commands**:

| Command | Description | Parameters |
|---------|-------------|------------|
| `navigate` | Move to location | destination, speed, avoid_obstacles |
| `speak` | Speak text | text, language, emotion, volume |
| `listen` | Active listening | duration, wake_word_required |
| `execute_task` | Run predefined task | task_id, parameters |
| `emergency_stop` | Immediate halt | reason |
| `reboot` | Restart device | graceful, delay_seconds |
| `update_firmware` | Install update | version, force |
| `calibrate` | Run calibration | sensors, full |
| `sleep` | Enter sleep mode | duration, wake_conditions |
| `wake` | Exit sleep mode | none |

### Device Telemetry

```http
GET /v3/devices/{device_id}/telemetry
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `metrics` | array | Metrics to retrieve |
| `start_time` | datetime | Start of time range |
| `end_time` | datetime | End of time range |
| `resolution` | string | Data resolution (1m, 5m, 1h, 1d) |

**Response**:
```json
{
  "device_id": "dev_abc123",
  "metrics": {
    "cpu_usage": {
      "unit": "percent",
      "values": [
        {"timestamp": "2024-10-21T14:00:00Z", "value": 23.4},
        {"timestamp": "2024-10-21T14:05:00Z", "value": 45.2}
      ]
    },
    "memory_usage": {
      "unit": "percent",
      "values": [...]
    },
    "battery_level": {
      "unit": "percent",
      "values": [...]
    }
  }
}
```

---

## Cognitive API

The Cognitive API provides access to Soong-Daystrom's AI reasoning capabilities.

### Create Conversation

```http
POST /v3/cognitive/conversations
```

**Request Body**:
```json
{
  "device_id": "dev_abc123",
  "context": {
    "user_name": "John",
    "relationship": "owner",
    "preferences": {
      "formality": "casual",
      "verbosity": "concise"
    }
  },
  "initial_message": "Hello, how are you today?"
}
```

**Response**:
```json
{
  "conversation_id": "conv_xyz789",
  "device_id": "dev_abc123",
  "created_at": "2024-10-21T14:30:00Z",
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Hello, how are you today?",
      "timestamp": "2024-10-21T14:30:00Z"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "Hi John! I'm doing well, thank you for asking. I've been keeping busy organizing the kitchen inventory and noticed we're running low on a few items. Would you like me to add them to the shopping list?",
      "timestamp": "2024-10-21T14:30:01Z",
      "emotion": {
        "primary": "cheerful",
        "intensity": 0.7
      },
      "confidence": 0.94
    }
  ]
}
```

### Continue Conversation

```http
POST /v3/cognitive/conversations/{conversation_id}/messages
```

**Request Body**:
```json
{
  "content": "Yes, please add them to the list.",
  "attachments": []
}
```

### Query Knowledge

```http
POST /v3/cognitive/query
```

**Request Body**:
```json
{
  "device_id": "dev_abc123",
  "query": "What appointments do I have tomorrow?",
  "sources": ["calendar", "email", "notes"],
  "max_results": 10,
  "include_confidence": true
}
```

**Response**:
```json
{
  "query_id": "qry_abc123",
  "results": [
    {
      "type": "calendar_event",
      "title": "Team Meeting",
      "start_time": "2024-10-22T09:00:00Z",
      "end_time": "2024-10-22T10:00:00Z",
      "location": "Conference Room A",
      "confidence": 1.0,
      "source": "calendar"
    },
    {
      "type": "calendar_event",
      "title": "Dentist Appointment",
      "start_time": "2024-10-22T14:30:00Z",
      "end_time": "2024-10-22T15:30:00Z",
      "location": "Dr. Smith's Office",
      "confidence": 1.0,
      "source": "calendar"
    }
  ],
  "summary": "You have 2 appointments tomorrow: a Team Meeting at 9 AM and a Dentist Appointment at 2:30 PM."
}
```

### Execute Task

```http
POST /v3/cognitive/tasks
```

**Request Body**:
```json
{
  "device_id": "dev_abc123",
  "task_type": "research",
  "description": "Find information about local Italian restaurants with outdoor seating",
  "constraints": {
    "max_distance_km": 10,
    "price_range": "$$",
    "rating_minimum": 4.0
  },
  "output_format": "summary",
  "deadline": "2024-10-21T15:00:00Z"
}
```

**Response**:
```json
{
  "task_id": "task_xyz789",
  "status": "in_progress",
  "estimated_completion": "2024-10-21T14:35:00Z",
  "progress": 0,
  "webhook_url": "https://api.soong-daystrom.com/v3/tasks/task_xyz789/status"
}
```

### Get Task Result

```http
GET /v3/cognitive/tasks/{task_id}
```

**Response**:
```json
{
  "task_id": "task_xyz789",
  "status": "completed",
  "completed_at": "2024-10-21T14:34:47Z",
  "result": {
    "summary": "I found 5 Italian restaurants within 10km that have outdoor seating...",
    "data": [
      {
        "name": "Bella Italia",
        "address": "123 Main St",
        "rating": 4.5,
        "price_range": "$$",
        "outdoor_seating": true,
        "distance_km": 2.3
      }
    ]
  },
  "confidence": 0.89,
  "sources_used": ["yelp", "google_maps", "tripadvisor"]
}
```

---

## Memory API

The Memory API provides access to device memories and learned information.

### List Memories

```http
GET /v3/memory/{device_id}/memories
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Memory type (episodic, semantic, procedural) |
| `category` | string | Category filter |
| `start_date` | date | Filter by date range start |
| `end_date` | date | Filter by date range end |
| `search` | string | Full-text search |

### Create Memory

```http
POST /v3/memory/{device_id}/memories
```

**Request Body**:
```json
{
  "type": "semantic",
  "category": "user_preferences",
  "content": {
    "preference": "coffee_preparation",
    "details": {
      "type": "latte",
      "milk": "oat",
      "temperature": "extra_hot",
      "size": "large"
    }
  },
  "importance": 0.8,
  "source": "user_explicit"
}
```

### Delete Memory

```http
DELETE /v3/memory/{device_id}/memories/{memory_id}
```

**Response**: 204 No Content

### Export Memories

```http
POST /v3/memory/{device_id}/export
```

**Request Body**:
```json
{
  "format": "json",
  "include_types": ["episodic", "semantic"],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-10-21"
  },
  "anonymize": false
}
```

---

## Analytics API

### Get Device Analytics

```http
GET /v3/analytics/devices/{device_id}
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `metrics` | array | Metrics to include |
| `period` | string | Time period (7d, 30d, 90d, 1y) |
| `granularity` | string | Data granularity (hourly, daily, weekly) |

**Response**:
```json
{
  "device_id": "dev_abc123",
  "period": "30d",
  "metrics": {
    "total_interactions": 4728,
    "unique_users": 4,
    "tasks_completed": 1847,
    "average_response_time_ms": 234,
    "uptime_percentage": 99.7,
    "battery_cycles": 28,
    "errors": 7,
    "user_satisfaction_score": 4.8
  },
  "trends": {
    "interactions": {
      "change_percent": 12.4,
      "direction": "up"
    }
  },
  "daily_breakdown": [
    {
      "date": "2024-10-21",
      "interactions": 187,
      "tasks": 72,
      "errors": 0
    }
  ]
}
```

### Get Fleet Analytics

```http
GET /v3/analytics/fleet
```

**Response**:
```json
{
  "total_devices": 47,
  "devices_online": 45,
  "devices_offline": 2,
  "aggregate_metrics": {
    "total_interactions_30d": 89472,
    "average_uptime": 99.4,
    "fleet_satisfaction_score": 4.7
  },
  "alerts": [
    {
      "device_id": "dev_def456",
      "type": "offline",
      "since": "2024-10-21T12:00:00Z"
    }
  ]
}
```

---

## WebSocket API

For real-time communication, connect to the WebSocket endpoint:

**Endpoint**: `wss://realtime.soong-daystrom.com/v3/`

### Connection

```javascript
const ws = new WebSocket('wss://realtime.soong-daystrom.com/v3/', {
  headers: {
    'Authorization': 'Bearer sk_live_abc123'
  }
});
```

### Subscribe to Events

```json
{
  "type": "subscribe",
  "channels": [
    "device:dev_abc123:status",
    "device:dev_abc123:telemetry",
    "device:dev_abc123:conversations"
  ]
}
```

### Event Types

| Event | Channel | Description |
|-------|---------|-------------|
| `status_changed` | device:*:status | Device status update |
| `telemetry` | device:*:telemetry | Real-time metrics |
| `message` | device:*:conversations | New conversation message |
| `task_complete` | device:*:tasks | Task completion |
| `alert` | device:*:alerts | Device alert |
| `error` | device:*:errors | Error notification |

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "device_not_found",
    "message": "The requested device does not exist.",
    "details": {
      "device_id": "dev_invalid123"
    },
    "request_id": "req_abc123xyz",
    "documentation_url": "https://developer.soong-daystrom.com/errors/device_not_found"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `authentication_failed` | 401 | Invalid or missing credentials |
| `permission_denied` | 403 | Insufficient permissions |
| `device_not_found` | 404 | Device does not exist |
| `device_offline` | 409 | Device is not reachable |
| `rate_limit_exceeded` | 429 | Too many requests |
| `invalid_request` | 400 | Malformed request |
| `internal_error` | 500 | Server error |
| `service_unavailable` | 503 | Temporary unavailability |

---

## SDKs and Libraries

Official SDKs are available for:

| Language | Package | Documentation |
|----------|---------|---------------|
| Python | `soong-daystrom` | [PyPI](https://pypi.org/project/soong-daystrom) |
| JavaScript | `@soong-daystrom/sdk` | [npm](https://npmjs.com/package/@soong-daystrom/sdk) |
| Go | `github.com/soong-daystrom/go-sdk` | [pkg.go.dev](https://pkg.go.dev/github.com/soong-daystrom/go-sdk) |
| Java | `com.soong-daystrom:sdk` | [Maven Central](https://search.maven.org/artifact/com.soong-daystrom/sdk) |
| C# | `SoongDaystrom.SDK` | [NuGet](https://nuget.org/packages/SoongDaystrom.SDK) |
| Ruby | `soong_daystrom` | [RubyGems](https://rubygems.org/gems/soong_daystrom) |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 3.2 | 2024-10 | Added NIM integration, enhanced analytics |
| 3.1 | 2024-04 | WebSocket improvements, new memory APIs |
| 3.0 | 2023-10 | Complete API redesign, gRPC support |
| 2.5 | 2023-04 | Cognitive API v2, task system |
| 2.0 | 2022-10 | OAuth 2.0, rate limiting |

---

## Support

- **Documentation**: developer.soong-daystrom.com
- **API Status**: status.soong-daystrom.com
- **Support Email**: api-support@soong-daystrom.com
- **Developer Forum**: community.soong-daystrom.com
- **GitHub**: github.com/soong-daystrom
