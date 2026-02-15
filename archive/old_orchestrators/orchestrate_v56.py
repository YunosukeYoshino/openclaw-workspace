#!/usr/bin/env python3
"""
オーケストレーター V56 - 次期エージェントプロジェクト
自律的にエージェントを作成するスクリプト
"""

import os
import json
import traceback
from pathlib import Path

BASE_DIR = Path("/workspace")
AGENTS_DIR = BASE_DIR / "agents"
PROGRESS_FILE = BASE_DIR / "v56_progress.json"

# V56 プロジェクト定義
V56_PROJECTS = {
    "野球コーチング・フィジカルトレーニングエージェント (5個)": [
        {
            "name": "baseball-physical-coach-agent",
            "title": "野球フィジカルコーチエージェント",
            "description": "野球選手のフィジカルトレーニングを管理するエージェント",
            "details": {
                "ja": "野球選手のフィジカルトレーニング計画を策定・管理するエージェント。筋力トレーニング、有酸素運動、柔軟性トレーニングなどを含む包括的なフィジカルコーチング機能を提供する。",
                "en": "An agent that manages physical training for baseball players. Provides comprehensive physical coaching including strength training, aerobic exercise, and flexibility training."
            }
        },
        {
            "name": "baseball-strength-conditioning-agent",
            "title": "野球ストレングス&コンディショニングエージェント",
            "description": "野球選手のストレングストレーニングとコンディショニングを管理するエージェント",
            "details": {
                "ja": "野球選手のストレングストレーニングとコンディショニングプログラムを管理するエージェント。スプリント、プライオメトリクス、ウェイトトレーニングなどのメソッドを統合する。",
                "en": "An agent that manages strength training and conditioning programs for baseball players. Integrates methods like sprint training, plyometrics, and weight training."
            }
        },
        {
            "name": "baseball-injury-rehab-agent",
            "title": "野球怪我リハビリエージェント",
            "description": "野球選手の怪我リハビリテーションを管理するエージェント",
            "details": {
                "ja": "野球選手の怪我リハビリテーションプログラムを管理するエージェント。怪我の種類、進行状況、医師の指示に基づいたリハビリ計画を策定・追跡する。",
                "en": "An agent that manages injury rehabilitation programs for baseball players. Creates and tracks rehabilitation plans based on injury type, progress, and medical guidance."
            }
        },
        {
            "name": "baseball-flexibility-training-agent",
            "title": "野球柔軟性トレーニングエージェント",
            "description": "野球選手の柔軟性トレーニングを管理するエージェント",
            "details": {
                "ja": "野球選手の柔軟性トレーニングプログラムを管理するエージェント。ストレッチ、ヨガ、可動域改善エクササイズなどを含む。",
                "en": "An agent that manages flexibility training programs for baseball players. Includes stretching, yoga, and range of motion exercises."
            }
        },
        {
            "name": "baseball-mental-performance-agent",
            "title": "野球メンタルパフォーマンスエージェント",
            "description": "野球選手のメンタルトレーニングとパフォーマンス強化を管理するエージェント",
            "details": {
                "ja": "野球選手のメンタルトレーニングとパフォーマンス強化を管理するエージェント。集中力、自信、ストレス管理、ビジュアライゼーションなどのメンタルスキルを向上させる。",
                "en": "An agent that manages mental training and performance enhancement for baseball players. Improves mental skills such as focus, confidence, stress management, and visualization."
            }
        },
    ],
    "ゲームライブ配信・実況エージェント (5個)": [
        {
            "name": "game-stream-commentator-agent",
            "title": "ゲームストリーム実況エージェント",
            "description": "ゲームライブ配信の実況を管理するエージェント",
            "details": {
                "ja": "ゲームライブ配信の実況を管理するエージェント。AIによる実況生成、キーワード検出、ハイライト自動生成機能を提供する。",
                "en": "An agent that manages game live streaming commentary. Provides AI-powered commentary generation, keyword detection, and automatic highlight creation."
            }
        },
        {
            "name": "game-caster-scheduler-agent",
            "title": "ゲームキャスタースケジューラーエージェント",
            "description": "ゲーム配信キャスターのスケジュールを管理するエージェント",
            "details": {
                "ja": "ゲーム配信キャスターのスケジュールを管理するエージェント。キャスターの空き状況、配信スケジュール、マッチング機能を提供する。",
                "en": "An agent that manages game streamer schedules. Provides caster availability, streaming schedules, and matching functionality."
            }
        },
        {
            "name": "game-live-qa-agent",
            "title": "ゲームライブQ&Aエージェント",
            "description": "ゲームライブ配信のQ&Aを管理するエージェント",
            "details": {
                "ja": "ゲームライブ配信のQ&Aを管理するエージェント。視聴者からの質問収集、回答生成、優先順位管理機能を提供する。",
                "en": "An agent that manages Q&A in game live streaming. Provides question collection from viewers, answer generation, and priority management."
            }
        },
        {
            "name": "game-stream-recorder-agent",
            "title": "ゲームストリームレコーダーエージェント",
            "description": "ゲームライブ配信の録画・保存を管理するエージェント",
            "details": {
                "ja": "ゲームライブ配信の録画・保存を管理するエージェント。自動録画、クラウド保存、アーカイブ管理機能を提供する。",
                "en": "An agent that manages recording and storage of game live streams. Provides automatic recording, cloud storage, and archive management."
            }
        },
        {
            "name": "game-stream-analytics-agent",
            "title": "ゲームストリームアナリティクスエージェント",
            "description": "ゲームライブ配信の分析を管理するエージェント",
            "details": {
                "ja": "ゲームライブ配信の分析を管理するエージェント。視聴者数、エンゲージメント、収益、ピーク時間などの分析を提供する。",
                "en": "An agent that manages game live stream analytics. Provides analysis of viewer counts, engagement, revenue, and peak times."
            }
        },
    ],
    "えっちコンテンツAI動画生成・編集エージェント (5個)": [
        {
            "name": "erotic-ai-video-gen-agent",
            "title": "えっちAI動画生成エージェント",
            "description": "AIによるえっちコンテンツ動画の生成を管理するエージェント",
            "details": {
                "ja": "AIによるえっちコンテンツ動画の生成を管理するエージェント。テキストから動画、画像から動画、スタイル変換などの機能を提供する。",
                "en": "An agent that manages AI-generated erotic content videos. Provides features such as text-to-video, image-to-video, and style transfer."
            }
        },
        {
            "name": "erotic-ai-video-editor-agent",
            "title": "えっちAI動画編集エージェント",
            "description": "AIによるえっちコンテンツ動画の編集を管理するエージェント",
            "details": {
                "ja": "AIによるえっちコンテンツ動画の編集を管理するエージェント。カット編集、トランジション、エフェクト追加などの機能を提供する。",
                "en": "An agent that manages AI editing of erotic content videos. Provides features such as cut editing, transitions, and effect addition."
            }
        },
        {
            "name": "erotic-ai-video-upscaler-agent",
            "title": "えっちAI動画アップスケーラーエージェント",
            "description": "AIによるえっちコンテンツ動画の高画質化を管理するエージェント",
            "details": {
                "ja": "AIによるえっちコンテンツ動画の高画質化を管理するエージェント。解像度向上、ノイズ除去、鮮明化などの機能を提供する。",
                "en": "An agent that manages AI upscaling of erotic content videos. Provides features such as resolution enhancement, noise reduction, and sharpening."
            }
        },
        {
            "name": "erotic-ai-video-filler-agent",
            "title": "えっちAI動画フィラーエージェント",
            "description": "AIによるえっちコンテンツ動画の補間・補完を管理するエージェント",
            "details": {
                "ja": "AIによるえっちコンテンツ動画の補間・補完を管理するエージェント。フレーム補間、欠損修復、長さ調整などの機能を提供する。",
                "en": "An agent that manages AI interpolation and completion of erotic content videos. Provides features such as frame interpolation, missing data repair, and length adjustment."
            }
        },
        {
            "name": "erotic-ai-video-stylizer-agent",
            "title": "えっちAI動画スタイライザーエージェント",
            "description": "AIによるえっちコンテンツ動画のスタイル変換を管理するエージェント",
            "details": {
                "ja": "AIによるえっちコンテンツ動画のスタイル変換を管理するエージェント。アニメ風、レトロ風、アート風などのスタイル変換機能を提供する。",
                "en": "An agent that manages AI style transformation of erotic content videos. Provides style conversion features such as anime style, retro style, and art style."
            }
        },
    ],
    "サーバーレス・エッジコンピューティングエージェント (5個)": [
        {
            "name": "edge-function-manager-agent",
            "title": "エッジファンクションマネージャーエージェント",
            "description": "エッジコンピューティングの関数管理を担当するエージェント",
            "details": {
                "ja": "エッジコンピューティングの関数管理を担当するエージェント。デプロイ、スケーリング、バージョン管理、モニタリングなどの機能を提供する。",
                "en": "An agent responsible for managing edge computing functions. Provides features such as deployment, scaling, version management, and monitoring."
            }
        },
        {
            "name": "edge-cdn-manager-agent",
            "title": "エッジCDNマネージャーエージェント",
            "description": "エッジコンテンツデリバリーネットワークの管理を担当するエージェント",
            "details": {
                "ja": "エッジコンテンツデリバリーネットワークの管理を担当するエージェント。キャッシング、配信最適化、オリジン管理などの機能を提供する。",
                "en": "An agent responsible for managing edge content delivery networks. Provides features such as caching, delivery optimization, and origin management."
            }
        },
        {
            "name": "edge-worker-orchestrator-agent",
            "title": "エッジワーカーオーケストレーターエージェント",
            "description": "エッジワーカーのオーケストレーションを担当するエージェント",
            "details": {
                "ja": "エッジワーカーのオーケストレーションを担当するエージェント。タスク分散、負荷分散、フェイルオーバーなどの機能を提供する。",
                "en": "An agent responsible for orchestrating edge workers. Provides features such as task distribution, load balancing, and failover."
            }
        },
        {
            "name": "edge-latency-optimizer-agent",
            "title": "エッジレイテンシオプティマイザーエージェント",
            "description": "エッジ環境のレイテンシ最適化を担当するエージェント",
            "details": {
                "ja": "エッジ環境のレイテンシ最適化を担当するエージェント。ルート最適化、キャッシュ戦略、プリフェッチなどの機能を提供する。",
                "en": "An agent responsible for optimizing latency in edge environments. Provides features such as route optimization, caching strategies, and prefetching."
            }
        },
        {
            "name": "edge-resource-scaler-agent",
            "title": "エッジリソーススケーラーエージェント",
            "description": "エッジ環境のリソーススケーリングを担当するエージェント",
            "details": {
                "ja": "エッジ環境のリソーススケーリングを担当するエージェント。自動スケーリング、コスト最適化、リソース監視などの機能を提供する。",
                "en": "An agent responsible for resource scaling in edge environments. Provides features such as auto-scaling, cost optimization, and resource monitoring."
            }
        },
    ],
    "セキュリティログ・監査エージェント (5個)": [
        {
            "name": "security-log-collector-agent",
            "title": "セキュリティログコレクターエージェント",
            "description": "セキュリティログの収集・管理を担当するエージェント",
            "details": {
                "ja": "セキュリティログの収集・管理を担当するエージェント。複数ソースからのログ集約、正規化、インデックス化などの機能を提供する。",
                "en": "An agent responsible for collecting and managing security logs. Provides features such as log aggregation from multiple sources, normalization, and indexing."
            }
        },
        {
            "name": "log-forensics-agent",
            "title": "ログフォレンジックエージェント",
            "description": "ログのフォレンジック分析を担当するエージェント",
            "details": {
                "ja": "ログのフォレンジック分析を担当するエージェント。異常検知、タイムライン構築、証拠収集などの機能を提供する。",
                "en": "An agent responsible for log forensic analysis. Provides features such as anomaly detection, timeline construction, and evidence collection."
            }
        },
        {
            "name": "audit-reporter-agent",
            "title": "監査レポーターエージェント",
            "description": "監査レポートの生成・管理を担当するエージェント",
            "details": {
                "ja": "監査レポートの生成・管理を担当するエージェント。コンプライアンスチェック、レポート自動生成、配信などの機能を提供する。",
                "en": "An agent responsible for generating and managing audit reports. Provides features such as compliance checks, automatic report generation, and distribution."
            }
        },
        {
            "name": "compliance-monitor-agent",
            "title": "コンプライアンスモニターエージェント",
            "description": "コンプライアンスの監視・管理を担当するエージェント",
            "details": {
                "ja": "コンプライアンスの監視・管理を担当するエージェント。規制要件チェック、違反検知、改善提案などの機能を提供する。",
                "en": "An agent responsible for monitoring and managing compliance. Provides features such as regulatory requirement checks, violation detection, and improvement recommendations."
            }
        },
        {
            "name": "security-incident-logger-agent",
            "title": "セキュリティインシデントロガーエージェント",
            "description": "セキュリティインシデントのログ記録を担当するエージェント",
            "details": {
                "ja": "セキュリティインシデントのログ記録を担当するエージェント。インシデント記録、分類、追跡、レポートなどの機能を提供する。",
                "en": "An agent responsible for logging security incidents. Provides features such as incident recording, classification, tracking, and reporting."
            }
        },
    ],
}


