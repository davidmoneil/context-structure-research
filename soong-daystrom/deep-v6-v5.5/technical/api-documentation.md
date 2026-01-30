# PCS Companion Robot SDK Documentation

## Overview

The PCS Companion Robot SDK provides developers with comprehensive tools to build applications that integrate with Soong-Daystrom's Positronic Companion Series robots. This SDK enables custom behaviors, third-party integrations, and enterprise applications.

**SDK Version**: 4.2.0
**API Version**: v3
**Release Date**: October 2124
**Compatibility**: PCS-250, PCS-400, PCS-500, PCS v4 (Aurora)
**Documentation Portal**: developer.soong-daystrom.com/pcs-sdk

---

## 1. Getting Started

### 1.1 Prerequisites

- Active Soong-Daystrom Developer Account
- API credentials (API Key + Secret)
- PCS device with firmware 3.2.0 or higher
- SDK-compatible development environment

### 1.2 Installation

**Python**:
```bash
pip install soong-daystrom-pcs-sdk>=4.2.0
```

**JavaScript/TypeScript**:
```bash
npm install @soong-daystrom/pcs-sdk
# or
yarn add @soong-daystrom/pcs-sdk
```

**Go**:
```bash
go get github.com/soong-daystrom/pcs-sdk-go@v4.2.0
```

**Rust**:
```toml
[dependencies]
soong-daystrom-pcs = "4.2.0"
```

### 1.3 Quick Start

**Python Example**:
```python
from soong_daystrom import PCSClient, DeviceConfig

# Initialize client
client = PCSClient(
    api_key="pk_live_your_public_key",
    api_secret="sk_live_your_secret_key",
    environment="production"  # or "sandbox"
)

# Connect to device
device = client.connect_device("dev_abc123xyz")

# Simple interaction
response = device.cognitive.send_message(
    message="Hello! What's the weather like today?",
    context={"user_name": "Alex"}
)
print(response.content)  # "Hi Alex! Let me check..."

# Execute a task
task = device.execute_task(
    task_type="schedule_reminder",
    parameters={
        "message": "Meeting with Dr. Chen",
        "time": "2024-10-22T14:00:00Z",
        "priority": "high"
    }
)
print(f"Task created: {task.id}")
```

---

## 2. Authentication

### 2.1 API Key Authentication

All SDK operations require authentication. The SDK supports multiple authentication methods:

**Method 1: Direct Initialization**
```python
client = PCSClient(
    api_key="pk_live_xxx",
    api_secret="sk_live_xxx"
)
```

**Method 2: Environment Variables**
```bash
export SDI_API_KEY="pk_live_xxx"
export SDI_API_SECRET="sk_live_xxx"
```

```python
client = PCSClient.from_environment()
```

**Method 3: Configuration File**
```yaml
# ~/.soong-daystrom/config.yaml
production:
  api_key: pk_live_xxx
  api_secret: sk_live_xxx

sandbox:
  api_key: pk_test_xxx
  api_secret: sk_test_xxx
```

```python
client = PCSClient.from_config(profile="production")
```

### 2.2 OAuth 2.0 for User Context

For applications acting on behalf of users:

```python
from soong_daystrom.auth import OAuth2Client

oauth = OAuth2Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="https://yourapp.com/callback"
)

# Generate authorization URL
auth_url = oauth.get_authorization_url(
    scopes=["device:read", "device:write", "cognitive:read"],
    state="random_state_string"
)

# After user authorization, exchange code for tokens
tokens = oauth.exchange_code(authorization_code="code_from_callback")

# Use tokens with client
client = PCSClient.with_oauth(tokens)
```

### 2.3 Scopes Reference

| Scope | Description | Access Level |
|-------|-------------|--------------|
| `device:read` | Read device status, telemetry | Basic |
| `device:write` | Control device, send commands | Standard |
| `device:admin` | Full device management, firmware | Admin |
| `cognitive:read` | Query AI, read conversations | Basic |
| `cognitive:write` | Create conversations, tasks | Standard |
| `cognitive:admin` | Modify AI behavior, training | Admin |
| `memory:read` | Read device memories | Sensitive |
| `memory:write` | Create/modify memories | Sensitive |
| `memory:delete` | Delete memories | Admin |
| `sensor:read` | Access sensor data streams | Standard |
| `sensor:raw` | Raw sensor data access | Admin |
| `analytics:read` | View usage analytics | Basic |
| `fleet:manage` | Multi-device management | Enterprise |

