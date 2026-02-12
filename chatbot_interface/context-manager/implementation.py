#!/usr/bin/env python3
"""
Context Manager Module
コンテキストマネージャー - 会話履歴・コンテキスト管理
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json


class Context:
    """コンテキストクラス"""

    def __init__(self, context_id: str, user_id: str, max_messages: int = 10):
        self.context_id = context_id
        self.user_id = user_id
        self.max_messages = max_messages
        self.messages = deque(maxlen=max_messages)
        self.variables = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """メッセージを追加"""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        })
        self.updated_at = datetime.now()

    def set_variable(self, key: str, value: Any):
        """変数を設定"""
        self.variables[key] = value
        self.updated_at = datetime.now()

    def get_variable(self, key: str, default: Any = None) -> Any:
        """変数を取得"""
        return self.variables.get(key, default)

    def get_messages(self, n: Optional[int] = None) -> List[Dict]:
        """メッセージを取得"""
        if n:
            return list(self.messages)[-n:]
        return list(self.messages)

    def to_dict(self) -> Dict[str, Any]:
        """辞書に変換"""
        return {
            'context_id': self.context_id,
            'user_id': self.user_id,
            'messages': list(self.messages),
            'variables': self.variables,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ContextManager:
    """コンテキストマネージャー"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.contexts: Dict[str, Context] = {}
        self.max_context_age = self.config.get('max_context_age', 3600)  # seconds

    def create_context(self, user_id: str) -> Context:
        """新しいコンテキストを作成"""
        context_id = f"ctx_{datetime.now().timestamp()}_{user_id}"
        context = Context(context_id, user_id)
        self.contexts[context_id] = context
        return context

    def get_context(self, context_id: str) -> Optional[Context]:
        """コンテキストを取得"""
        return self.contexts.get(context_id)

    def get_user_context(self, user_id: str) -> Optional[Context]:
        """ユーザーの最新コンテキストを取得"""
        user_contexts = [
            ctx for ctx in self.contexts.values()
            if ctx.user_id == user_id
        ]
        if user_contexts:
            return sorted(user_contexts, key=lambda c: c.updated_at, reverse=True)[0]
        return None

    def cleanup_old_contexts(self):
        """古いコンテキストを削除"""
        cutoff = datetime.now() - timedelta(seconds=self.max_context_age)
        to_remove = [
            ctx_id for ctx_id, ctx in self.contexts.items()
            if ctx.updated_at < cutoff
        ]
        for ctx_id in to_remove:
            del self.contexts[ctx_id]


if __name__ == '__main__':
    manager = ContextManager()
    print("Context Manager Module initialized")