def load_progress():
    """進捗ファイルを読み込む"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "completed": [],
        "in_progress": None,
        "total_agents": sum(len(agents) for agents in V56_PROJECTS.values()),
        "completed_count": 0,
    }


def save_progress(progress):
    """進捗ファイルを保存する"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def create_agent_dir(agent_name):
    """エージェントディレクトリを作成する"""
    agent_dir = AGENTS_DIR / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir


def sanitize_agent_name(agent_name):
    """エージェント名をサニタイズする"""
    return agent_name.replace('-', '_')


def to_class_name(agent_name):
    """エージェント名をクラス名に変換する"""
    return ''.join(word.title() for word in agent_name.replace('-', '_').split('_'))


def generate_agent_py(agent_name, title, description, details):
    """agent.pyを生成する"""
    table_name = sanitize_agent_name(agent_name)
    class_name = to_class_name(agent_name)

    sql_create_main = "CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, metadata TEXT, status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)".format(table_name)
    sql_create_tags = "CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)"
    sql_create_junction = "CREATE TABLE IF NOT EXISTS {}_tags ({}_id INTEGER, tag_id INTEGER, PRIMARY KEY ({}_id, tag_id), FOREIGN KEY ({}_id) REFERENCES {}(id), FOREIGN KEY (tag_id) REFERENCES tags(id))".format(table_name, table_name, table_name, table_name, table_name)

    sql_insert_main = "INSERT INTO {} (title, content, metadata) VALUES (?, ?, ?)".format(table_name)
    sql_insert_tag = "INSERT OR IGNORE INTO tags (name) VALUES (?)"
    sql_select_tag_id = "SELECT id FROM tags WHERE name = ?"
    sql_insert_junction = "INSERT INTO {}_tags ({}_id, tag_id) VALUES (?, ?)".format(table_name, table_name)

    sql_select_all = "SELECT id, title, content, metadata, status, created_at, updated_at FROM {} ORDER BY created_at DESC LIMIT ?".format(table_name)
    sql_select_one = "SELECT id, title, content, metadata, status, created_at, updated_at FROM {} WHERE id = ?".format(table_name)
    sql_search = "SELECT id, title, content, metadata, status, created_at, updated_at FROM " + table_name + " WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC"
    sql_count_all = "SELECT COUNT(*) FROM {}".format(table_name)
    sql_count_active = "SELECT COUNT(*) FROM {} WHERE status = 'active'".format(table_name)

    sql_delete_main = "DELETE FROM {} WHERE id = ?".format(table_name)
    sql_delete_junction = "DELETE FROM {}_tags WHERE {}_id = ?".format(table_name, table_name)

    sql_select_by_tag = "SELECT e.id, e.title, e.content, e.metadata, e.status, e.created_at, e.updated_at FROM " + table_name + " e INNER JOIN " + table_name + "_tags et ON e.id = et." + table_name + "_id INNER JOIN tags t ON et.tag_id = t.id WHERE t.name = ? ORDER BY e.created_at DESC"

    template = f'''#!/usr/bin/env python3
"""
{title} - {description}
{details.get('en', '')}
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

class {class_name}Agent:
    """{title}"""

    def __init__(self, db_path: str = "{agent_name}.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("{sql_create_main}")
        cursor.execute("{sql_create_tags}")
        cursor.execute("{sql_create_junction}")

        self.conn.commit()

    def add_entry(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> int:
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute("{sql_insert_main}", (title, content, metadata_json))

        entry_id = cursor.lastrowid

        if tags:
            for tag_name in tags:
                cursor.execute("{sql_insert_tag}", (tag_name,))
                cursor.execute("{sql_select_tag_id}", (tag_name,))
                tag_id = cursor.fetchone()[0]
                cursor.execute("{sql_insert_junction}", (entry_id, tag_id))

        self.conn.commit()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("{sql_select_one}", (entry_id,))
        row = cursor.fetchone()
        if row:
            return {{
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }}
        return None

    def list_entries(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("{sql_select_all}", (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({{
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }})

        return results

    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        search_pattern = "%" + query + "%"
        cursor.execute("{sql_search}", (search_pattern, search_pattern))

        results = []
        for row in cursor.fetchall():
            results.append({{
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }})

        return results

    def delete_entry(self, entry_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("{sql_delete_junction}", (entry_id,))
        cursor.execute("{sql_delete_main}", (entry_id,))

        self.conn.commit()
        return cursor.rowcount > 0

    def get_entries_by_tag(self, tag_name: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("{sql_select_by_tag}", (tag_name,))

        results = []
        for row in cursor.fetchall():
            results.append({{
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }})

        return results

    def get_stats(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()

        cursor.execute("{sql_count_all}")
        total_entries = cursor.fetchone()[0]

        cursor.execute("{sql_count_active}")
        active_entries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tags")
        total_tags = cursor.fetchone()[0]

        return {{
            "total_entries": total_entries,
            "active_entries": active_entries,
            "total_tags": total_tags,
        }}

    def close(self):
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    with {class_name}Agent() as agent:
        print(f"{agent_name} エージェント初期化完了")
        stats = agent.get_stats()
        print(f"統計情報: {{stats}}")
'''
    return template