---

## 3. Device Management API

### 3.1 Listing Devices

```python
# Get all devices
devices = client.devices.list()

for device in devices:
    print(f"{device.name}: {device.status}")

# Filter devices
online_devices = client.devices.list(
    status="online",
    model="PCS-400",
    location_id="loc_home_main"
)

# Pagination
page1 = client.devices.list(page=1, per_page=20)
page2 = client.devices.list(page=2, per_page=20)
```

**Response Object**:
```python
Device(
    id="dev_abc123",
    serial_number="SDI-2024-847291",
    model="PCS-400",
    name="Kitchen Companion",
    status="online",  # online, offline, maintenance, updating
    firmware_version="3.2.1",
    sce_version="3.2.0",
    location=Location(id="loc_xyz", name="Main House"),
    capabilities=["conversation", "household", "health_monitoring"],
    battery=BatteryStatus(level=87, charging=False),
    created_at=datetime(2023, 3, 15)
)
```

### 3.2 Device Details

```python
device = client.devices.get("dev_abc123")

# Detailed status
print(f"Battery: {device.battery.level}%")
print(f"Uptime: {device.statistics.uptime_hours} hours")
print(f"Sensors: {device.sensors}")

# Network information
print(f"IP: {device.network.ip_address}")
print(f"WiFi Signal: {device.network.wifi_strength} dBm")
```

### 3.3 Device Configuration

```python
# Update device settings
device.update(
    name="New Name",
    settings={
        "volume": 75,
        "personality_mode": "professional",  # friendly, professional, formal
        "wake_word": "Hey Companion",
        "language": "en-US",
        "voice": "voice_sarah_v3",
        "timezone": "America/Los_Angeles"
    }
)

# Enable/disable features
device.features.enable("health_monitoring")
device.features.disable("ambient_music")

# Personality customization (Enterprise only)
device.personality.customize(
    traits={
        "formality": 0.7,  # 0.0 = casual, 1.0 = formal
        "verbosity": 0.4,  # 0.0 = concise, 1.0 = detailed
        "humor": 0.5,      # 0.0 = serious, 1.0 = humorous
        "empathy": 0.8     # 0.0 = neutral, 1.0 = empathetic
    }
)
```

### 3.4 Device Commands

```python
# Navigation
device.commands.navigate(
    destination="kitchen",
    speed="normal",  # slow, normal, fast
    avoid_obstacles=True
)

# Speech
device.commands.speak(
    text="Dinner is ready!",
    language="en-US",
    emotion="cheerful",
    volume=80
)

# Task execution
device.commands.execute_task(
    task_id="task_vacuum_living_room",
    parameters={"intensity": "deep"}
)

# Emergency operations
device.commands.emergency_stop(reason="user_requested")
device.commands.reboot(graceful=True, delay_seconds=5)

# Firmware update
device.commands.update_firmware(
    version="3.2.2",
    schedule="2024-10-23T03:00:00Z",  # Optional: schedule update
    force=False
)
```

### 3.5 Command Response Handling

```python
# Synchronous execution (wait for completion)
result = device.commands.navigate(
    destination="bedroom",
    wait=True,
    timeout=300  # seconds
)
print(f"Navigation completed: {result.success}")

# Asynchronous execution
command = device.commands.navigate(
    destination="bedroom",
    wait=False
)
print(f"Command ID: {command.id}")

# Poll for status
while not command.is_complete:
    command.refresh()
    print(f"Progress: {command.progress}%")
    time.sleep(1)

# Callback-based
def on_complete(result):
    print(f"Navigation finished: {result.success}")

device.commands.navigate(
    destination="bedroom",
    on_complete=on_complete
)
```

---

## 4. Cognitive API

### 4.1 Conversations

