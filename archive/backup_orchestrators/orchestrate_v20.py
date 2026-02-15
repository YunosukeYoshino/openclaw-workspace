#!/usr/bin/env python3
"""
Orchestrator for Next Projects V20
次期プロジェクト V20 オーケストレーター

自律的に5つのプロジェクト（25エージェント）を開発するオーケストレーター
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

# プロジェクト定義 - V20
PROJECTS = [
    {
        "id": "baseball-history",
        "name_ja": "野球歴史・伝承エージェント",
        "name_en": "Baseball History & Legacy Agents",
        "agents": [
            {
                "id": "baseball-historical-match-agent",
                "name_ja": "野球歴史的名試合エージェント",
                "name_en": "Baseball Historical Match Agent",
                "description_ja": "歴史的な名試合、ドラマチックな展開の記録、勝敗を決めた重要場面の分析、映像・音声との統合、再現プレイ、記念イベントの自動提案",
                "description_en": "Record historic dramatic matches, analyze key moments, integrate with video/audio, suggest replay recreations and commemorative events",
                "features": [
                    "Historical Match Records",
                    "Key Moment Analysis",
                    "Media Integration",
                    "Replay Suggestions",
                    "Commemorative Events",
                    "Match Search"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "beautifulsoup4", "matplotlib"]
            },
            {
                "id": "baseball-legend-profile-agent",
                "name_ja": "野球伝説選手プロフィールエージェント",
                "name_en": "Baseball Legend Profile Agent",
                "description_ja": "殿堂入り選手、レジェンド選手のプロフィール管理、統計、ハイライト、語り継がれるエピソードの収集、クロス世代比較、影響力の可視化",
                "description_en": "Manage Hall of Fame and legend player profiles, collect stats, highlights, and legendary stories, cross-generational comparison, influence visualization",
                "features": [
                    "Legend Profiles",
                    "Statistics Tracking",
                    "Highlight Collection",
                    "Cross-Gen Comparison",
                    "Influence Metrics",
                    "Search & Discovery"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "matplotlib", "networkx"]
            },
            {
                "id": "baseball-evolution-agent",
                "name_ja": "野球戦術・ルール進化エージェント",
                "name_en": "Baseball Evolution Agent",
                "description_ja": "野球戦術の歴史的進化（死球打法、シフト等）の追跡、ルール変更の影響分析、時代ごとのプレイスタイル比較、未来の戦術・ルールの予測・提案",
                "description_en": "Track historical evolution of tactics (sacrifice bunt, shift), analyze rule change impacts, compare play styles across eras, predict future tactics and rules",
                "features": [
                    "Tactic Evolution Tracking",
                    "Rule Change Analysis",
                    "Era Comparison",
                    "Future Prediction",
                    "Trend Analysis",
                    "Historical Search"
                ],
                "tech_stack": ["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn"]
            },
            {
                "id": "baseball-stadium-history-agent",
                "name_ja": "野球場歴史エージェント",
                "name_en": "Baseball Stadium History Agent",
                "description_ja": "歴史的野球場の建設、改名、移転などの歴史、球場の特徴、伝説的なイベント、記録的な試合との紐付け、球場ツアー、記念日の自動通知",
                "description_en": "History of ballpark construction, renaming, relocation, stadium features, legendary events, tie to record games, stadium tours, anniversary notifications",
                "features": [
                    "Stadium Histories",
                    "Feature Tracking",
                    "Event Records",
                    "Historic Matches",
                    "Tour Planning",
                    "Anniversary Alerts"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "geopandas", "matplotlib"]
            },
            {
                "id": "baseball-culture-agent",
                "name_ja": "野球文化エージェント",
                "name_en": "Baseball Culture Agent",
                "description_ja": "野球に関連する音楽、映画、文学、アートの収集、ファン文化、チーム伝統、サポーターの歴史、野球の社会的影響、文化への統合分析",
                "description_en": "Collect baseball-related music, film, literature, art, fan culture, team traditions, supporter history, social impact, cultural integration analysis",
                "features": [
                    "Cultural Content",
                    "Fan Culture",
                    "Team Traditions",
                    "Media Collection",
                    "Social Impact",
                    "Cultural Analysis"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "beautifulsoup4", "networkx"]
            }
        ]
    },
    {
        "id": "game-modeling",
        "name_ja": "ゲームモデリング・シミュレーションエージェント",
        "name_en": "Game Modeling & Simulation Agents",
        "agents": [
            {
                "id": "game-probability-agent",
                "name_ja": "ゲーム確率計算エージェント",
                "name_en": "Game Probability Agent",
                "description_ja": "ゲーム内の確率計算（ドロップ、クリティカル、等）、Monte Carloシミュレーションによる期待値計算、確率の可視化、最適戦略の提案",
                "description_en": "Calculate in-game probabilities (drop rates, crits, etc.), expected value via Monte Carlo simulation, probability visualization, optimal strategy suggestions",
                "features": [
                    "Probability Calculation",
                    "Monte Carlo Sim",
                    "Expected Value",
                    "Probability Viz",
                    "Strategy Opt",
                    "Risk Assessment"
                ],
                "tech_stack": ["pandas", "numpy", "scipy", "matplotlib", "seaborn"]
            },
            {
                "id": "game-mechanics-analysis-agent",
                "name_ja": "ゲームメカニクス分析エージェント",
                "name_en": "Game Mechanics Analysis Agent",
                "description_ja": "ゲーム内メカニクスの逆解析、数式化、バランス問題、不公平性の検出、パッチ変更によるメカニクス変化の追跡",
                "description_en": "Reverse engineer game mechanics, mathematical modeling, detect balance issues and unfairness, track mechanics changes from patches",
                "features": [
                    "Mechanics Reverse",
                    "Math Modeling",
                    "Balance Detection",
                    "Patch Tracking",
                    "Unfairness Alert",
                    "Mechanics Docs"
                ],
                "tech_stack": ["pandas", "numpy", "scipy", "scikit-learn", "matplotlib"]
            },
            {
                "id": "game-simulation-agent",
                "name_ja": "ゲームシミュレーションエージェント",
                "name_en": "Game Simulation Agent",
                "description_ja": "戦闘、経済、生産等のゲーム内システムのシミュレーション、シナリオテスト、最適戦略の探索、AI vs AI のシミュレーション、戦闘力測定",
                "description_en": "Simulate in-game systems (combat, economy, production), scenario testing, optimal strategy search, AI vs AI simulation, power measurement",
                "features": [
                    "Combat Sim",
                    "Economy Sim",
                    "Production Sim",
                    "Scenario Testing",
                    "AI vs AI",
                    "Power Measurement"
                ],
                "tech_stack": ["pandas", "numpy", "scipy", "matplotlib", "joblib"]
            },
            {
                "id": "game-theory-agent",
                "name_ja": "ゲーム理論エージェント",
                "name_en": "Game Theory Agent",
                "description_ja": "プレイヤー間の意思決定、ナッシュ均衡の分析、囚人のジレンマ、チキンゲーム等の適用、協力・競争戦略の最適化",
                "description_en": "Analyze player decision-making, Nash equilibrium, apply prisoner's dilemma, chicken game, optimize cooperation/competition strategies",
                "features": [
                    "Decision Analysis",
                    "Nash Equilibrium",
                    "Game Theory Models",
                    "Strategy Opt",
                    "Payoff Matrix",
                    "Equilibrium Finder"
                ],
                "tech_stack": ["pandas", "numpy", "scipy", "networkx", "matplotlib"]
            },
            {
                "id": "game-replay-analysis-agent",
                "name_ja": "ゲームリプレイ分析エージェント",
                "name_en": "Game Replay Analysis Agent",
                "description_ja": "リプレイファイルの解析、重要局面の抽出、プレイヤー行動のパターン認識、改善提案、プロ選手との比較、スキルギャップの特定",
                "description_en": "Parse replay files, extract key moments, pattern recognition for player behavior, improvement suggestions, compare with pros, identify skill gaps",
                "features": [
                    "Replay Parsing",
                    "Key Moments",
                    "Pattern Recognition",
                    "Improvement Suggest",
                    "Pro Comparison",
                    "Skill Gap Analysis"
                ],
                "tech_stack": ["pandas", "numpy", "scikit-learn", "matplotlib", "opencv-python"]
            }
        ]
    },
    {
        "id": "erotic-ai-analysis",
        "name_ja": "えっちコンテンツAI解析・推薦エージェント",
        "name_en": "Erotic Content AI Analysis & Recommendation Agents",
        "agents": [
            {
                "id": "erotic-ai-scene-analysis-agent",
                "name_ja": "えっちシーンAI分析エージェント",
                "name_en": "Erotic AI Scene Analysis Agent",
                "description_ja": "シーンの分類、タグ付け、重要要素の抽出、シチュエーション、プレイスタイルの分類、シーン間の類似度計算、関連シーンの提案",
                "description_en": "Scene classification, tagging, key element extraction, situation and play style classification, scene similarity calculation, related scene suggestions",
                "features": [
                    "Scene Classification",
                    "Auto Tagging",
                    "Key Elements",
                    "Situation Analysis",
                    "Similarity Search",
                    "Related Scenes"
                ],
                "tech_stack": ["pandas", "numpy", "scikit-learn", "torch", "transformers"]
            },
            {
                "id": "erotic-ai-preference-learning-agent",
                "name_ja": "えっち嗜好AI学習エージェント",
                "name_en": "Erotic AI Preference Learning Agent",
                "description_ja": "ユーザーの閲覧履歴、評価、フィードバックから嗜好を学習、時間経過による嗜好変化の追跡、潜在的嗜好の発見、新ジャンルの提案",
                "description_en": "Learn preferences from viewing history, ratings, feedback, track preference changes over time, discover latent preferences, suggest new genres",
                "features": [
                    "Preference Learning",
                    "History Tracking",
                    "Trend Detection",
                    "Latent Preference",
                    "New Genre Suggest",
                    "Feedback Loop"
                ],
                "tech_stack": ["pandas", "numpy", "scikit-learn", "torch", "surprise"]
            },
            {
                "id": "erotic-ai-quality-assessment-agent",
                "name_ja": "えっち品質AI評価エージェント",
                "name_en": "Erotic AI Quality Assessment Agent",
                "description_ja": "アート、ストーリー、アニメーション等の品質評価、技術的な完成度、芸術的な価値の分析、コミュニティ評価との相関分析",
                "description_en": "Quality assessment of art, story, animation, technical completion level, artistic value analysis, correlation with community ratings",
                "features": [
                    "Art Quality",
                    "Story Quality",
                    "Animation Quality",
                    "Technical Score",
                    "Artistic Value",
                    "Community Correlation"
                ],
                "tech_stack": ["pandas", "numpy", "scikit-learn", "torch", "torchvision"]
            },
            {
                "id": "erotic-ai-curation-agent",
                "name_ja": "えっちAIキュレーションエージェント",
                "name_en": "Erotic AI Curation Agent",
                "description_ja": "AIによるコレクションの自動キュレーション、テーマ別、ムード別、時間帯別のプレイリスト作成、機械学習によるトレンド予測、先行コンテンツの提案",
                "description_en": "AI-powered collection curation, create playlists by theme, mood, time of day, ML-based trend prediction, suggest trending content",
                "features": [
                    "Auto Curation",
                    "Theme Playlists",
                    "Mood Matching",
                    "Trend Prediction",
                    "Trending Content",
                    "Personalized List"
                ],
                "tech_stack": ["pandas", "numpy", "scikit-learn", "torch", "recommenders"]
            },
            {
                "id": "erotic-ai-finder-agent",
                "name_ja": "えっちAI検索エージェント",
                "name_en": "Erotic AI Finder Agent",
                "description_ja": "自然言語でのあいまい検索（「切ない」「情熱的」等）、画像、動画からの類似コンテンツ検索、複合条件検索、パーソナライズ順位付け",
                "description_en": "Natural language fuzzy search (sad, passionate, etc.), similar content search from images/videos, complex condition search, personalized ranking",
                "features": [
                    "Natural Search",
                    "Semantic Search",
                    "Image Search",
                    "Video Search",
                    "Complex Filters",
                    "Personalized Rank"
                ],
                "tech_stack": ["pandas", "numpy", "scikit-learn", "torch", "sentence-transformers"]
            }
        ]
    },
    {
        "id": "baseball-scouting",
        "name_ja": "野球スカウティング・ドラフトエージェント",
        "name_en": "Baseball Scouting & Draft Agents",
        "agents": [
            {
                "id": "baseball-draft-candidate-agent",
                "name_ja": "野球ドラフト候補エージェント",
                "name_en": "Baseball Draft Candidate Agent",
                "description_ja": "ドラフト候補選手のプロフィール、統計、評価、大学、高校、社会人選手の情報収集、チームのニーズに応じた候補選手の提案",
                "description_en": "Draft candidate profiles, statistics, evaluations, collect info on college, high school, industrial league players, suggest candidates based on team needs",
                "features": [
                    "Candidate Profiles",
                    "Stats Tracking",
                    "Evaluations",
                    "Multi-Source Data",
                    "Team Matching",
                    "Draft Rankings"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "beautifulsoup4", "scikit-learn"]
            },
            {
                "id": "baseball-minor-league-agent",
                "name_ja": "野球マイナーリーグエージェント",
                "name_en": "Baseball Minor League Agent",
                "description_ja": "マイナーリーグ選手のパフォーマンス追跡、昇格の可能性、開発状況の評価、ロスター管理、メジャー昇格のタイミング提案",
                "description_en": "Track minor league player performance, promotion potential, development evaluation, roster management, suggest major league call-up timing",
                "features": [
                    "Performance Track",
                    "Promotion Potential",
                    "Development Eval",
                    "Roster Mgmt",
                    "Call-up Timing",
                    "Progress Tracking"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "matplotlib", "scikit-learn"]
            },
            {
                "id": "baseball-international-agent",
                "name_ja": "野球国際選手エージェント",
                "name_en": "Baseball International Agent",
                "description_ja": "海外選手（アジア、中南米等）の情報収集、ポスティングシステム、FA市場の分析、文化適応、移籍のリスク評価",
                "description_en": "Collect info on international players (Asia, Latin America, etc.), analyze posting system, FA market, cultural adaptation, transfer risk assessment",
                "features": [
                    "International Players",
                    "Posting System",
                    "FA Market",
                    "Cultural Adaptation",
                    "Risk Assessment",
                    "Global Scouting"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "beautifulsoup4", "geopandas"]
            },
            {
                "id": "baseball-scout-report-agent",
                "name_ja": "野球スカウトレポートエージェント",
                "name_en": "Baseball Scout Report Agent",
                "description_ja": "スカウトリポートの統合・管理、複数スカウトの評価の統合、バイアス補正、選手比較、プロジェクション、ツール評価",
                "description_en": "Integrate and manage scout reports, aggregate multiple scout evaluations, bias correction, player comparison, projection, tool grading",
                "features": [
                    "Report Mgmt",
                    "Multi-Scout Agg",
                    "Bias Correction",
                    "Player Compare",
                    "Projection",
                    "Tool Grading"
                ],
                "tech_stack": ["pandas", "numpy", "scikit-learn", "matplotlib", "seaborn"]
            },
            {
                "id": "baseball-trade-simulator-agent",
                "name_ja": "野球トレードシミュレータエージェント",
                "name_en": "Baseball Trade Simulator Agent",
                "description_ja": "トレード提案のシミュレーション、サラリー、ロスター、MLBルールの考慮、トレード後の戦力変化の予測、評価",
                "description_en": "Simulate trade proposals, consider salary, roster, MLB rules, predict post-trade roster changes, evaluate trade outcomes",
                "features": [
                    "Trade Sim",
                    "Salary Cap",
                    "Roster Rules",
                    "Roster Impact",
                    "Win Value",
                    "Trade Evaluation"
                ],
                "tech_stack": ["pandas", "numpy", "scipy", "matplotlib", "networkx"]
            }
        ]
    },
    {
        "id": "game-esports",
        "name_ja": "ゲームeスポーツ・大会エージェント",
        "name_en": "Game Esports & Tournament Agents",
        "agents": [
            {
                "id": "game-esports-calendar-agent",
                "name_ja": "ゲームeスポーツカレンダーエージェント",
                "name_en": "Game Esports Calendar Agent",
                "description_ja": "主要eスポーツ大会のスケジュール管理、資格、予選、決勝の情報統合、リマインダー、ストリームリンクの提供",
                "description_en": "Major esports tournament schedule management, integrate qualification, prelim, finals info, reminders, stream links",
                "features": [
                    "Tournament Schedule",
                    "Qualification Info",
                    "Reminders",
                    "Stream Links",
                    "Multi-Game Support",
                    "Calendar Export"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "icalendar", "discord.py"]
            },
            {
                "id": "game-pro-team-agent",
                "name_ja": "ゲームプロチームエージェント",
                "name_en": "Game Pro Team Agent",
                "description_ja": "プロチームの情報、ロスター、成績追跡、チーム戦略、シグネチャーの分析、移籍、契約、解散の情報管理",
                "description_en": "Pro team info, roster, performance tracking, team strategy, signature analysis, manage transfer, contract, disband info",
                "features": [
                    "Team Profiles",
                    "Roster Tracking",
                    "Performance Stats",
                    "Strategy Analysis",
                    "Transfer News",
                    "Contract Info"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "networkx", "matplotlib"]
            },
            {
                "id": "game-pro-player-agent",
                "name_ja": "ゲームプロ選手エージェント",
                "name_en": "Game Pro Player Agent",
                "description_ja": "プロ選手のプロフィール、成績、プレイスタイル、チャンピオン/キャラクターの得意・苦手、ランキング、賞金、キャリアの追跡",
                "description_en": "Pro player profile, performance, play style, champ/character strengths/weaknesses, ranking, prize money, career tracking",
                "features": [
                    "Player Profiles",
                    "Performance Stats",
                    "Play Style",
                    "Champ Mastery",
                    "Rankings",
                    "Prize Tracking"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "scikit-learn", "matplotlib"]
            },
            {
                "id": "game-tournament-bracket-agent",
                "name_ja": "ゲーム大会ブラケットエージェント",
                "name_en": "Game Tournament Bracket Agent",
                "description_ja": "トーナメントブラケットの可視化、予測、勝率計算、マッチアップ分析、ライブ更新、結果通知",
                "description_en": "Tournament bracket visualization, predictions, win rate calculation, matchup analysis, live updates, result notifications",
                "features": [
                    "Bracket Viz",
                    "Predictions",
                    "Win Rates",
                    "Matchup Analysis",
                    "Live Updates",
                    "Result Alerts"
                ],
                "tech_stack": ["pandas", "numpy", "requests", "matplotlib", "networkx"]
            },
            {
                "id": "game-esports-analytics-agent",
                "name_ja": "ゲームeスポーツ分析エージェント",
                "name_en": "Game Esports Analytics Agent",
                "description_ja": "プロレベルのプレイ分析、メタの追跡、パッチによる環境変化の影響分析、アマチュア・プロのギャップ分析、上達のヒント",
                "description_en": "Pro-level play analysis, meta tracking, analyze patch impact on meta, amateur-pro gap analysis, improvement tips",
                "features": [
                    "Pro Play Analysis",
                    "Meta Tracking",
                    "Patch Impact",
                    "Gap Analysis",
                    "Improvement Tips",
                    "Trend Reports"
                ],
                "tech_stack": ["pandas", "numpy", "scikit-learn", "matplotlib", "seaborn"]
            }
        ]
    }
]

# プロジェクト設定
PROJECT_NAME = "Next Projects V20"
PROJECT_DIR = "/workspace"
PROGRESS_FILE = "/workspace/v20_progress.json"


def load_progress():
    """進捗を読み込む"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "project": PROJECT_NAME,
        "started_at": datetime.utcnow().isoformat(),
        "projects": {},
        "total_projects": len(PROJECTS),
        "total_agents": sum(len(p['agents']) for p in PROJECTS),
        "completed_projects": 0,
        "completed_agents": 0
    }


