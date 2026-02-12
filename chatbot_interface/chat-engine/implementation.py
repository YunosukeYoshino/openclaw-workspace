#!/usr/bin/env python3
"""
Chat Engine Module
チャットエンジン - メッセージ送受信・会話管理
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio


class Message:
    """メッセージクラス"""

    def __init__(self, message_id: str, user_id: str, content: str, message_type: str = 'text'):
        self.message_id = message_id
        self.user_id = user_id
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now()
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'user_id': self.user_id,
            'content': self.content,
            'type': self.message_type,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class Conversation:
    """会話クラス"""

    def __init__(self, conversation_id: str, user_id: str):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.messages: List[Message] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.state = {}

    def add_message(self, message: Message):
        """メッセージを追加"""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_last_n_messages(self, n: int) -> List[Message]:
        """最後のn件のメッセージを取得"""
        return self.messages[-n:]


class ChatEngine:
    """チャットエンジン"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.conversations: Dict[str, Conversation] = {}
        self.message_handlers = []

    def create_conversation(self, user_id: str) -> Conversation:
        """新しい会話を作成"""
        conv_id = f"conv_{datetime.now().timestamp()}_{user_id}"
        conversation = Conversation(conv_id, user_id)
        self.conversations[conv_id] = conversation
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """会話を取得"""
        return self.conversations.get(conversation_id)

    async def send_message(self, conversation_id: str, user_id: str, content: str) -> Message:
        """メッセージを送信"""
        message = Message(
            message_id=f"msg_{datetime.now().timestamp()}",
            user_id=user_id,
            content=content
        )

        if conversation_id in self.conversations:
            self.conversations[conversation_id].add_message(message)

        # ハンドラーに通知
        for handler in self.message_handlers:
            await handler(message)

        return message

    def add_message_handler(self, handler):
        """メッセージハンドラーを追加"""
        self.message_handlers.append(handler)


if __name__ == '__main__':
    engine = ChatEngine()
    print("Chat Engine Module initialized")