```python
# Start a new conversation
conversation = device.cognitive.create_conversation(
    context={
        "user_name": "Alex",
        "relationship": "owner",
        "preferences": {
            "formality": "casual",
            "topics_of_interest": ["technology", "cooking"]
        }
    }
)

# Send message and get response
response = conversation.send_message("What should I make for dinner tonight?")
print(response.content)
print(f"Emotion: {response.emotion.primary} ({response.emotion.intensity})")
print(f"Confidence: {response.confidence}")

# Continue conversation
response2 = conversation.send_message("I have chicken and vegetables")

# Get conversation history
for message in conversation.messages:
    print(f"[{message.role}]: {message.content}")

# End conversation
conversation.close()
```

### 4.2 Streaming Responses

```python
# Stream response chunks
for chunk in conversation.send_message_stream("Tell me about the history of robotics"):
    print(chunk.content, end="", flush=True)
    if chunk.is_final:
        print(f"\n[Emotion: {chunk.emotion}]")
```

### 4.3 Knowledge Queries

```python
# Query device knowledge
results = device.cognitive.query(
    query="What appointments do I have tomorrow?",
    sources=["calendar", "email", "notes"],
    max_results=10
)

print(results.summary)
for result in results.data:
    print(f"- {result.title} at {result.start_time}")

# Query with filters
results = device.cognitive.query(
    query="Find my recent purchases",
    sources=["email"],
    filters={
        "date_range": {"start": "2024-10-01", "end": "2024-10-21"},
        "keywords": ["order", "confirmation", "receipt"]
    }
)
```

### 4.4 Task Execution

```python
# Create a cognitive task
task = device.cognitive.create_task(
    task_type="research",
    description="Find the best Italian restaurants nearby with outdoor seating",
    constraints={
        "max_distance_km": 10,
        "price_range": "$$",
        "rating_minimum": 4.0,
        "must_have": ["outdoor_seating", "reservations"]
    },
    output_format="detailed",
    deadline="2024-10-21T18:00:00Z"
)

# Wait for completion
result = task.wait(timeout=600)
print(result.summary)
for restaurant in result.data:
    print(f"- {restaurant.name}: {restaurant.rating}★")

# Or use callbacks
task.on_progress(lambda p: print(f"Progress: {p}%"))
task.on_complete(lambda r: print(f"Found {len(r.data)} results"))
```

### 4.5 Task Types Reference

| Task Type | Description | Typical Duration |
|-----------|-------------|------------------|
| `research` | Information gathering | 30s - 5min |
| `summarize` | Content summarization | 10s - 1min |
| `schedule` | Calendar management | 5s - 30s |
| `reminder` | Set reminders | <5s |
| `communication` | Draft messages | 10s - 1min |
| `analysis` | Data analysis | 30s - 10min |
| `recommendation` | Personalized suggestions | 15s - 2min |
| `planning` | Trip/event planning | 1min - 10min |
| `translation` | Language translation | 5s - 30s |
| `creative` | Creative writing | 30s - 5min |

---

## 5. Sensor Data API

### 5.1 Available Sensors

| Sensor | Data Type | Update Rate | PCS-250 | PCS-400 | PCS-500 |
|--------|-----------|-------------|---------|---------|---------|
| Camera (RGB) | Image/Video | 30 fps | Yes | Yes | Yes |
| Camera (Depth) | Point cloud | 30 fps | No | Yes | Yes |
| Microphone | Audio | 48 kHz | Yes | Yes | Yes |
| LIDAR | 3D scan | 10 Hz | No | Yes | Yes |
| Temperature | Float (°C) | 1 Hz | Yes | Yes | Yes |
| Humidity | Float (%) | 1 Hz | No | Yes | Yes |
| Air Quality | Integer (AQI) | 0.1 Hz | No | Optional | Yes |
| Touch | Boolean array | 100 Hz | Yes | Yes | Yes |
| IMU | Quaternion + Accel | 100 Hz | Yes | Yes | Yes |
| Battery | Status object | 1 Hz | Yes | Yes | Yes |

### 5.2 Reading Sensor Data

