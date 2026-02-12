#!/usr/bin/env python3
"""
Webhook Agent - Webhook 管理 (Webhook URL Registration & Event Logging)
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "webhook.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Webhook設定テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS webhooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        webhook_type TEXT CHECK(webhook_type IN ('discord', 'slack', 'telegram', 'custom', 'generic')),
        description TEXT,
        secret TEXT,
        enabled INTEGER DEFAULT 1,
        rate_limit INTEGER DEFAULT 60,
        timeout_seconds INTEGER DEFAULT 10,
        headers TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Webhookイベントログテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS webhook_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        webhook_id INTEGER,
        event_type TEXT,
        payload TEXT,
        response_status INTEGER,
        response_body TEXT,
        duration_ms INTEGER DEFAULT 0,
        success INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
    )
    ''')

    # イベント統計テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS webhook_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        webhook_id INTEGER,
        date TEXT,
        total_sent INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        failed_count INTEGER DEFAULT 0,
        avg_duration_ms REAL DEFAULT 0,
        FOREIGN KEY (webhook_id) REFERENCES webhooks(id),
        UNIQUE(webhook_id, date)
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_webhooks_updated_at
    AFTER UPDATE ON webhooks
    BEGIN
        UPDATE webhooks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhooks_enabled ON webhooks(enabled)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhooks_type ON webhooks(webhook_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhook_events_webhook_id ON webhook_events(webhook_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhook_events_created_at ON webhook_events(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhook_events_success ON webhook_events(success)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_webhook_stats_date ON webhook_stats(date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_webhook(name, url, webhook_type='generic', description=None, secret=None,
                enabled=1, rate_limit=60, timeout_seconds=10, headers=None):
    """Webhook追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    headers_json = None
    if headers:
        import json
        headers_json = json.dumps(headers)

    cursor.execute('''
    INSERT INTO webhooks (name, url, webhook_type, description, secret, enabled, rate_limit, timeout_seconds, headers)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, url, webhook_type, description, secret, enabled, rate_limit, timeout_seconds, headers_json))

    webhook_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return webhook_id

def get_webhook(webhook_id):
    """Webhook取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, url, webhook_type, description, secret, enabled,
           rate_limit, timeout_seconds, headers, created_at, updated_at
    FROM webhooks WHERE id = ?
    ''', (webhook_id,))

    webhook = cursor.fetchone()
    conn.close()
    return webhook

def list_webhooks(enabled_only=False, webhook_type=None):
    """Webhook一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, url, webhook_type, description, enabled, created_at, updated_at
    FROM webhooks
    '''

    conditions = []
    params = []

    if enabled_only:
        conditions.append("enabled = 1")

    if webhook_type:
        conditions.append("webhook_type = ?")
        params.append(webhook_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += ' ORDER BY created_at DESC'

    cursor.execute(query, params)
    webhooks = cursor.fetchall()
    conn.close()
    return webhooks

def update_webhook(webhook_id, **kwargs):
    """Webhook更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    allowed_fields = ['name', 'url', 'webhook_type', 'description', 'secret',
                      'enabled', 'rate_limit', 'timeout_seconds', 'headers']

    set_clause = []
    params = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            if field == 'headers' and value:
                import json
                set_clause.append(f"{field} = ?")
                params.append(json.dumps(value))
            elif field == 'headers':
                set_clause.append(f"{field} = ?")
                params.append(None)
            else:
                set_clause.append(f"{field} = ?")
                params.append(value)

    if not set_clause:
        conn.close()
        return False

    params.append(webhook_id)
    query = f"UPDATE webhooks SET {', '.join(set_clause)} WHERE id = ?"
    cursor.execute(query, params)

    conn.commit()
    conn.close()
    return True