def generate_db_py(agent_name):
    """db.pyを生成する"""
    table_name = sanitize_agent_name(agent_name)

    sql_create_main = "CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, metadata TEXT, status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)".format(table_name)
    sql_create_tags = "CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)"
    sql_create_junction = "CREATE TABLE IF NOT EXISTS {}_tags ({}_id INTEGER NOT NULL, tag_id INTEGER NOT NULL, PRIMARY KEY ({}_id, tag_id), FOREIGN KEY ({}_id) REFERENCES {}(id) ON DELETE CASCADE, FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE)".format(table_name, table_name, table_name, table_name, table_name)

    template = f'''#!/usr/bin/env python3
"""
{agent_name} - データベースモジュール
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DB_PATH = Path(__file__).parent / "{agent_name}.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("{sql_create_main}")
    cursor.execute("{sql_create_tags}")
    cursor.execute("{sql_create_junction}")

    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_created_at ON {table_name}(created_at)')
    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_status ON {table_name}(status)')

    conn.commit()
    conn.close()

def create_entry(title: str, content: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute(f"INSERT INTO {table_name} (title, content, metadata) VALUES (?, ?, ?)", (title, content, metadata_json))

        entry_id = cursor.lastrowid

        if tags:
            for tag_name in tags:
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag_id = cursor.fetchone()[0]
                cursor.execute(f"INSERT INTO {table_name}_tags ({table_name}_id, tag_id) VALUES (?, ?)", (entry_id, tag_id))

        conn.commit()
        return entry_id

def get_entry(entry_id: int) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, title, content, metadata, status, created_at, updated_at FROM {table_name} WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def list_entries(status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if status:
            cursor.execute(f"SELECT id, title, content, metadata, status, created_at, updated_at FROM {table_name} WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (status, limit, offset))
        else:
            cursor.execute(f"SELECT id, title, content, metadata, status, created_at, updated_at FROM {table_name} ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))

        return [dict(row) for row in cursor.fetchall()]

def search_entries(query: str, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        search_pattern = "%" + query + "%"
        cursor.execute(f"SELECT id, title, content, metadata, status, created_at, updated_at FROM {table_name} WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT ?", (search_pattern, search_pattern, limit))

        return [dict(row) for row in cursor.fetchall()]

def update_entry(entry_id: int, **kwargs) -> bool:
    valid_fields = ["title", "content", "metadata", "status"]
    update_fields = {{k: v for k, v in kwargs.items() if k in valid_fields}}

    if not update_fields:
        return False

    if "metadata" in update_fields and update_fields["metadata"]:
        update_fields["metadata"] = json.dumps(update_fields["metadata"])

    set_clause = ", ".join([f"{{k}} = ?" for k in update_fields.keys()])
    values = list(update_fields.values())
    values.append(entry_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table_name} SET {{set_clause}}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
        return cursor.rowcount > 0

def delete_entry(entry_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}_tags WHERE {table_name}_id = ?", (entry_id,))
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0

def add_tag_to_entry(entry_id: int, tag_name: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        row = cursor.fetchone()
        if not row:
            return False

        tag_id = row[0]
        cursor.execute(f"INSERT OR IGNORE INTO {table_name}_tags ({table_name}_id, tag_id) VALUES (?, ?)", (entry_id, tag_id))
        conn.commit()
        return True

def remove_tag_from_entry(entry_id: int, tag_name: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}_tags WHERE {table_name}_id = ? AND tag_id = (SELECT id FROM tags WHERE name = ?)", (entry_id, tag_name))
        conn.commit()
        return cursor.rowcount > 0

def get_all_tags() -> List[str]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM tags ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

def get_entries_by_tag(tag_name: str, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT e.id, e.title, e.content, e.metadata, e.status, e.created_at, e.updated_at FROM {table_name} e INNER JOIN {table_name}_tags et ON e.id = et.{table_name}_id INNER JOIN tags t ON et.tag_id = t.id WHERE t.name = ? ORDER BY e.created_at DESC LIMIT ?", (tag_name, limit))

        return [dict(row) for row in cursor.fetchall()]

def get_stats() -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_entries = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE status = 'active'")
        active_entries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tags")
        total_tags = cursor.fetchone()[0]

        cursor.execute(f"SELECT name, COUNT(*) as count FROM {table_name}_tags INNER JOIN tags ON {table_name}_tags.tag_id = tags.id GROUP BY name ORDER BY count DESC LIMIT 10")
        top_tags = [{{"name": row[0], "count": row[1]}} for row in cursor.fetchall()]

        return {{
            "total_entries": total_entries,
            "active_entries": active_entries,
            "archived_entries": total_entries - active_entries,
            "total_tags": total_tags,
            "top_tags": top_tags,
        }}

if __name__ == "__main__":
    init_db()
    print("データベース初期化完了")
    print("統計情報:", get_stats())
'''
    return template