```python
# Single reading
temperature = device.sensors.temperature.read()
print(f"Temperature: {temperature.value}°C")

# Batch reading
readings = device.sensors.read_all()
print(f"Temperature: {readings.temperature.value}°C")
print(f"Humidity: {readings.humidity.value}%")
print(f"Air Quality: {readings.air_quality.aqi}")

# Camera snapshot
image = device.sensors.camera.capture()
image.save("snapshot.jpg")

# Depth map
depth = device.sensors.depth_camera.capture()
depth.to_point_cloud().save("scene.ply")
```

### 5.3 Streaming Sensor Data

```python
# Stream camera feed
stream = device.sensors.camera.stream(
    resolution="1080p",
    fps=30,
    format="h264"
)

for frame in stream:
    process_frame(frame)
    if should_stop:
        break

stream.stop()

# Stream multiple sensors
async def process_sensors():
    async with device.sensors.stream_multiple(
        sensors=["temperature", "humidity", "air_quality"],
        interval_ms=1000
    ) as stream:
        async for reading in stream:
            log_environmental_data(reading)

# WebSocket streaming
ws_url = device.sensors.get_stream_url(
    sensors=["camera", "microphone"],
    token=client.get_stream_token()
)
```

### 5.4 Sensor Events

```python
# Subscribe to sensor events
def on_motion_detected(event):
    print(f"Motion detected in {event.location}")
    print(f"Confidence: {event.confidence}")

device.sensors.on_event("motion_detected", on_motion_detected)

# Event types
device.sensors.on_event("face_detected", handle_face)
device.sensors.on_event("voice_activity", handle_voice)
device.sensors.on_event("object_detected", handle_object)
device.sensors.on_event("anomaly_detected", handle_anomaly)

# Remove handler
device.sensors.off_event("motion_detected", on_motion_detected)
```

---

## 6. Memory API

### 6.1 Memory Types

| Type | Description | Retention | Example |
|------|-------------|-----------|---------|
| `episodic` | Events and experiences | Configurable | "User had coffee at 8am" |
| `semantic` | Facts and knowledge | Permanent | "User prefers oat milk" |
| `procedural` | Learned skills | Permanent | "How to make user's coffee" |
| `working` | Current context | Session | "Currently helping with dinner" |

### 6.2 Reading Memories

```python
# List memories
memories = device.memory.list(
    type="semantic",
    category="user_preferences",
    limit=50
)

for memory in memories:
    print(f"[{memory.created_at}] {memory.content}")

# Search memories
results = device.memory.search(
    query="coffee preferences",
    types=["semantic", "procedural"],
    date_range={
        "start": "2024-01-01",
        "end": "2024-10-21"
    }
)

# Get specific memory
memory = device.memory.get("mem_abc123")
print(memory.content)
print(f"Importance: {memory.importance}")
print(f"Source: {memory.source}")
```

### 6.3 Creating Memories

```python
# Create semantic memory
memory = device.memory.create(
    type="semantic",
    category="user_preferences",
    content={
        "preference": "coffee_preparation",
        "details": {
            "type": "latte",
            "milk": "oat",
            "temperature": "extra_hot",
            "size": "large"
        }
    },
    importance=0.8,
    source="user_explicit"  # user_explicit, observed, inferred
)

# Create episodic memory
device.memory.create(
    type="episodic",
    category="daily_events",
    content={
        "event": "user_returned_home",
        "time": "2024-10-21T18:30:00Z",
        "mood_observed": "tired",
        "actions_taken": ["greeted_user", "offered_tea"]
    },
    importance=0.5
)
```

### 6.4 Memory Management

```python
# Update memory importance
device.memory.update("mem_abc123", importance=0.9)

# Delete memory
device.memory.delete("mem_abc123")

# Bulk delete (with confirmation)
device.memory.delete_many(
    type="episodic",
    older_than="2024-01-01",
    confirm=True
)

# Export memories (GDPR compliance)
export = device.memory.export(
    format="json",
    include_types=["episodic", "semantic"],
    anonymize=False
)
export.download("my_memories.json")

# Import memories (device migration)
device.memory.import_from(
    file_path="old_device_memories.json",
    merge_strategy="keep_newer"  # keep_newer, keep_older, keep_both
)
```

---

## 7. Real-Time Events API