def delete_webhook(webhook_id):
    """Webhook削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM webhooks WHERE id = ?', (webhook_id,))
    cursor.execute('DELETE FROM webhook_events WHERE webhook_id = ?', (webhook_id,))
    cursor.execute('DELETE FROM webhook_stats WHERE webhook_id = ?', (webhook_id,))

    conn.commit()
    conn.close()

def toggle_webhook(webhook_id):
    """Webhook有効/無効切り替え"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE webhooks SET enabled = NOT enabled WHERE id = ?
    ''', (webhook_id,))

    conn.commit()
    conn.close()

def log_webhook_event(webhook_id, event_type, payload, response_status=None, response_body=None,
                       duration_ms=0, success=0, error_message=None):
    """Webhookイベントログ記録"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    import json
    payload_json = json.dumps(payload) if payload else None
    response_json = json.dumps(response_body) if response_body else None

    cursor.execute('''
    INSERT INTO webhook_events
    (webhook_id, event_type, payload, response_status, response_body, duration_ms, success, error_message)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (webhook_id, event_type, payload_json, response_status, response_json, duration_ms, success, error_message))

    event_id = cursor.lastrowid

    # 統計更新
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
    INSERT OR IGNORE INTO webhook_stats (webhook_id, date, total_sent, success_count, failed_count, avg_duration_ms)
    VALUES (?, ?, 0, 0, 0, 0)
    ''', (webhook_id, today))

    cursor.execute('''
    UPDATE webhook_stats
    SET total_sent = total_sent + 1,
        success_count = success_count + ?,
        failed_count = failed_count + ?,
        avg_duration_ms = (avg_duration_ms * (total_sent - 1) + ?) / total_sent
    WHERE webhook_id = ? AND date = ?
    ''', (1 if success else 0, 0 if success else 1, duration_ms, webhook_id, today))

    conn.commit()
    conn.close()
    return event_id

def get_webhook_events(webhook_id=None, limit=50, success_only=None):
    """Webhookイベント履歴取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT e.id, e.webhook_id, w.name, e.event_type, e.response_status, e.duration_ms,
           e.success, e.error_message, e.created_at
    FROM webhook_events e
    JOIN webhooks w ON e.webhook_id = w.id
    '''

    conditions = []
    params = []

    if webhook_id:
        conditions.append("e.webhook_id = ?")
        params.append(webhook_id)

    if success_only is not None:
        conditions.append("e.success = ?")
        params.append(1 if success_only else 0)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += ' ORDER BY e.created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    events = cursor.fetchall()
    conn.close()
    return events

def get_webhook_stats(webhook_id=None, days=7):
    """Webhook統計取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT s.webhook_id, w.name, s.date, s.total_sent, s.success_count, s.failed_count, s.avg_duration_ms
    FROM webhook_stats s
    JOIN webhooks w ON s.webhook_id = w.id
    '''

    conditions = []
    params = []

    if webhook_id:
        conditions.append("s.webhook_id = ?")
        params.append(webhook_id)

    # 最近N日分
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    conditions.append("s.date >= ?")
    params.append(cutoff_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += ' ORDER BY s.date DESC, s.webhook_id'

    cursor.execute(query, params)
    stats = cursor.fetchall()
    conn.close()
    return stats

def get_webhook_summary():
    """Webhook全体サマリー"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    summary = {}

    # Webhook数
    cursor.execute('SELECT COUNT(*) FROM webhooks')
    summary['total_webhooks'] = cursor.fetchone()[0]

    # 有効Webhook数
    cursor.execute('SELECT COUNT(*) FROM webhooks WHERE enabled = 1')
    summary['enabled_webhooks'] = cursor.fetchone()[0]

    # タイプ別集計
    cursor.execute('''
    SELECT webhook_type, COUNT(*) FROM webhooks GROUP BY webhook_type
    ''')
    summary['by_type'] = dict(cursor.fetchall())

    # イベント総数
    cursor.execute('SELECT COUNT(*) FROM webhook_events')
    summary['total_events'] = cursor.fetchone()[0]

    # 成功/失敗
    cursor.execute('SELECT COUNT(*) FROM webhook_events WHERE success = 1')
    summary['success_events'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM webhook_events WHERE success = 0')
    summary['failed_events'] = cursor.fetchone()[0]

    # 平均送信時間
    cursor.execute('SELECT AVG(duration_ms) FROM webhook_events WHERE duration_ms > 0')
    result = cursor.fetchone()[0]
    summary['avg_duration_ms'] = round(result, 2) if result else 0

    # 最新イベント
    cursor.execute('''
    SELECT MAX(created_at) FROM webhook_events
    ''')
    summary['last_event'] = cursor.fetchone()[0]

    # 今日のイベント
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
    SELECT COUNT(*) FROM webhook_events WHERE DATE(created_at) = ?
    ''', (today,))
    summary['today_events'] = cursor.fetchone()[0]

    conn.close()
    return summary

def test_webhook_connection(webhook_id):
    """Webhook接続テスト（ローカル検証）"""
    webhook = get_webhook(webhook_id)

    if not webhook:
        return {'success': False, 'error': 'Webhook not found'}

    _, _, url, webhook_type, _, _, _, _, _, headers, _, _ = webhook

    import json
    headers_dict = json.loads(headers) if headers else {}

    test_result = {
        'webhook_id': webhook_id,
        'url': url,
        'webhook_type': webhook_type,
        'test': True
    }

    # URL検証
    if not url.startswith(('http://', 'https://')):
        return {**test_result, 'success': False, 'error': 'Invalid URL format'}

    return {**test_result, 'success': True, 'message': 'Valid webhook configuration'}

def cleanup_old_events(days=30):
    """古いイベントを削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
    DELETE FROM webhook_events WHERE created_at < ?
    ''', (cutoff_date,))

    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count

if __name__ == '__main__':
    init_db()