def save_progress(progress):
    """進捗を保存する"""
    progress["updated_at"] = datetime.utcnow().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def create_agent_directory(agent):
    """エージェントディレクトリを作成"""
    agent_dir = f"{PROJECT_DIR}/agents/{agent['id']}"
    os.makedirs(agent_dir, exist_ok=True)
    return agent_dir


def generate_agent_py(agent):
    """agent.py を生成"""
    template = '''#!/usr/bin/env python3
"""
__NAME_JA__ / __NAME_EN__
__AGENT_ID__

__DESCRIPTION_JA__
__DESCRIPTION_EN__
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .db import Database
from .discord import DiscordBot

logger = logging.getLogger(__name__)


class __CLASS_NAME__:
    """__NAME_JA__"""

    def __init__(self, db: Database, discord: Optional[DiscordBot] = None):
        self.db = db
        self.discord = discord
        self.agent_id = "__AGENT_ID__"

    async def initialize(self):
        """初期化処理"""
        logger.info(f"Initializing {self.agent_id}...")
        await self.db.initialize()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        メイン処理

        Args:
            data: 入力データ

        Returns:
            処理結果
        """
        try:
            result = {"status": "success", "data": data}
            return result
        except Exception as e:
            logger.error(f"Error in {self.agent_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """ステータス取得"""
        return {
            "agent_id": self.agent_id,
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def cleanup(self):
        """クリーンアップ"""
        logger.info(f"Cleaning up {self.agent_id}...")
'''
    class_name = snake_to_camel(agent['id'])
    template = template.replace("__AGENT_ID__", agent['id'])
    template = template.replace("__NAME_JA__", agent['name_ja'])
    template = template.replace("__NAME_EN__", agent['name_en'])
    template = template.replace("__DESCRIPTION_JA__", agent['description_ja'])
    template = template.replace("__DESCRIPTION_EN__", agent['description_en'])
    template = template.replace("__CLASS_NAME__", class_name)
    return template