### 7.1 WebSocket Connection

```python
from soong_daystrom.realtime import RealtimeClient

realtime = RealtimeClient(client)

# Connect
await realtime.connect()

# Subscribe to device events
await realtime.subscribe(f"device:{device.id}:status")
await realtime.subscribe(f"device:{device.id}:conversations")
await realtime.subscribe(f"device:{device.id}:alerts")

# Handle events
@realtime.on("status_changed")
async def handle_status(event):
    print(f"Device status: {event.status}")

@realtime.on("message")
async def handle_message(event):
    print(f"New message: {event.content}")

@realtime.on("alert")
async def handle_alert(event):
    print(f"Alert: {event.severity} - {event.message}")

# Run event loop
await realtime.listen()
```

### 7.2 Event Types

| Event | Channel | Payload |
|-------|---------|---------|
| `status_changed` | device:*:status | `{status, previous_status, timestamp}` |
| `telemetry` | device:*:telemetry | `{metrics: {...}, timestamp}` |
| `message` | device:*:conversations | `{conversation_id, message, role}` |
| `task_progress` | device:*:tasks | `{task_id, progress, status}` |
| `task_complete` | device:*:tasks | `{task_id, result, duration}` |
| `alert` | device:*:alerts | `{severity, message, action_required}` |
| `sensor_event` | device:*:sensors | `{sensor, event_type, data}` |
| `battery_low` | device:*:power | `{level, estimated_time_remaining}` |
| `firmware_update` | device:*:system | `{version, status, progress}` |

### 7.3 Presence and Heartbeat

```python
# Track connection status
@realtime.on("connected")
def on_connected():
    print("Connected to realtime service")

@realtime.on("disconnected")
def on_disconnected(reason):
    print(f"Disconnected: {reason}")

@realtime.on("reconnecting")
def on_reconnecting(attempt):
    print(f"Reconnecting... attempt {attempt}")

# Configure heartbeat
realtime.configure(
    heartbeat_interval=30,  # seconds
    reconnect_attempts=5,
    reconnect_delay=1000  # ms, exponential backoff
)
```

---

## 8. Fleet Management API

### 8.1 Fleet Overview (Enterprise)

```python
from soong_daystrom.fleet import FleetManager

fleet = FleetManager(client)

# Get fleet status
status = fleet.get_status()
print(f"Total devices: {status.total_devices}")
print(f"Online: {status.devices_online}")
print(f"Alerts: {status.active_alerts}")

# List all devices
for device in fleet.devices:
    print(f"{device.name}: {device.status}")
```

### 8.2 Group Management

```python
# Create device group
group = fleet.groups.create(
    name="Office Robots",
    description="All companion robots in the office building",
    device_ids=["dev_abc", "dev_def", "dev_ghi"]
)

# Add/remove devices
group.add_device("dev_jkl")
group.remove_device("dev_abc")

# Bulk operations
group.execute_command(
    command="update_firmware",
    parameters={"version": "3.2.2"},
    schedule="2024-10-23T03:00:00Z"
)

# Group settings
group.update_settings({
    "personality_mode": "professional",
    "volume": 60,
    "language": "en-US"
})
```

### 8.3 Fleet Analytics

```python
# Fleet-wide analytics
analytics = fleet.analytics.get(period="30d")
print(f"Total interactions: {analytics.total_interactions}")
print(f"Average satisfaction: {analytics.average_satisfaction}")
print(f"Uptime: {analytics.average_uptime}%")

# Device comparison
comparison = fleet.analytics.compare(
    device_ids=["dev_abc", "dev_def"],
    metrics=["interactions", "tasks_completed", "errors"],
    period="7d"
)

# Anomaly detection
anomalies = fleet.analytics.detect_anomalies(
    threshold="medium",  # low, medium, high
    period="24h"
)
for anomaly in anomalies:
    print(f"{anomaly.device_id}: {anomaly.description}")
```

---

## 9. Error Handling

### 9.1 Exception Hierarchy

