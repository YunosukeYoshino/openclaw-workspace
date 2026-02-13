#!/usr/bin/env python3
"""
V27 Agent Generator - Creates all 25 agents for the V27 project
"""

import os
from pathlib import Path

AGENTS_DIR = Path("/workspace/agents")

# Agent configurations with their specific features
AGENT_CONFIGS = {
    "baseball-stadium-finder-agent": {
        "ja_desc": "野球スタジアム検索・情報エージェント",
        "en_desc": "Baseball Stadium Finder and Information Agent",
        "features": [
            "スタジアム検索・フィルタリング機能 / Stadium search and filtering",
            "座席エリア情報の提供 / Seat area information",
            "アクセス方法・交通手段の提案 / Access and transportation options",
            "周辺施設（飲食店、駐車場）の情報 / Nearby facilities (restaurants, parking)",
            "チケット価格帯の比較 / Ticket price comparison"
        ]
    },
    "baseball-ticket-optimizer-agent": {
        "ja_desc": "野球チケット最適化エージェント",
        "en_desc": "Baseball Ticket Optimizer Agent",
        "features": [
            "チケット価格の比較・最適化 / Ticket price comparison and optimization",
            "リアルタイム空席監視 / Real-time seat availability monitoring",
            "価格変動の予測 / Price fluctuation prediction",
            "購入タイミングの提案 / Purchase timing recommendations",
            "割引情報の収集・配信 / Discount information collection and delivery"
        ]
    },
    "baseball-food-beverage-agent": {
        "ja_desc": "野球スタジアムフード・ドリンクエージェント",
        "en_desc": "Baseball Stadium Food and Beverage Agent",
        "features": [
            "スタジアムフードメニューのカタログ / Stadium food menu catalog",
            "待ち時間の予測・監視 / Wait time prediction and monitoring",
            "事前注文機能の統合 / Pre-order integration",
            "人気メニューのランキング / Popular menu rankings",
            "食事タイミングの提案 / Meal timing recommendations"
        ]
    },
    "baseball-accessibility-agent": {
        "ja_desc": "野球スタジアムアクセシビリティエージェント",
        "en_desc": "Baseball Stadium Accessibility Agent",
        "features": [
            "車いす対応席の情報 / Wheelchair accessible seating information",
            "バリアフリー施設の案内 / Barrier-free facility guidance",
            "サポートサービスの予約 / Support service booking",
            "視覚・聴覚障害者支援情報 / Visual and hearing impairment support",
            "多言語対応サービス / Multi-language services"
        ]
    },
    "baseball-fan-experience-agent": {
        "ja_desc": "野球ファン体験エージェント",
        "en_desc": "Baseball Fan Experience Agent",
        "features": [
            "ファン体験イベントの案内 / Fan experience event information",
            "記念品・グッズ情報の収集 / Merchandise information collection",
            "スタジアムクイズ・ゲーム / Stadium quizzes and games",
            "AR/VR体験機能 / AR/VR experience features",
            "ファン参加型コンテンツ / Fan participation content"
        ]
    },
    "game-cross-save-agent": {
        "ja_desc": "ゲームクロスセーブエージェント",
        "en_desc": "Game Cross-Save Agent",
        "features": [
            "クロスプラットフォームセーブ同期 / Cross-platform save synchronization",
            "クラウドストレージ統合 / Cloud storage integration",
            "競合解決機能 / Conflict resolution",
            "同期履歴の追跡 / Sync history tracking",
            "手動/自動同期モード / Manual/automatic sync modes"
        ]
    },
    "game-achievement-sync-agent": {
        "ja_desc": "ゲーム実績同期エージェント",
        "en_desc": "Game Achievement Sync Agent",
        "features": [
            "実績・トロフィーの同期 / Achievement and trophy synchronization",
            "プラットフォーム間の統合表示 / Cross-platform unified display",
            "実績進捗の追跡 / Achievement progress tracking",
            "実績比較機能 / Achievement comparison",
            "実績統計の可視化 / Achievement statistics visualization"
        ]
    },
    "game-progression-sync-agent": {
        "ja_desc": "ゲーム進行状況同期エージェント",
        "en_desc": "Game Progression Sync Agent",
        "features": [
            "レベル・経験値の同期 / Level and experience synchronization",
            "装備・アイテムの同期 / Equipment and item synchronization",
            "アンロック状況の管理 / Unlock status management",
            "マルチデバイス進行管理 / Multi-device progress management",
            "同期ステータスの表示 / Sync status display"
        ]
    },
    "game-friends-unified-agent": {
        "ja_desc": "ゲームフレンド統合エージェント",
        "en_desc": "Game Friends Unified Agent",
        "features": [
            "統合フレンドリスト / Unified friend list",
            "オンライン状態の監視 / Online status monitoring",
            "クロスプラットフォーム招待 / Cross-platform invitations",
            "フレンド活動の追跡 / Friend activity tracking",
            "ソーシャル機能の統合 / Social feature integration"
        ]
    },
    "game-data-migration-agent": {
        "ja_desc": "ゲームデータ移行エージェント",
        "en_desc": "Game Data Migration Agent",
        "features": [
            "データ移行の自動化 / Automated data migration",
            "移行計画の作成 / Migration plan creation",
            "データ整合性の検証 / Data integrity verification",
            "移行ログの記録 / Migration log recording",
            "移行失敗時のロールバック / Rollback on migration failure"
        ]
    },
    "erotic-age-verification-agent": {
        "ja_desc": "えっち年齢認証エージェント",
        "en_desc": "Erotic Age Verification Agent",
        "features": [
            "年齢認証機能 / Age verification",
            "ID検証統合 / ID verification integration",
            "アクセス制限の実施 / Access restriction enforcement",
            "セッション管理 / Session management",
            "認証ログの記録 / Authentication log recording"
        ]
    },
    "erotic-content-filter-agent": {
        "ja_desc": "えっちコンテンツフィルターエージェント",
        "en_desc": "Erotic Content Filter Agent",
        "features": [
            "NSFWコンテンツ検出 / NSFW content detection",
            "AIベースのフィルタリング / AI-based filtering",
            "コンテンツカテゴリ分類 / Content categorization",
            "ユーザー設定に基づくフィルター / User-configurable filters",
            "誤検出の報告・修正 / False positive reporting and correction"
        ]
    },
    "erotic-privacy-guard-agent": {
        "ja_desc": "えっちプライバシーガードエージェント",
        "en_desc": "Erotic Privacy Guard Agent",
        "features": [
            "閲覧履歴の暗号化 / Encrypted browsing history",
            "検索履歴の保護 / Search history protection",
            "自動削除機能 / Auto-delete functionality",
            "プライベートモード / Private mode",
            "追跡防止機能 / Tracking prevention"
        ]
    },
    "erotic-safe-browsing-agent": {
        "ja_desc": "えっちセーフブラウジングエージェント",
        "en_desc": "Erotic Safe Browsing Agent",
        "features": [
            "安全なサイト判定 / Safe site detection",
            "詐欺サイト検出 / Scam site detection",
            "マルウェアスキャン / Malware scanning",
            "フィッシング対策 / Phishing protection",
            "安全なダウンロード / Safe downloads"
        ]
    },
    "erotic-data-compliance-agent": {
        "ja_desc": "えっちデータコンプライアンスエージェント",
        "en_desc": "Erotic Data Compliance Agent",
        "features": [
            "規制対応の監査 / Regulation compliance audit",
            "データポリシーの管理 / Data policy management",
            "同意管理 / Consent management",
            "データリクエスト処理 / Data request processing",
            "コンプライアンスレポート / Compliance reporting"
        ]
    },
    "baseball-training-plan-agent": {
        "ja_desc": "野球トレーニングプランエージェント",
        "en_desc": "Baseball Training Plan Agent",
        "features": [
            "パーソナライズドトレーニングプラン / Personalized training plans",
            "スキルレベル評価 / Skill level assessment",
            "目標設定機能 / Goal setting",
            "進捗追跡 / Progress tracking",
            "プラン調整・最適化 / Plan adjustment and optimization"
        ]
    },
    "baseball-drill-library-agent": {
        "ja_desc": "野球ドリルライブラリエージェント",
        "en_desc": "Baseball Drill Library Agent",
        "features": [
            "ドリルライブラリ / Drill library",
            "動画チュートリアル / Video tutorials",
            "難易度別分類 / Difficulty-based classification",
            "目的別ドリル検索 / Purpose-based drill search",
            "お気に入り機能 / Favorites"
        ]
    },
    "baseball-form-coach-agent": {
        "ja_desc": "野球フォームコーチエージェント",
        "en_desc": "Baseball Form Coach Agent",
        "features": [
            "フォーム分析 / Form analysis",
            "改善提案 / Improvement recommendations",
            "ビデオフィードバック / Video feedback",
            "進捗追跡 / Progress tracking",
            "コーチングチャット / Coaching chat"
        ]
    },
    "baseball-fitness-tracker-agent": {
        "ja_desc": "野球フィットネストラッカーエージェント",
        "en_desc": "Baseball Fitness Tracker Agent",
        "features": [
            "フィットネスデータ追跡 / Fitness data tracking",
            "ウェアラブル統合 / Wearable integration",
            "トレーニングログ / Training logs",
            "目標設定 / Goal setting",
            "分析・レポート / Analysis and reporting"
        ]
    },
    "baseball-skill-assessment-agent": {
        "ja_desc": "野球スキル評価エージェント",
        "en_desc": "Baseball Skill Assessment Agent",
        "features": [
            "スキル評価テスト / Skill assessment tests",
            "成長記録 / Growth records",
            "比較分析 / Comparative analysis",
            "レーダーチャート表示 / Radar chart visualization",
            "評価レポート / Assessment reports"
        ]
    },
    "game-inventory-tracker-agent": {
        "ja_desc": "ゲーム在庫トラッカーエージェント",
        "en_desc": "Game Inventory Tracker Agent",
        "features": [
            "在庫管理 / Inventory management",
            "アイテム価値追跡 / Item value tracking",
            "通貨残高管理 / Currency balance management",
            "アイテム履歴 / Item history",
            "価値変動分析 / Value fluctuation analysis"
        ]
    },
    "game-spending-tracker-agent": {
        "ja_desc": "ゲーム支出トラッカーエージェント",
        "en_desc": "Game Spending Tracker Agent",
        "features": [
            "支出追跡 / Expense tracking",
            "購入履歴 / Purchase history",
            "カテゴリ別分析 / Category-based analysis",
            "月次レポート / Monthly reports",
            "支出予測 / Expense forecasting"
        ]
    },
    "game-budget-manager-agent": {
        "ja_desc": "ゲーム予算管理エージェント",
        "en_desc": "Game Budget Manager Agent",
        "features": [
            "予算設定 / Budget setting",
            "支出アラート / Spending alerts",
            "予算進捗表示 / Budget progress display",
            "予算超過警告 / Over-budget warnings",
            "節約提案 / Saving suggestions"
        ]
    },
    "game-value-calculator-agent": {
        "ja_desc": "ゲーム価値計算エージェント",
        "en_desc": "Game Value Calculator Agent",
        "features": [
            "プレイ時間追跡 / Play time tracking",
            "1時間あたり価値計算 / Per-hour value calculation",
            "ROI分析 / ROI analysis",
            "価値比較 / Value comparison",
            "最適化提案 / Optimization suggestions"
        ]
    },
    "game-subscription-manager-agent": {
        "ja_desc": "ゲームサブスクリプション管理エージェント",
        "en_desc": "Game Subscription Manager Agent",
        "features": [
            "サブスクリプション管理 / Subscription management",
            "更新リマインダー / Renewal reminders",
            "コスト分析 / Cost analysis",
            "最適化提案 / Optimization suggestions",
            "解約追跡 / Cancellation tracking"
        ]
    }
}