def generate_db_py(agent):
    """db.py を生成"""
    template = '''#!/usr/bin/env python3
"""
Database for __NAME_JA__ / __NAME_EN__
"""

import sqlite3
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Database for __AGENT_ID__"""

    def __init__(self, db_path: str = "data/__AGENT_ID__.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None

    async def initialize(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        logger.info(f"Database initialized: {self.db_path}")

    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Main entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Entry tags relation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (entry_id, tag_id),
                FOREIGN KEY (entry_id) REFERENCES entries(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            )
        """)

        self.conn.commit()

    async def create_entry(self, title: str, content: str, category: str = None, tags: List[str] = None) -> int:
        """Create a new entry"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (title, content, category, tags)
            VALUES (?, ?, ?, ?)
        """, (title, content, category, ','.join(tags or [])))
        self.conn.commit()
        entry_id = cursor.lastrowid

        if tags:
            for tag in tags:
                await self._add_tag_to_entry(entry_id, tag)

        return entry_id

    async def _add_tag_to_entry(self, entry_id: int, tag_name: str):
        """Add a tag to an entry"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))
        self.conn.commit()
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        tag_id = cursor.fetchone()[0]
        cursor.execute('INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)',
                      (entry_id, tag_id))
        self.conn.commit()

    async def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get an entry by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0], "title": row[1], "content": row[2],
                "category": row[3], "tags": row[4].split(',') if row[4] else [],
                "created_at": row[5], "updated_at": row[6]
            }
        return None

    async def list_entries(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entries"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute('SELECT * FROM entries WHERE category = ? ORDER BY created_at DESC LIMIT ?',
                          (category, limit))
        else:
            cursor.execute('SELECT * FROM entries ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        return [{
            "id": row[0], "title": row[1], "content": row[2],
            "category": row[3], "tags": row[4].split(',') if row[4] else [],
            "created_at": row[5], "updated_at": row[6]
        } for row in rows]

    async def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """Search entries"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        return [{
            "id": row[0], "title": row[1], "content": row[2],
            "category": row[3], "tags": row[4].split(',') if row[4] else [],
            "created_at": row[5], "updated_at": row[6]
        } for row in rows]

    async def update_entry(self, entry_id: int, title: str = None, content: str = None,
                          category: str = None, tags: List[str] = None) -> bool:
        """Update an entry"""
        cursor = self.conn.cursor()
        updates = []
        values = []

        if title:
            updates.append("title = ?")
            values.append(title)
        if content:
            updates.append("content = ?")
            values.append(content)
        if category:
            updates.append("category = ?")
            values.append(category)
        if tags is not None:
            updates.append("tags = ?")
            values.append(','.join(tags))

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(entry_id)
            cursor.execute(f"UPDATE entries SET {', '.join(updates)} WHERE id = ?", values)
            self.conn.commit()
            return cursor.rowcount > 0
        return False

    async def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM entry_tags WHERE entry_id = ?', (entry_id,))
        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
'''
    template = template.replace("__AGENT_ID__", agent['id'])
    template = template.replace("__NAME_JA__", agent['name_ja'])
    template = template.replace("__NAME_EN__", agent['name_en'])
    return template