```python
from soong_daystrom.exceptions import (
    SDIException,           # Base exception
    AuthenticationError,    # Invalid credentials
    PermissionDeniedError,  # Insufficient permissions
    DeviceNotFoundError,    # Device doesn't exist
    DeviceOfflineError,     # Device unreachable
    RateLimitError,         # Too many requests
    ValidationError,        # Invalid parameters
    NetworkError,           # Connection issues
    TimeoutError,           # Operation timeout
    ServiceError            # Server-side error
)
```

### 9.2 Error Handling Patterns

```python
from soong_daystrom.exceptions import *

try:
    device = client.devices.get("dev_abc123")
    response = device.cognitive.send_message("Hello")
except DeviceNotFoundError as e:
    print(f"Device not found: {e.device_id}")
except DeviceOfflineError as e:
    print(f"Device offline since: {e.last_seen}")
    # Queue for retry
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
    time.sleep(e.retry_after)
except AuthenticationError:
    print("Please check your API credentials")
except SDIException as e:
    print(f"Error: {e.message}")
    print(f"Request ID: {e.request_id}")
    print(f"Documentation: {e.documentation_url}")
```

### 9.3 Retry Configuration

```python
from soong_daystrom import PCSClient, RetryConfig

client = PCSClient(
    api_key="pk_live_xxx",
    api_secret="sk_live_xxx",
    retry_config=RetryConfig(
        max_retries=3,
        retry_on=[429, 500, 502, 503, 504],
        backoff_factor=2,
        max_backoff=60
    )
)
```

---

## 10. SDK Configuration

### 10.1 Client Options

```python
client = PCSClient(
    api_key="pk_live_xxx",
    api_secret="sk_live_xxx",

    # Environment
    environment="production",  # production, sandbox
    base_url=None,  # Custom API endpoint

    # Timeouts
    timeout=30,  # seconds
    connect_timeout=10,

    # Retry
    retry_config=RetryConfig(...),

    # Logging
    log_level="INFO",  # DEBUG, INFO, WARNING, ERROR
    log_requests=False,  # Log all API requests

    # HTTP
    http_client=None,  # Custom HTTP client
    proxy=None,  # HTTP proxy
    verify_ssl=True
)
```

### 10.2 Logging Configuration

```python
import logging
from soong_daystrom import configure_logging

configure_logging(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handler=logging.FileHandler("sdk.log")
)
```

---

## 11. Rate Limits and Quotas

### 11.1 Rate Limit Tiers

| Tier | Requests/Hour | Burst/Second | WebSocket Connections | Price |
|------|---------------|--------------|----------------------|-------|
| Free | 100 | 10 | 1 | $0 |
| Developer | 10,000 | 100 | 5 | $49/mo |
| Professional | 100,000 | 500 | 20 | $299/mo |
| Enterprise | 1,000,000 | 2,000 | 100 | Custom |
| Unlimited | Unlimited | 10,000 | 500 | Custom |

### 11.2 Checking Rate Limits

```python
# Check current usage
limits = client.get_rate_limits()
print(f"Remaining: {limits.remaining}/{limits.limit}")
print(f"Reset at: {limits.reset_at}")

# Rate limit headers are also available on responses
response = client.devices.list()
print(f"Remaining: {response.rate_limit.remaining}")
```

---

## 12. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 4.2.0 | 2124-10 | Added fleet management, enhanced streaming |
| 4.1.0 | 2124-07 | PCS v4 (Aurora) support, new sensors |
| 4.0.0 | 2124-04 | Major rewrite, async support, breaking changes |
| 3.5.0 | 2123-10 | Memory API enhancements |
| 3.4.0 | 2123-07 | Real-time events API |
| 3.3.0 | 2123-04 | Cognitive tasks API |
| 3.2.0 | 2122-10 | Initial public release |

---

## 13. Support

- **Documentation**: developer.soong-daystrom.com/pcs-sdk
- **API Status**: status.soong-daystrom.com
- **Support Email**: sdk-support@soong-daystrom.com
- **Developer Forum**: community.soong-daystrom.com/sdk
- **GitHub Issues**: github.com/soong-daystrom/pcs-sdk-python/issues
- **Discord**: discord.gg/soong-daystrom-developers

**Office Hours**: Wednesdays 10am-12pm PT (Developer Q&A)