def generate_db_schema(agent_name, config):
    """Generate db.py content based on agent type"""
    agent_prefix = agent_name.replace("-agent", "").replace("-", "_")

    if agent_name.startswith("baseball-"):
        if "stadium" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stadiums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        team TEXT,
        location TEXT,
        capacity INTEGER,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seat_areas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        area_name TEXT NOT NULL,
        price_range TEXT,
        capacity INTEGER,
        description TEXT,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_id INTEGER,
        method TEXT,
        time_required TEXT,
        notes TEXT,
        FOREIGN KEY (station_id) REFERENCES stations(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS facilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        type TEXT,
        name TEXT,
        description TEXT,
        distance TEXT,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_stadium(name, team=None, location=None, capacity=None, description=None):
    """スタジアムを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO stadiums (name, team, location, capacity, description)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, team, location, capacity, description))
    stadium_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return stadium_id

def get_stadiums(search_term=None):
    """スタジアム一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if search_term:
        cursor.execute('''
        SELECT * FROM stadiums WHERE name LIKE ? OR team LIKE ? OR location LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    else:
        cursor.execute('SELECT * FROM stadiums ORDER BY name')

    stadiums = cursor.fetchall()
    conn.close()
    return stadiums

def get_stadium(stadium_id):
    """スタジアム詳細"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stadiums WHERE id = ?', (stadium_id,))
    stadium = cursor.fetchone()
    conn.close()
    return stadium

if __name__ == '__main__':
    init_db()
'''

        elif "ticket" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        event_date DATE,
        section TEXT,
        row TEXT,
        seat TEXT,
        price REAL,
        available BOOLEAN DEFAULT 1,
        source_url TEXT,
        last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        price REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS discount_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        threshold_price REAL,
        active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_ticket(stadium_id, event_date, section, row, seat, price, source_url=None):
    """チケットを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO tickets (stadium_id, event_date, section, row, seat, price, source_url)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (stadium_id, event_date, section, row, seat, price, source_url))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def search_tickets(stadium_id=None, min_price=None, max_price=None, date=None):
    """チケット検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT * FROM tickets WHERE available = 1'
    params = []

    if stadium_id:
        query += ' AND stadium_id = ?'
        params.append(stadium_id)
    if min_price:
        query += ' AND price >= ?'
        params.append(min_price)
    if max_price:
        query += ' AND price <= ?'
        params.append(max_price)
    if date:
        query += ' AND event_date = ?'
        params.append(date)

    query += ' ORDER BY price ASC'

    cursor.execute(query, params)
    tickets = cursor.fetchall()
    conn.close()
    return tickets

if __name__ == '__main__':
    init_db()
'''

        elif "food" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        name TEXT NOT NULL,
        category TEXT,
        price REAL,
        description TEXT,
        popular BOOLEAN DEFAULT 0,
        calories INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wait_times (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stand_id INTEGER,
        wait_minutes INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_item_id INTEGER,
        user_id TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_menu_item(stadium_id, name, category, price, description=None, calories=None):
    """メニューアイテム追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO menu_items (stadium_id, name, category, price, description, calories)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (stadium_id, name, category, price, description, calories))
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def get_menu(stadium_id, category=None):
    """メニュー取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if category:
        cursor.execute('''
        SELECT * FROM menu_items WHERE stadium_id = ? AND category = ? ORDER BY popular DESC, name
        ''', (stadium_id, category))
    else:
        cursor.execute('''
        SELECT * FROM menu_items WHERE stadium_id = ? ORDER BY popular DESC, name
        ''', (stadium_id,))

    items = cursor.fetchall()
    conn.close()
    return items

if __name__ == '__main__':
    init_db()
'''

        elif "accessibility" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accessible_seats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        section TEXT,
        row TEXT,
        seat_count INTEGER,
        features TEXT,
        notes TEXT,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS facilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        type TEXT,
        location TEXT,
        availability TEXT,
        description TEXT,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        name TEXT,
        type TEXT,
        booking_required BOOLEAN DEFAULT 0,
        contact_info TEXT,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_accessible_seat(stadium_id, section, row, seat_count, features=None, notes=None):
    """アクセシブル席追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO accessible_seats (stadium_id, section, row, seat_count, features, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (stadium_id, section, row, seat_count, features, notes))
    seat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return seat_id

if __name__ == '__main__':
    init_db()
'''

        elif "fan" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        name TEXT NOT NULL,
        event_date DATE,
        event_time TIME,
        description TEXT,
        registration_required BOOLEAN DEFAULT 0,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS merchandise (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stadium_id INTEGER,
        name TEXT NOT NULL,
        category TEXT,
        price REAL,
        availability TEXT,
        description TEXT,
        FOREIGN KEY (stadium_id) REFERENCES stadiums(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        options TEXT,
        correct_answer TEXT,
        points INTEGER DEFAULT 10
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "training" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS training_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT NOT NULL,
        skill_level TEXT,
        duration_weeks INTEGER,
        goals TEXT,
        start_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER,
        date DATE,
        duration_minutes INTEGER,
        activity TEXT,
        notes TEXT,
        completed BOOLEAN DEFAULT 0,
        FOREIGN KEY (plan_id) REFERENCES training_plans(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        skill TEXT,
        level INTEGER,
        measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "drill" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        difficulty TEXT,
        duration_minutes INTEGER,
        equipment_needed TEXT,
        video_url TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        drill_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (drill_id) REFERENCES drills(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "form" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS form_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        swing_type TEXT,
        score REAL,
        issues TEXT,
        recommendations TEXT,
        video_path TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        metric TEXT,
        value REAL,
        measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "fitness" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date DATE,
        workout_type TEXT,
        duration_minutes INTEGER,
        calories_burned INTEGER,
        notes TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        metric TEXT,
        target_value REAL,
        current_value REAL,
        deadline DATE,
        status TEXT DEFAULT 'active'
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "skill" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        overall_score REAL,
        notes TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skill_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER,
        skill_name TEXT,
        score REAL,
        FOREIGN KEY (assessment_id) REFERENCES assessments(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

    elif agent_name.startswith("game-"):
        if "cross-save" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        platforms TEXT,
        cloud_provider TEXT,
        last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS save_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        platform TEXT,
        slot INTEGER,
        save_date TIMESTAMP,
        data_hash TEXT,
        FOREIGN KEY (game_id) REFERENCES games(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sync_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        from_platform TEXT,
        to_platform TEXT,
        status TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "achievement" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        platform TEXT,
        achievement_id TEXT,
        name TEXT,
        description TEXT,
        unlocked BOOLEAN DEFAULT 0,
        unlocked_date TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sync_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        achievement_id INTEGER,
        platform TEXT,
        status TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (achievement_id) REFERENCES achievements(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "progression" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        platform TEXT,
        level INTEGER,
        experience INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        progress_id INTEGER,
        item_name TEXT,
        quantity INTEGER,
        FOREIGN KEY (progress_id) REFERENCES progress_data(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "friends" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        friend_id TEXT,
        friend_name TEXT,
        platforms TEXT,
        last_seen TIMESTAMP,
        notes TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        friend_id INTEGER,
        game_id INTEGER,
        activity_type TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (friend_id) REFERENCES friends(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "migration" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS migration_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        from_platform TEXT,
        to_platform TEXT,
        scheduled_date DATE,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS migration_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER,
        log_text TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (plan_id) REFERENCES migration_plans(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "inventory" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        item_name TEXT,
        quantity INTEGER,
        rarity TEXT,
        estimated_value REAL,
        acquired_date DATE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS currencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        currency_name TEXT,
        amount REAL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "spending" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        item_name TEXT,
        amount REAL,
        currency TEXT,
        category TEXT,
        date DATE,
        notes TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "budget" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        monthly_limit REAL,
        current_spent REAL DEFAULT 0,
        month TEXT,
        year INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        budget_id INTEGER,
        threshold_percentage INTEGER,
        triggered BOOLEAN DEFAULT 0,
        FOREIGN KEY (budget_id) REFERENCES budgets(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "value" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        platform TEXT,
        purchase_price REAL,
        purchase_date DATE,
        hours_played REAL DEFAULT 0,
        currency TEXT DEFAULT 'USD'
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS play_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        date DATE,
        hours_played REAL,
        FOREIGN KEY (game_id) REFERENCES games(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "subscription" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT,
        game_id INTEGER,
        monthly_cost REAL,
        renewal_date DATE,
        status TEXT DEFAULT 'active',
        notes TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS renewal_reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_id INTEGER,
        reminder_days INTEGER,
        sent BOOLEAN DEFAULT 0,
        FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

    elif agent_name.startswith("erotic-"):
        if "age" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        verification_method TEXT,
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'verified'
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        session_token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "content" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS content_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        content_hash TEXT,
        nsfw_score REAL,
        category TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS filter_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        category TEXT,
        action TEXT,
        active BOOLEAN DEFAULT 1
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "privacy" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS encrypted_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        log_type TEXT,
        encrypted_data TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS privacy_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        auto_delete_days INTEGER,
        private_mode BOOLEAN DEFAULT 0,
        tracking_prevention BOOLEAN DEFAULT 1
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "safe" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS site_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        safety_score REAL,
        is_safe BOOLEAN,
        threats TEXT,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blocklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        threat_type TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

        elif "compliance" in agent_name:
            return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS compliance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_type TEXT,
        result TEXT,
        findings TEXT,
        audited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        request_type TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''

    # Default fallback
    return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} / {config['en_desc']}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "{agent_prefix}.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
'''


def generate_agent_py(agent_name, config):
    """Generate agent.py content"""
    agent_class = ''.join(word.capitalize() for word in agent_name.replace('-agent', '').split('-'))
    return f'''#!/usr/bin/env python3
"""
{config['ja_desc']}
{config['en_desc']}
"""

import discord
from discord.ext import commands
from db import init_db

class {agent_class}Agent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        init_db()

    async def setup_hook(self):
        await self.add_command(self.status)
        await self.add_command(self.help)

    @commands.command(name='status')
    async def status(self, ctx):
        """ステータスを表示 / Show status"""
        await ctx.send(f"✅ {config['ja_desc']} is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **{config['ja_desc']}**\\n\\n"
        response += "**Features / 機能:**\\n"
        for feature in config['features']:
            response += f"• {feature}\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = {agent_class}Agent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
'''


def generate_discord_py(agent_name, config):
    """Generate discord.py content"""
    return f'''#!/usr/bin/env python3
"""
{config['ja_desc']} - Discord連携
{config['en_desc']} - Discord Integration
"""

import re

def parse_message(message):
    """メッセージを解析"""
    if message.strip().lower() in ['status', 'ステータス']:
        return {{'action': 'status'}}
    if message.strip().lower() in ['help', 'ヘルプ']:
        return {{'action': 'help'}}
    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    if parsed['action'] == 'status':
        return f"✅ {config['ja_desc']} is online"

    if parsed['action'] == 'help':
        response = f"📖 **{config['ja_desc']}**\\n\\n"
        response += "**Features / 機能:**\\n"
        for feature in config['features']:
            response += f"• {feature}\\n"
        return response

    return None

if __name__ == '__main__':
    test_messages = ['status', 'help']
    for msg in test_messages:
        print(f"Input: {{msg}}")
        result = handle_message(msg)
        if result:
            print(result)
        print()
'''


def generate_readme_md(agent_name, config):
    """Generate README.md content"""
    features_list = '\\n'.join([f'- {feature}' for feature in config['features']])

    return f'''# {agent_name}

{config['ja_desc']} / {config['en_desc']}

## 概要 / Overview

{config['ja_desc']}は、{config['en_desc'].lower()}のためのAIエージェントです。

## 機能 / Features

{features_list}

## インストール / Installation

```bash
cd agents/{agent_name}
pip install -r requirements.txt
```

## 使用方法 / Usage

### Discord Botとして実行 / Run as Discord Bot

```bash
python agent.py
```

### データベース初期化 / Initialize Database

```bash
python db.py
```

## データベーススキーマ / Database Schema

The agent uses SQLite. See `db.py` for the complete schema.

## 設定 / Configuration

Configuration is loaded from environment variables:
- `DISCORD_BOT_TOKEN`: Discordボットトークン / Discord bot token

## 依存パッケージ / Requirements

See `requirements.txt` for dependencies.

## ライセンス / License

MIT License
'''


def generate_requirements_txt():
    """Generate requirements.txt content"""
    return '''discord.py>=2.3.0
python-dotenv>=1.0.0
'''


def create_agent_files(agent_name, config):
    """Create all files for an agent"""
    agent_dir = AGENTS_DIR / agent_name

    # Generate and write files
    files = {
        'agent.py': generate_agent_py(agent_name, config),
        'db.py': generate_db_schema(agent_name, config),
        'discord.py': generate_discord_py(agent_name, config),
        'README.md': generate_readme_md(agent_name, config),
        'requirements.txt': generate_requirements_txt()
    }

    for filename, content in files.items():
        filepath = agent_dir / filename
        filepath.write_text(content, encoding='utf-8')
        print(f"Created: {agent_name}/{filename}")

    return agent_name


def main():
    """Main generation function"""
    print("=" * 60)
    print("V27 Agent Generator - Creating 25 agents")
    print("=" * 60)

    created_agents = []

    for agent_name, config in AGENT_CONFIGS.items():
        print(f"\\nCreating agent: {agent_name}")
        try:
            created = create_agent_files(agent_name, config)
            created_agents.append(created)
        except Exception as e:
            print(f"❌ Error creating {agent_name}: {e}")
            import traceback
            traceback.print_exc()

    print("\\n" + "=" * 60)
    print(f"✅ Completed! Created {len(created_agents)}/{len(AGENT_CONFIGS)} agents")
    print("=" * 60)

    return created_agents


if __name__ == '__main__':
    main()
