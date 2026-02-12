#!/usr/bin/env python3
"""
Webhook URLの登録・管理、イベントログ記録、設定の更新・削除、履歴照会を行うエージェントです。
"""

from pathlib import Path
from datetime import datetime
from db import Database
import json

class WebhookAgent:
    """WebhookAgent - Webhook URLの登録・管理、イベントログ記録、設定の更新・削除、履歴照会を行うエージェントです。"""

    def __init__(self, db_path: str = None):
        """初期化"""
        if db_path is None:
            db_path = Path(__file__).parent / "webhook-agent.db"
        self.db = Database(str(db_path))
        self.table_name = "webhook_agent"
        self._initialize_schema()

    def _initialize_schema(self):
        """データベーススキーマ初期化"""
        sql = f"""
            CREATE TABLE IF NOT EXISTS {{self.table_name}} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.db.execute(sql)

    def add(self, content: str, metadata: dict = None) -> int:
        """レコードを追加"""
        metadata_json = json.dumps(metadata) if metadata else None
        return self.db.insert(
            self.table_name,
            {"content": content, "metadata": metadata_json}
        )

    def get(self, record_id: int) -> dict:
        """レコードを取得"""
        return self.db.get_by_id(self.table_name, record_id)

    def list_all(self, limit: int = 100) -> list:
        """全レコードを取得"""
        return self.db.list_all(self.table_name, limit=limit)

    def update(self, record_id: int, content: str = None, metadata: dict = None) -> bool:
        """レコードを更新"""
        updates = {}
        if content is not None:
            updates["content"] = content
        if metadata is not None:
            updates["metadata"] = json.dumps(metadata)
        updates["updated_at"] = datetime.now().isoformat()

        return self.db.update(self.table_name, record_id, updates)

    def delete(self, record_id: int) -> bool:
        """レコードを削除"""
        return self.db.delete(self.table_name, record_id)

    def search(self, query: str) -> list:
        """レコードを検索"""
        return self.db.search(self.table_name, "content", query)


if __name__ == "__main__":
    agent = WebhookAgent()
    print(f"{WebhookAgent} initialized")