def generate_discord_py(agent):
    """discord.py を生成"""
    features_list = '\n'.join([f'            - {f}' for f in agent['features']])
    template = '''#!/usr/bin/env python3
"""
Discord Bot Integration for __NAME_JA__ / __NAME_EN__
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord Bot for __AGENT_ID__"""

    def __init__(self, command_prefix: str = "!", db=None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db = db
        self.agent_id = "__AGENT_ID__"

    async def setup_hook(self):
        """Bot setup"""
        logger.info(f"Setting up {self.agent_id} Discord bot...")
        await self.add_cog(__CLASS_NAME__Commands(self))

    async def on_ready(self):
        """Bot is ready"""
        logger.info(f"{self.user.name} is ready!")


class __CLASS_NAME__Commands(commands.Cog):
    """Commands for __AGENT_ID__"""

    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @commands.command(name="status")
    async def status(self, ctx: commands.Context):
        """Check agent status"""
        await ctx.send(f"✅ {self.bot.agent_id} is active!")

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """Show help"""
        help_text = f"""
📚 **__NAME_JA__ Help**

**Features:**
__FEATURES_LIST__

**Commands:**
- `!status` - Check agent status
- `!help` - Show this help message
- `!create <title> <content>` - Create new entry
- `!list [category]` - List entries
- `!search <query>` - Search entries
- `!get <id>` - Get entry by ID
"""
        help_text = help_text.replace("__AGENT_ID__", agent['id'])
        help_text = help_text.replace("__NAME_JA__", agent['name_ja'])
        help_text = help_text.replace("__FEATURES_LIST__", features_list)
        help_text = help_text.replace("__CLASS_NAME__", snake_to_camel(agent['id']))
        await ctx.send(help_text)

    @commands.command(name="create")
    async def create_entry(self, ctx: commands.Context, title: str, *, content: str):
        """Create a new entry"""
        if self.bot.db:
            entry_id = await self.bot.db.create_entry(title, content)
            await ctx.send(f"✅ Created entry #{entry_id}")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="list")
    async def list_entries(self, ctx: commands.Context, category: str = None):
        """List entries"""
        if self.bot.db:
            entries = await self.bot.db.list_entries(category, limit=10)
            if entries:
                response = "📋 **Entries:\\n"
                for entry in entries:
                    response += f"- #{entry['id']}: {entry['title']}\\n"
                await ctx.send(response)
            else:
                await ctx.send("No entries found")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="search")
    async def search_entries(self, ctx: commands.Context, *, query: str):
        """Search entries"""
        if self.bot.db:
            entries = await self.bot.db.search_entries(query)
            if entries:
                response = f"🔍 **Search Results for '{query}':\\n"
                for entry in entries:
                    response += f"- #{entry['id']}: {entry['title']}\\n"
                await ctx.send(response)
            else:
                await ctx.send("No results found")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="get")
    async def get_entry(self, ctx: commands.Context, entry_id: int):
        """Get entry by ID"""
        if self.bot.db:
            entry = await self.bot.db.get_entry(entry_id)
            if entry:
                response = f"""
📄 **Entry #{entry['id']}**
**Title:** {entry['title']}
**Category:** {entry.get('category', 'N/A')}
**Content:** {entry['content'][:500]}
{'...' if len(entry['content']) > 500 else ''}
**Tags:** {', '.join(entry.get('tags', []))}
"""
                await ctx.send(response)
            else:
                await ctx.send(f"Entry #{entry_id} not found")
        else:
            await ctx.send("❌ Database not connected")


def create_bot(db, token: str, command_prefix: str = "!") -> DiscordBot:
    """Create and return Discord bot instance"""
    bot = DiscordBot(command_prefix=command_prefix, db=db)
    return bot
'''
    class_name = snake_to_camel(agent['id'])
    template = template.replace("__AGENT_ID__", agent['id'])
    template = template.replace("__NAME_JA__", agent['name_ja'])
    template = template.replace("__NAME_EN__", agent['name_en'])
    template = template.replace("__CLASS_NAME__", class_name)
    template = template.replace("__FEATURES_LIST__", features_list)
    return template


