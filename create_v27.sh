#!/bin/bash
# Create all V27 agent files

cd /workspace/agents

# Common requirements.txt
cat > /tmp/requirements.txt << 'REQ_EOF'
discord.py>=2.3.0
python-dotenv>=1.0.0
REQ_EOF

# Function to create common structure
create_agent_base() {
    local agent_name=$1
    local ja_desc=$2
    local en_desc=$3
    local features=$4

    local agent_dir="${agent_name}"
    local agent_class=$(echo $agent_name | sed 's/-agent$//' | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1' | tr -d ' ')
    local db_name=$(echo $agent_name | sed 's/-agent$//' | sed 's/-/_/g').db

    # Create agent.py
    cat > "${agent_dir}/agent.py" << AGENT_EOF
#!/usr/bin/env python3
"""
${ja_desc}
${en_desc}
"""

import discord
from discord.ext import commands
from db import init_db

class ${agent_class}Agent(commands.Bot):
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
        await ctx.send(f"✅ ${ja_desc} is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **${ja_desc}**\\n\\n"
        response += "**Features / 機能:**\\n"
${features}
        await ctx.send(response)

if __name__ == '__main__':
    bot = ${agent_class}Agent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
AGENT_EOF

    # Create db.py
    cat > "${agent_dir}/db.py" << DB_EOF
#!/usr/bin/env python3
"""
${ja_desc} / ${en_desc}
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "${db_name}"

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
DB_EOF

    # Create discord.py
    cat > "${agent_dir}/discord.py" << DISCORD_EOF
#!/usr/bin/env python3
"""
${ja_desc} - Discord連携
${en_desc} - Discord Integration
"""

import re

def parse_message(message):
    """メッセージを解析"""
    if message.strip().lower() in ['status', 'ステータス']:
        return {'action': 'status'}
    if message.strip().lower() in ['help', 'ヘルプ']:
        return {'action': 'help'}
    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    if parsed['action'] == 'status':
        return f"✅ ${ja_desc} is online"

    if parsed['action'] == 'help':
        response = f"📖 **${ja_desc}**\\n\\n"
        response += "**Features / 機能:**\\n"
${features}
        return response

    return None

if __name__ == '__main__':
    test_messages = ['status', 'help']
    for msg in test_messages:
        print(f"Input: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
        print()
DISCORD_EOF

    # Copy requirements.txt
    cp /tmp/requirements.txt "${agent_dir}/requirements.txt"

    echo "Created files for: ${agent_name}"
}

# Create all agents
echo "Creating V27 agents..."

create_agent_base "baseball-stadium-finder-agent" \
    "野球スタジアム検索・情報エージェント" \
    "Baseball Stadium Finder and Information Agent" \
    '        response += "• スタジアム検索・フィルタリング機能 / Stadium search and filtering\\n"
        response += "• 座席エリア情報の提供 / Seat area information\\n"
        response += "• アクセス方法・交通手段の提案 / Access and transportation\\n"
        response += "• 周辺施設情報 / Nearby facilities\\n"
        response += "• チケット価格帯の比較 / Ticket price comparison\\n"'

create_agent_base "baseball-ticket-optimizer-agent" \
    "野球チケット最適化エージェント" \
    "Baseball Ticket Optimizer Agent" \
    '        response += "• チケット価格の比較・最適化 / Ticket price comparison\\n"
        response += "• リアルタイム空席監視 / Real-time seat monitoring\\n"
        response += "• 価格変動の予測 / Price prediction\\n"
        response += "• 購入タイミングの提案 / Purchase timing\\n"
        response += "• 割引情報の収集・配信 / Discount information\\n"'

create_agent_base "baseball-food-beverage-agent" \
    "野球スタジアムフード・ドリンクエージェント" \
    "Baseball Stadium Food and Beverage Agent" \
    '        response += "• スタジアムフードメニューのカタログ / Food menu catalog\\n"
        response += "• 待ち時間の予測・監視 / Wait time prediction\\n"
        response += "• 事前注文機能の統合 / Pre-order integration\\n"
        response += "• 人気メニューのランキング / Popular menu rankings\\n"
        response += "• 食事タイミングの提案 / Meal timing recommendations\\n"'

create_agent_base "baseball-accessibility-agent" \
    "野球スタジアムアクセシビリティエージェント" \
    "Baseball Stadium Accessibility Agent" \
    '        response += "• 車いす対応席の情報 / Wheelchair accessible seating\\n"
        response += "• バリアフリー施設の案内 / Barrier-free facility guidance\\n"
        response += "• サポートサービスの予約 / Support service booking\\n"
        response += "• 視覚・聴覚障害者支援 / Visual/hearing impairment support\\n"
        response += "• 多言語対応サービス / Multi-language services\\n"'

create_agent_base "baseball-fan-experience-agent" \
    "野球ファン体験エージェント" \
    "Baseball Fan Experience Agent" \
    '        response += "• ファン体験イベントの案内 / Fan experience events\\n"
        response += "• 記念品・グッズ情報の収集 / Merchandise information\\n"
        response += "• スタジアムクイズ・ゲーム / Stadium quizzes and games\\n"
        response += "• AR/VR体験機能 / AR/VR experience features\\n"
        response += "• ファン参加型コンテンツ / Fan participation content\\n"'

create_agent_base "game-cross-save-agent" \
    "ゲームクロスセーブエージェント" \
    "Game Cross-Save Agent" \
    '        response += "• クロスプラットフォームセーブ同期 / Cross-platform save sync\\n"
        response += "• クラウドストレージ統合 / Cloud storage integration\\n"
        response += "• 競合解決機能 / Conflict resolution\\n"
        response += "• 同期履歴の追跡 / Sync history tracking\\n"
        response += "• 手動/自動同期モード / Manual/automatic sync modes\\n"'

create_agent_base "game-achievement-sync-agent" \
    "ゲーム実績同期エージェント" \
    "Game Achievement Sync Agent" \
    '        response += "• 実績・トロフィーの同期 / Achievement and trophy sync\\n"
        response += "• プラットフォーム間の統合表示 / Cross-platform display\\n"
        response += "• 実績進捗の追跡 / Achievement progress tracking\\n"
        response += "• 実績比較機能 / Achievement comparison\\n"
        response += "• 実績統計の可視化 / Achievement statistics\\n"'

create_agent_base "game-progression-sync-agent" \
    "ゲーム進行状況同期エージェント" \
    "Game Progression Sync Agent" \
    '        response += "• レベル・経験値の同期 / Level and experience sync\\n"
        response += "• 装備・アイテムの同期 / Equipment and item sync\\n"
        response += "• アンロック状況の管理 / Unlock status management\\n"
        response += "• マルチデバイス進行管理 / Multi-device progress\\n"
        response += "• 同期ステータスの表示 / Sync status display\\n"'

create_agent_base "game-friends-unified-agent" \
    "ゲームフレンド統合エージェント" \
    "Game Friends Unified Agent" \
    '        response += "• 統合フレンドリスト / Unified friend list\\n"
        response += "• オンライン状態の監視 / Online status monitoring\\n"
        response += "• クロスプラットフォーム招待 / Cross-platform invitations\\n"
        response += "• フレンド活動の追跡 / Friend activity tracking\\n"
        response += "• ソーシャル機能の統合 / Social feature integration\\n"'

create_agent_base "game-data-migration-agent" \
    "ゲームデータ移行エージェント" \
    "Game Data Migration Agent" \
    '        response += "• データ移行の自動化 / Automated data migration\\n"
        response += "• 移行計画の作成 / Migration plan creation\\n"
        response += "• データ整合性の検証 / Data integrity verification\\n"
        response += "• 移行ログの記録 / Migration log recording\\n"
        response += "• 移行失敗時のロールバック / Rollback on failure\\n"'

create_agent_base "erotic-age-verification-agent" \
    "えっち年齢認証エージェント" \
    "Erotic Age Verification Agent" \
    '        response += "• 年齢認証機能 / Age verification\\n"
        response += "• ID検証統合 / ID verification integration\\n"
        response += "• アクセス制限の実施 / Access restriction enforcement\\n"
        response += "• セッション管理 / Session management\\n"
        response += "• 認証ログの記録 / Authentication log recording\\n"'

create_agent_base "erotic-content-filter-agent" \
    "えっちコンテンツフィルターエージェント" \
    "Erotic Content Filter Agent" \
    '        response += "• NSFWコンテンツ検出 / NSFW content detection\\n"
        response += "• AIベースのフィルタリング / AI-based filtering\\n"
        response += "• コンテンツカテゴリ分類 / Content categorization\\n"
        response += "• ユーザー設定に基づくフィルター / User-configurable filters\\n"
        response += "• 誤検出の報告・修正 / False positive reporting\\n"'

create_agent_base "erotic-privacy-guard-agent" \
    "えっちプライバシーガードエージェント" \
    "Erotic Privacy Guard Agent" \
    '        response += "• 閲覧履歴の暗号化 / Encrypted browsing history\\n"
        response += "• 検索履歴の保護 / Search history protection\\n"
        response += "• 自動削除機能 / Auto-delete functionality\\n"
        response += "• プライベートモード / Private mode\\n"
        response += "• 追跡防止機能 / Tracking prevention\\n"'

create_agent_base "erotic-safe-browsing-agent" \
    "えっちセーフブラウジングエージェント" \
    "Erotic Safe Browsing Agent" \
    '        response += "• 安全なサイト判定 / Safe site detection\\n"
        response += "• 詐欺サイト検出 / Scam site detection\\n"
        response += "• マルウェアスキャン / Malware scanning\\n"
        response += "• フィッシング対策 / Phishing protection\\n"
        response += "• 安全なダウンロード / Safe downloads\\n"'

create_agent_base "erotic-data-compliance-agent" \
    "えっちデータコンプライアンスエージェント" \
    "Erotic Data Compliance Agent" \
    '        response += "• 規制対応の監査 / Regulation compliance audit\\n"
        response += "• データポリシーの管理 / Data policy management\\n"
        response += "• 同意管理 / Consent management\\n"
        response += "• データリクエスト処理 / Data request processing\\n"
        response += "• コンプライアンスレポート / Compliance reporting\\n"'

create_agent_base "baseball-training-plan-agent" \
    "野球トレーニングプランエージェント" \
    "Baseball Training Plan Agent" \
    '        response += "• パーソナライズドトレーニングプラン / Personalized training plans\\n"
        response += "• スキルレベル評価 / Skill level assessment\\n"
        response += "• 目標設定機能 / Goal setting\\n"
        response += "• 進捗追跡 / Progress tracking\\n"
        response += "• プラン調整・最適化 / Plan adjustment and optimization\\n"'

create_agent_base "baseball-drill-library-agent" \
    "野球ドリルライブラリエージェント" \
    "Baseball Drill Library Agent" \
    '        response += "• ドリルライブラリ / Drill library\\n"
        response += "• 動画チュートリアル / Video tutorials\\n"
        response += "• 難易度別分類 / Difficulty-based classification\\n"
        response += "• 目的別ドリル検索 / Purpose-based drill search\\n"
        response += "• お気に入り機能 / Favorites\\n"'

create_agent_base "baseball-form-coach-agent" \
    "野球フォームコーチエージェント" \
    "Baseball Form Coach Agent" \
    '        response += "• フォーム分析 / Form analysis\\n"
        response += "• 改善提案 / Improvement recommendations\\n"
        response += "• ビデオフィードバック / Video feedback\\n"
        response += "• 進捗追跡 / Progress tracking\\n"
        response += "• コーチングチャット / Coaching chat\\n"'

create_agent_base "baseball-fitness-tracker-agent" \
    "野球フィットネストラッカーエージェント" \
    "Baseball Fitness Tracker Agent" \
    '        response += "• フィットネスデータ追跡 / Fitness data tracking\\n"
        response += "• ウェアラブル統合 / Wearable integration\\n"
        response += "• トレーニングログ / Training logs\\n"
        response += "• 目標設定 / Goal setting\\n"
        response += "• 分析・レポート / Analysis and reporting\\n"'

create_agent_base "baseball-skill-assessment-agent" \
    "野球スキル評価エージェント" \
    "Baseball Skill Assessment Agent" \
    '        response += "• スキル評価テスト / Skill assessment tests\\n"
        response += "• 成長記録 / Growth records\\n"
        response += "• 比較分析 / Comparative analysis\\n"
        response += "• レーダーチャート表示 / Radar chart visualization\\n"
        response += "• 評価レポート / Assessment reports\\n"'

create_agent_base "game-inventory-tracker-agent" \
    "ゲーム在庫トラッカーエージェント" \
    "Game Inventory Tracker Agent" \
    '        response += "• 在庫管理 / Inventory management\\n"
        response += "• アイテム価値追跡 / Item value tracking\\n"
        response += "• 通貨残高管理 / Currency balance management\\n"
        response += "• アイテム履歴 / Item history\\n"
        response += "• 価値変動分析 / Value fluctuation analysis\\n"'

create_agent_base "game-spending-tracker-agent" \
    "ゲーム支出トラッカーエージェント" \
    "Game Spending Tracker Agent" \
    '        response += "• 支出追跡 / Expense tracking\\n"
        response += "• 購入履歴 / Purchase history\\n"
        response += "• カテゴリ別分析 / Category-based analysis\\n"
        response += "• 月次レポート / Monthly reports\\n"
        response += "• 支出予測 / Expense forecasting\\n"'

create_agent_base "game-budget-manager-agent" \
    "ゲーム予算管理エージェント" \
    "Game Budget Manager Agent" \
    '        response += "• 予算設定 / Budget setting\\n"
        response += "• 支出アラート / Spending alerts\\n"
        response += "• 予算進捗表示 / Budget progress display\\n"
        response += "• 予算超過警告 / Over-budget warnings\\n"
        response += "• 節約提案 / Saving suggestions\\n"'

create_agent_base "game-value-calculator-agent" \
    "ゲーム価値計算エージェント" \
    "Game Value Calculator Agent" \
    '        response += "• プレイ時間追跡 / Play time tracking\\n"
        response += "• 1時間あたり価値計算 / Per-hour value calculation\\n"
        response += "• ROI分析 / ROI analysis\\n"
        response += "• 価値比較 / Value comparison\\n"
        response += "• 最適化提案 / Optimization suggestions\\n"'

create_agent_base "game-subscription-manager-agent" \
    "ゲームサブスクリプション管理エージェント" \
    "Game Subscription Manager Agent" \
    '        response += "• サブスクリプション管理 / Subscription management\\n"
        response += "• 更新リマインダー / Renewal reminders\\n"
        response += "• コスト分析 / Cost analysis\\n"
        response += "• 最適化提案 / Optimization suggestions\\n"
        response += "• 解約追跡 / Cancellation tracking\\n"'

echo ""
echo "Creating README.md files for all agents..."

# Create README.md for each agent
for agent_dir in baseball-stadium-finder-agent baseball-ticket-optimizer-agent baseball-food-beverage-agent baseball-accessibility-agent baseball-fan-experience-agent game-cross-save-agent game-achievement-sync-agent game-progression-sync-agent game-friends-unified-agent game-data-migration-agent erotic-age-verification-agent erotic-content-filter-agent erotic-privacy-guard-agent erotic-safe-browsing-agent erotic-data-compliance-agent baseball-training-plan-agent baseball-drill-library-agent baseball-form-coach-agent baseball-fitness-tracker-agent baseball-skill-assessment-agent game-inventory-tracker-agent game-spending-tracker-agent game-budget-manager-agent game-value-calculator-agent game-subscription-manager-agent; do
    agent_name=$(echo $agent_dir | sed 's/-agent$//')
    agent_title=$(echo $agent_name | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')

    cat > "${agent_dir}/README.md" << README_EOF
# ${agent_dir}

${agent_title} Agent

## 概要 / Overview

このエージェントは、${agent_title}のためのAIエージェントです。

## インストール / Installation

\`\`\`bash
cd agents/${agent_dir}
pip install -r requirements.txt
\`\`\`

## 使用方法 / Usage

### Discord Botとして実行 / Run as Discord Bot

\`\`\`bash
python agent.py
\`\`\`

### データベース初期化 / Initialize Database

\`\`\`bash
python db.py
\`\`\`

## 設定 / Configuration

Configuration is loaded from environment variables:
- \`DISCORD_BOT_TOKEN\`: Discordボットトークン / Discord bot token

## 依存パッケージ / Requirements

See \`requirements.txt\` for dependencies.

## ライセンス / License

MIT License
README_EOF

    echo "Created README.md for: ${agent_dir}"
done

echo ""
echo "✅ All V27 agents created successfully!"
