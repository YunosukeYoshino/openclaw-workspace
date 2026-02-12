#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Event Bus - Pub/Sub communication system"""

import asyncio
import json
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    AGENT_START = "agent_start"
    AGENT_STOP = "agent_stop"
    AGENT_ERROR = "agent_error"
    DATA_UPDATE = "data_update"
    USER_MESSAGE = "user_message"
    SYSTEM_NOTIFY = "system_notify"
    CUSTOM = "custom"

@dataclass
class Event:
    id: str
    type: EventType
    source: str
    timestamp: datetime
    data: Dict[str, Any]

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000

    def subscribe(self, event_type: EventType, handler: Callable):
        type_key = event_type.value
        if type_key not in self.subscribers:
            self.subscribers[type_key] = []
        self.subscribers[type_key].append(handler)
        print(f"[EventBus] Subscribed {handler.__name__} to {type_key}")

    def unsubscribe(self, event_type: EventType, handler: Callable):
        type_key = event_type.value
        if type_key in self.subscribers and handler in self.subscribers[type_key]:
            self.subscribers[type_key].remove(handler)

    async def publish(self, event: Event):
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]

        type_key = event.type.value
        if type_key in self.subscribers:
            for handler in self.subscribers[type_key]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    print(f"[EventBus] Error in handler {handler.__name__}: {e}")

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        if event_type:
            filtered = [e for e in self.event_history if e.type == event_type]
            return filtered[-limit:]
        return self.event_history[-limit:]

event_bus = EventBus()

async def main():
    async def log_event(event: Event):
        print(f"[Logger] {event.type.value}: {event.data}")

    event_bus.subscribe(EventType.AGENT_START, log_event)

    await event_bus.publish(Event(
        id="1",
        type=EventType.AGENT_START,
        source="test",
        timestamp=datetime.now(),
        data={"agent": "test-agent", "pid": 12345}
    ))

if __name__ == "__main__":
    asyncio.run(main())