def generate_discord_py(agent_name, title):
    """discord.pyを生成する"""
    table_name = sanitize_agent_name(agent_name)
    class_name = to_class_name(agent_name)

    template = f'''#!/usr/bin/env python3
"""
{title} - Discord Bot Integration
"""

import discord
from discord.ext import commands
from typing import Optional, List, Dict, Any
import json

from db import (
    create_entry,
    get_entry,
    list_entries,
    search_entries,
    update_entry,
    delete_entry,
    add_tag_to_entry,
    remove_tag_from_entry,
    get_all_tags,
    get_entries_by_tag,
    get_stats,
)


class {class_name}DiscordBot(commands.Bot):
    """{title} - Discord Bot"""

    def __init__(self, command_prefix: str = "!", intents: Optional[discord.Intents] = None):
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.prefix = command_prefix

    async def setup_hook(self):
        print(f"{{self.__class__.__name__}} のセットアップ中...")

    async def on_ready(self):
        print(f"{{self.user}} がログインしました！")
        print(f"サーバー数: {{len(self.guilds)}}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.process_commands(message)

    @commands.command()
    async def stats(self, ctx: commands.Context):
        stats_data = get_stats()

        embed = discord.Embed(title=f"{title} 統計情報", color=discord.Color.blue())
        embed.add_field(name="総エントリー数", value=stats_data["total_entries"], inline=True)
        embed.add_field(name="アクティブエントリー", value=stats_data["active_entries"], inline=True)
        embed.add_field(name="総タグ数", value=stats_data["total_tags"], inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def list(self, ctx: commands.Context, limit: int = 10):
        entries = list_entries(limit=limit)

        if not entries:
            await ctx.send("エントリーが見つかりませんでした。")
            return

        embed = discord.Embed(title="エントリーリスト (最新" + str(len(entries)) + "件)", color=discord.Color.green())

        for entry in entries[:10]:
            title = entry["title"][:50] + "..." if len(entry["title"]) > 50 else entry["title"]
            status_emoji = "✅" if entry["status"] == "active" else "📦"
            embed.add_field(name=status_emoji + " #" + str(entry["id"]) + " - " + title,
                           value="作成: " + entry["created_at"], inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def search(self, ctx: commands.Context, *, query: str):
        if not query:
            await ctx.send("検索キーワードを指定してください。")
            return

        entries = search_entries(query, limit=10)

        if not entries:
            await ctx.send("検索結果が見つかりませんでした。")
            return

        embed = discord.Embed(title="検索結果: " + query, color=discord.Color.orange())

        for entry in entries[:5]:
            content = entry["content"][:200] + "..." if len(entry["content"]) > 200 else entry["content"]
            embed.add_field(name="#" + str(entry["id"]) + " - " + entry["title"], value=content, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx: commands.Context, title: str, *, content: str = ""):
        if not title:
            await ctx.send("タイトルを指定してください。")
            return

        if not content:
            content = "詳細なし"

        entry_id = create_entry(title=title, content=content)

        embed = discord.Embed(title="エントリーを作成しました", color=discord.Color.green())
        embed.add_field(name="ID", value=entry_id, inline=True)
        embed.add_field(name="タイトル", value=title, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def show(self, ctx: commands.Context, entry_id: int):
        entry = get_entry(entry_id)

        if not entry:
            await ctx.send("エントリー #" + str(entry_id) + " が見つかりませんでした。")
            return

        status_emoji = "✅" if entry["status"] == "active" else "📦"

        embed = discord.Embed(title=status_emoji + " " + entry["title"], color=discord.Color.blue())
        embed.add_field(name="ID", value=entry["id"], inline=True)
        embed.add_field(name="ステータス", value=entry["status"], inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def tags(self, ctx: commands.Context):
        tags = get_all_tags()

        if not tags:
            await ctx.send("タグがありません。")
            return

        embed = discord.Embed(title="タグ一覧 (" + str(len(tags)) + "件)", color=discord.Color.purple())
        embed.add_field(name="タグ", value=", ".join(tags[:30]), inline=False)

        await ctx.send(embed=embed)


def run_bot(token: str):
    bot = {class_name}DiscordBot(command_prefix="!")
    bot.run(token)


if __name__ == "__main__":
    import os
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("DISCORD_BOT_TOKEN環境変数を設定してください。")
    else:
        run_bot(token)
'''
    return template