def generate_readme(agent):
    """README.md を生成"""
    tech_list = ', '.join(agent['tech_stack'])
    features_list = '\n'.join([f'- {f}' for f in agent['features']])
    class_name = snake_to_camel(agent['id'])
    template = '''# __NAME_JA__ / __NAME_EN__

__AGENT_ID__

## 概要 / Overview

__DESCRIPTION_JA__

__DESCRIPTION_EN__

## 機能 / Features

__FEATURES_LIST__

## 技術スタック / Tech Stack

- __TECH_LIST__

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd __AGENT_ID__

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import __CLASS_NAME__

# Initialize database
db = Database(db_path="data/__AGENT_ID__.db")
await db.initialize()

# Initialize agent
agent = __CLASS_NAME__(db)
await agent.initialize()

# Process data
result = await agent.process({"key": "value"})
print(result)
```

### Discord Botとして使用 / As a Discord Bot

```python
from discord import DiscordBot

# Create bot
bot = create_bot(db, token="YOUR_DISCORD_TOKEN", command_prefix="!")

# Run bot
bot.run()
```

## データベース構造 / Database Schema

### entries テーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| content | TEXT | コンテンツ |
| category | TEXT | カテゴリ |
| tags | TEXT | タグ（カンマ区切り） |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

## Discordコマンド / Discord Commands

| コマンド | 説明 |
|----------|------|
| `!status` | エージェントのステータスを確認 |
| `!help` | ヘルプを表示 |
| `!create <title> <content>` | 新しいエントリーを作成 |
| `!list [category]` | エントリーを一覧表示 |
| `!search <query>` | エントリーを検索 |
| `!get <id>` | IDでエントリーを取得 |

## ライセンス / License

MIT License
'''
    template = template.replace("__AGENT_ID__", agent['id'])
    template = template.replace("__NAME_JA__", agent['name_ja'])
    template = template.replace("__NAME_EN__", agent['name_en'])
    template = template.replace("__DESCRIPTION_JA__", agent['description_ja'])
    template = template.replace("__DESCRIPTION_EN__", agent['description_en'])
    template = template.replace("__FEATURES_LIST__", features_list)
    template = template.replace("__TECH_LIST__", tech_list)
    template = template.replace("__CLASS_NAME__", class_name)
    return template


