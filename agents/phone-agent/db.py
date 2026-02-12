"""
Phone Agent Database Module
通話記録データベース管理
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager


class PhoneDB:
    """通話記録データベースクラス"""

    def __init__(self, db_path: str = "phone_calls.db"):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        """データベース接続コンテキストマネージャ"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """データベース初期化"""
        with self.get_connection() as conn:
            # 通話記録テーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_name TEXT,
                    phone_number TEXT NOT NULL,
                    call_type TEXT NOT NULL CHECK(call_type IN ('incoming', 'outgoing', 'missed')),
                    call_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    duration INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 連絡先テーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone_number TEXT UNIQUE NOT NULL,
                    email TEXT,
                    tags TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 通話履歴タグテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS call_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (call_id) REFERENCES calls(id) ON DELETE CASCADE
                )
            """)

            # インデックス作成
            conn.execute("CREATE INDEX IF NOT EXISTS idx_calls_time ON calls(call_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_calls_type ON calls(call_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_number)")

    # 通話記録の操作

    def add_call(self, contact_name: str, phone_number: str,
                 call_type: str, duration: int = 0, notes: str = None,
                 tags: List[str] = None) -> int:
        """通話記録を追加"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO calls (contact_name, phone_number, call_type, duration, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (contact_name, phone_number, call_type, duration, notes)
            )
            call_id = cursor.lastrowid

            # タグがあれば追加
            if tags:
                for tag in tags:
                    conn.execute(
                        "INSERT INTO call_tags (call_id, tag) VALUES (?, ?)",
                        (call_id, tag)
                    )

            return call_id

    def get_call(self, call_id: int) -> Optional[Dict]:
        """通話記録を取得"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM calls WHERE id = ?", (call_id,)).fetchone()
            if row:
                # タグ取得
                tags = conn.execute(
                    "SELECT tag FROM call_tags WHERE call_id = ?",
                    (call_id,)
                ).fetchall()
                call = dict(row)
                call['tags'] = [t['tag'] for t in tags]
                return call
            return None

    def list_calls(self, limit: int = 50, call_type: str = None,
                   contact_name: str = None) -> List[Dict]:
        """通話記録一覧を取得"""
        with self.get_connection() as conn:
            query = "SELECT * FROM calls WHERE 1=1"
            params = []

            if call_type:
                query += " AND call_type = ?"
                params.append(call_type)

            if contact_name:
                query += " AND contact_name LIKE ?"
                params.append(f"%{contact_name}%")

            query += " ORDER BY call_time DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            calls = []

            for row in rows:
                call = dict(row)
                tags = conn.execute(
                    "SELECT tag FROM call_tags WHERE call_id = ?",
                    (row['id'],)
                ).fetchall()
                call['tags'] = [t['tag'] for t in tags]
                calls.append(call)

            return calls

    def update_call(self, call_id: int, **kwargs) -> bool:
        """通話記録を更新"""
        with self.get_connection() as conn:
            fields = []
            params = []

            for key, value in kwargs.items():
                if key in ['contact_name', 'phone_number', 'call_type',
                          'duration', 'notes']:
                    fields.append(f"{key} = ?")
                    params.append(value)

            if not fields:
                return False

            fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(call_id)

            conn.execute(
                f"UPDATE calls SET {', '.join(fields)} WHERE id = ?",
                params
            )
            return True

    def delete_call(self, call_id: int) -> bool:
        """通話記録を削除"""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM calls WHERE id = ?", (call_id,))
            return cursor.rowcount > 0

    # 連絡先の操作

    def add_contact(self, name: str, phone_number: str, email: str = None,
                    tags: str = None, notes: str = None) -> int:
        """連絡先を追加"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO contacts (name, phone_number, email, tags, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, phone_number, email, tags, notes)
            )
            return cursor.lastrowid

    def get_contact(self, contact_id: int) -> Optional[Dict]:
        """連絡先を取得"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM contacts WHERE id = ?",
                (contact_id,)
            ).fetchone()
            return dict(row) if row else None

    def find_contact_by_phone(self, phone_number: str) -> Optional[Dict]:
        """電話番号で連絡先を検索"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM contacts WHERE phone_number = ?",
                (phone_number,)
            ).fetchone()
            return dict(row) if row else None

    def list_contacts(self, limit: int = 50, name: str = None) -> List[Dict]:
        """連絡先一覧を取得"""
        with self.get_connection() as conn:
            query = "SELECT * FROM contacts WHERE 1=1"
            params = []

            if name:
                query += " AND name LIKE ?"
                params.append(f"%{name}%")

            query += " ORDER BY name ASC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def update_contact(self, contact_id: int, **kwargs) -> bool:
        """連絡先を更新"""
        with self.get_connection() as conn:
            fields = []
            params = []

            for key, value in kwargs.items():
                if key in ['name', 'phone_number', 'email', 'tags', 'notes']:
                    fields.append(f"{key} = ?")
                    params.append(value)

            if not fields:
                return False

            fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(contact_id)

            conn.execute(
                f"UPDATE contacts SET {', '.join(fields)} WHERE id = ?",
                params
            )
            return True

    def delete_contact(self, contact_id: int) -> bool:
        """連絡先を削除"""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            return cursor.rowcount > 0

    # 統計情報

    def get_stats(self) -> Dict:
        """通話統計を取得"""
        with self.get_connection() as conn:
            stats = {}

            # 総通話数
            stats['total_calls'] = conn.execute(
                "SELECT COUNT(*) FROM calls"
            ).fetchone()[0]

            # タイプ別通話数
            stats['by_type'] = {}
            for row in conn.execute(
                "SELECT call_type, COUNT(*) as count FROM calls GROUP BY call_type"
            ).fetchall():
                stats['by_type'][row['call_type']] = row['count']

            # 連絡先数
            stats['total_contacts'] = conn.execute(
                "SELECT COUNT(*) FROM contacts"
            ).fetchone()[0]

            # 今月の通話時間（分）
            stats['this_month_minutes'] = conn.execute("""
                SELECT SUM(duration) / 60 FROM calls
                WHERE strftime('%Y-%m', call_time) = strftime('%Y-%m', 'now')
            """).fetchone()[0] or 0

            return stats


# エクスポート
__all__ = ['PhoneDB']
