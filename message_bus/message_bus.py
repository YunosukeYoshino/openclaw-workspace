#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Message Bus - Async messaging system"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Message:
    id: str
    topic: str
    payload: Dict[str, Any]
    priority: MessagePriority
    timestamp: datetime
    sender: str
    reply_to: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "payload": self.payload,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "sender": self.sender,
            "reply_to": self.reply_to
        }

class MessageBus:
    def __init__(self):
        self.topics: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False

    async def start(self):
        self.running = True
        asyncio.create_task(self._process_messages())

    async def stop(self):
        self.running = False

    def subscribe(self, topic: str, handler: Callable):
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(handler)
        print(f"[MessageBus] Subscribed to topic: {topic}")

    def unsubscribe(self, topic: str, handler: Callable):
        if topic in self.topics and handler in self.topics[topic]:
            self.topics[topic].remove(handler)

    async def publish(self, topic: str, payload: Dict[str, Any],
                     priority: MessagePriority = MessagePriority.NORMAL,
                     sender: str = "unknown") -> str:
        message = Message(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            priority=priority,
            timestamp=datetime.now(),
            sender=sender
        )
        await self.message_queue.put(message)
        return message.id

    async def _process_messages(self):
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
                if message.topic in self.topics:
                    for handler in self.topics[message.topic]:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(message)
                            else:
                                handler(message)
                        except Exception as e:
                            print(f"[MessageBus] Error in handler: {e}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[MessageBus] Error: {e}")

message_bus = MessageBus()

async def main():
    await message_bus.start()

    def handle_message(msg: Message):
        print(f"[Handler] Received: {msg.topic} - {msg.payload}")

    message_bus.subscribe("test.topic", handle_message)
    await message_bus.publish("test.topic", {"message": "Hello, World!"})

    await asyncio.sleep(0.5)
    await message_bus.stop()

if __name__ == "__main__":
    asyncio.run(main())