def generate_requirements_txt(agent):
    """requirements.txt を生成"""
    template = '''# Core dependencies
discord.py>=2.3.2
aiohttp>=3.9.0

# Database
aiosqlite>=0.19.0

# Tech stack specific
'''
    for tech in agent['tech_stack']:
        template += f'{tech}\n'

    template += '''
# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0
'''
    return template


def snake_to_camel(snake_str: str) -> str:
    """snake_case to CamelCase"""
    return ''.join(x.capitalize() for x in snake_str.replace('-', ' ').replace('_', ' ').split())


def create_agent(agent):
    """エージェントを作成"""
    logger.info(f"Creating agent: {agent['id']}")

    agent_dir = create_agent_directory(agent)

    files = {
        f"{agent_dir}/agent.py": generate_agent_py(agent),
        f"{agent_dir}/db.py": generate_db_py(agent),
        f"{agent_dir}/discord.py": generate_discord_py(agent),
        f"{agent_dir}/README.md": generate_readme(agent),
        f"{agent_dir}/requirements.txt": generate_requirements_txt(agent),
    }

    for filepath, content in files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Created: {filepath}")

    class_name = snake_to_camel(agent['id'])
    with open(f"{agent_dir}/__init__.py", 'w', encoding='utf-8') as f:
        f.write(f'''"""
{agent['name_ja']} / {agent['name_en']}
{agent['id']}
"""

from .agent import {class_name}
from .db import Database
from .discord import DiscordBot, create_bot

__all__ = ['{class_name}', 'Database', 'DiscordBot', 'create_bot']
''')

    logger.info(f"✅ Agent created: {agent['id']}")