def generate_readme_md(agent_name, title, description, details):
    """README.mdを生成する"""
    class_name = to_class_name(agent_name)

    template = f'''# {title}

{description}

{details.get('en', '')}

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd {agent_name}
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import {class_name}

agent = {class_name}()
entry_id = agent.add_entry("サンプル", "これはサンプルエントリーです", tags=["sample", "test"])
print(f"作成されたエントリーID: {{entry_id}}")
agent.close()
```

### Discord Bot

```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
python discord.py
```

## ライセンス

MIT License
'''
    return template


def generate_requirements_txt():
    """requirements.txtを生成する"""
    return '''# Core dependencies
discord.py>=2.3.2

# Development dependencies
pytest>=7.4.3
pytest-asyncio>=0.21.1
black>=23.12.0
flake8>=6.1.0
mypy>=1.7.1
'''


def create_agent(agent_name, title, description, details):
    """エージェントを作成する"""
    agent_dir = create_agent_dir(agent_name)

    files = {
        "agent.py": generate_agent_py(agent_name, title, description, details),
        "db.py": generate_db_py(agent_name),
        "discord.py": generate_discord_py(agent_name, title),
        "README.md": generate_readme_md(agent_name, title, description, details),
        "requirements.txt": generate_requirements_txt(),
    }

    for filename, content in files.items():
        file_path = agent_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"  ✓ {agent_name}: 5 files created")
    return agent_name


