# Agent Integration System

## Components

### 1. Event Bus (event_bus/)
Event-based Pub/Sub communication system

**Features:**
- Async event processing
- Event history management
- Multiple subscribers

### 2. Message Bus (message_bus/)
Pub/Sub async messaging system

**Features:**
- Topic-based routing
- Priority messaging
- RPC support

### 3. Workflow Engine (workflow_engine/)
Complex workflow definition and execution

**Features:**
- Dependency management
- Parallel execution
- Error handling

### 4. Agent Discovery (agent_discovery/)
Dynamic agent detection and registration

**Features:**
- Auto detection
- Heartbeat monitoring
- Capability search

### 5. Event Logger (event_logger/)
Event history and replay system

**Features:**
- SQLite persistence
- Query functionality
- Auto cleanup

## Architecture

```
Agent Integration System
├── Event Bus (Pub/Sub)
├── Message Bus (Async messaging)
├── Workflow Engine (Workflows)
├── Agent Discovery (Registry)
└── Event Logger (Persistence)
```

## Usage

### Event Bus
```python
from event_bus.event_bus import event_bus, Event, EventType

def handler(event):
    print(f"Received: {event.data}")

event_bus.subscribe(EventType.AGENT_START, handler)
await event_bus.publish(Event(
    id="1",
    type=EventType.AGENT_START,
    source="test",
    timestamp=datetime.now(),
    data={"agent": "test-agent"}
))
```

### Message Bus
```python
from message_bus.message_bus import message_bus

await message_bus.start()

def handler(msg):
    print(f"Received: {msg.payload}")

message_bus.subscribe("topic.name", handler)
await message_bus.publish("topic.name", {"key": "value"})
```

### Workflow Engine
```python
from workflow_engine.workflow_engine import workflow_engine, Step

async def my_action(context):
    return {"result": "success"}

wf_id = workflow_engine.create_workflow("My Workflow", "Description")
workflow_engine.add_step(wf_id, Step(
    id="step1",
    name="Step 1",
    action=my_action
))

result = await workflow_engine.execute_workflow(wf_id)
```

### Agent Discovery
```python
from agent_discovery.agent_discovery import agent_discovery

agents = agent_discovery.get_all_agents()
management_agents = agent_discovery.find_by_capability("management")
```

### Event Logger
```python
from event_logger.event_logger import event_logger

event_logger.log("event_type", "source", {"key": "value"})
logs = event_logger.get_recent(limit=10)
stats = event_logger.get_stats()
```

## Status

- [OK] Event Bus
- [OK] Message Bus
- [OK] Workflow Engine
- [OK] Agent Discovery
- [OK] Event Logger

## Next Steps

1. Agent integration
2. Test suite creation
3. Performance optimization
4. Monitoring tools

---

Created: 2026-2-12
Author: Nanatou