def main():
    """メイン処理"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    global logger
    logger = logging.getLogger(__name__)

    progress = load_progress()

    for project in PROJECTS:
        project_id = project['id']
        logger.info("=" * 50)
        logger.info(f"Project: {project['name_ja']}")
        logger.info("=" * 50)

        if project_id not in progress['projects']:
            progress['projects'][project_id] = {
                'name_ja': project['name_ja'],
                'name_en': project['name_en'],
                'agents': {},
                'completed_agents': 0,
                'total_agents': len(project['agents'])
            }

        for agent in project['agents']:
            agent_id = agent['id']
            if agent_id in progress['projects'][project_id]['agents'] and progress['projects'][project_id]['agents'][agent_id].get('completed'):
                logger.info(f"Skipping completed agent: {agent_id}")
                continue

            try:
                create_agent(agent)

                progress['projects'][project_id]['agents'][agent_id] = {
                    'completed': True,
                    'completed_at': datetime.utcnow().isoformat()
                }
                progress['projects'][project_id]['completed_agents'] += 1
                progress['completed_agents'] += 1
                save_progress(progress)

            except Exception as e:
                logger.error(f"Error creating agent {agent_id}: {e}")
                progress['projects'][project_id]['agents'][agent_id] = {
                    'completed': False,
                    'error': str(e),
                    'failed_at': datetime.utcnow().isoformat()
                }
                save_progress(progress)

        # Check if project is complete
        if progress['projects'][project_id]['completed_agents'] == progress['projects'][project_id]['total_agents']:
            progress['projects'][project_id]['completed'] = True
            progress['projects'][project_id]['completed_at'] = datetime.utcnow().isoformat()
            progress['completed_projects'] += 1
            logger.info(f"✅ Project complete: {project['name_ja']}")
            save_progress(progress)

    logger.info("=" * 50)
    logger.info(f"Project: {PROJECT_NAME}")
    logger.info(f"Total Projects: {progress['total_projects']}")
    logger.info(f"Completed Projects: {progress['completed_projects']}")
    logger.info(f"Total Agents: {progress['total_agents']}")
    logger.info(f"Completed Agents: {progress['completed_agents']}")
    logger.info("=" * 50)

    if progress['completed_agents'] == progress['total_agents']:
        logger.info("🎉 All agents created successfully!")
        progress['completed_at'] = datetime.utcnow().isoformat()
        save_progress(progress)
    else:
        logger.info("⚠️ Some agents failed. Check progress for details.")


if __name__ == '__main__':
    main()