def main():
    """メイン処理"""
    print("=" * 60)
    print("オーケストレーター V56 - 次期エージェントプロジェクト")
    print("=" * 60)

    progress = load_progress()
    total_agents = progress["total_agents"]
    completed_count = progress["completed_count"]
    completed_agents = progress.get("completed", [])

    print(f"\\n進捗: {completed_count}/{total_agents} エージェント完了")

    if completed_count >= total_agents:
        print("\\n✅ V56 プロジェクトはすでに完了しています！")
        return

    all_agents = []
    for project_name, agents in V56_PROJECTS.items():
        print(f"\\n📁 {project_name}")
        for agent_data in agents:
            all_agents.append((project_name, agent_data))

    for project_name, agent_data in all_agents:
        agent_name = agent_data["name"]

        if agent_name in completed_agents:
            print(f"  ⊙ {agent_name}: すでに完了")
            continue

        try:
            create_agent(
                agent_name,
                agent_data["title"],
                agent_data["description"],
                agent_data["details"]
            )

            completed_agents.append(agent_name)
            progress["completed"] = completed_agents
            progress["completed_count"] = len(completed_agents)
            progress["in_progress"] = None
            save_progress(progress)

        except Exception as e:
            print(f"  ✗ {agent_name}: エラー発生")
            print(f"    Error: {str(e)}")
            traceback.print_exc()
            continue

    print("\\n" + "=" * 60)
    print(f"✅ V56 プロジェクト完了！")
    print(f"総エージェント数: {progress['completed_count']}/{progress['total_agents']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
