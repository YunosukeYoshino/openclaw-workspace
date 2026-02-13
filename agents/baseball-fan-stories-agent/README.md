# {agent['name']}

{agent['emoji']} {agent['description_ja']} / {agent['description_en']}

## 概要 (Overview)

このエージェントは、野球ファン同士の交流を促進し、ライブ視聴体験を強化し、ファンコミュニティを活性化します。マッチメイキング、観戦パーティー、ファンストーリー、チャレンジ、分析機能を提供します。

This agent promotes interaction between baseball fans, enhances live viewing experiences, and activates fan communities. It provides matchmaking, watch parties, fan stories, challenges, and analytics features.

## 機能 (Features)

### 野球ファンマッチメイキング (Baseball Fan Matchmaking)
- 趣味・チーム・観戦スタイルが似ているファンを自動マッチング
- ソーシャルメディア分析による相性スコア計算
- 観戦同行の提案、ファン交流イベントの自動企画
- Find and match fans with similar interests, teams, and viewing styles
- Calculate compatibility scores based on social media analysis
- Suggest game-watching companions and automatically organize fan events

### 野球観戦パーティー (Baseball Watch Party)
- 仮想視聴パーティーの開催・管理
- チャット機能、リアクション、ゲーム連動企画の実装
- ライブ投票、プレディクション、ビンゴゲームの統合
- Host and manage virtual watch parties
- Implement chat features, reactions, and game-interactive activities
- Integrate live voting, predictions, and bingo games

### 野球ファンストーリー (Baseball Fan Stories)
- ファンからの観戦記録、思い出の収集・共有
- 写真、ビデオ、感想の統合管理
- タイムライン形式での表示、検索、アーカイブ機能
- Collect and share fan game records and memories
- Unified management of photos, videos, and impressions
- Timeline display, search, and archive features

### 野球ファンチャレンジ (Baseball Fan Challenges)
- ファン向けゲーム、クイズ、チャレンジタスクの作成・管理
- ポイントシステム、ランク付け、バッジ・報酬の付与
- シーズンごとのイベント、スペシャルチャレンジ企画
- Create and manage fan-facing games, quizzes, and challenge tasks
- Point system, ranking, badges, and rewards
- Seasonal events and special challenge campaigns

### 野球ファン分析 (Baseball Fan Analytics)
- ファン行動パターンの分析、トレンド抽出
- チーム別・選手別ファン人気度の可視化
- ファン満足度アンケート、フィードバック収集・分析
- Analyze fan behavior patterns and extract trends
- Visualize team and player popularity among fans
- Collect and analyze fan satisfaction surveys and feedback

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使い方 (Usage)

### Python API

```python
from agent import {agent['name'].replace('-', '_').title().replace('_', '')}Agent

# エージェント初期化 / Initialize agent
agent = {agent['name'].replace('-', '_').title().replace('_', '')}Agent()

# ファン登録 / Register fan
fan_id = agent.register_fan("discord_id_123", "FanName", favorite_team="Giants")

# マッチング / Find matches
matches = agent.find_matching_fans(fan_id, limit=5)

# 観戦パーティー作成 / Create watch party
party_id = agent.create_watch_party(fan_id, "Opening Day Party", "Let's watch together!")

# ストーリー作成 / Create story
story_id = agent.create_fan_story(fan_id, "Great Game!", "Best game ever...", team="Giants")

# チャレンジ完了 / Complete challenge
agent.complete_challenge(fan_id, challenge_id=1)

# 接続を閉じる / Close connection
agent.get_close()
```

### Discord Bot Commands

**ユーザー管理 / User Management**
```
!bf register <team> [players] [location] - ユーザー登録 / Register user
!bf profile - プロフィール確認 / View profile
```

**マッチング / Matchmaking**
```
!bf match [limit] - おすすめファンを検索 / Find recommended fans
```

**観戦パーティー / Watch Parties**
```
!bf party create <title> - パーティー作成 / Create party
!bf party join <party_id> - パーティー参加 / Join party
!bf party list - パーティー一覧 / List parties
```

**ファンストーリー / Fan Stories**
```
!bf story post <content> - ストーリー投稿 / Post story
!bf story list [limit] - ストーリー一覧 / List stories
!bf story mine - 自分のストーリー / My stories
```

**チャレンジ / Challenges**
```
!bf challenge list - チャレンジ一覧 / List challenges
!bf challenge complete <id> - チャレンジ完了 / Complete challenge
!bf challenge points - ポイント確認 / Check points
!bf challenge leaderboard - リーダーボード / Leaderboard
```

**分析 / Analytics**
```
!bf analytics summary - アクティビティサマリー / Activity summary
!bf analytics leaderboard - リーダーボード / Leaderboard
```

**フィードバック / Feedback**
```
!bf feedback <type> <comments> - フィードバック送信 / Send feedback
```

**ヘルプ / Help**
```
!bf help - コマンド一覧 / Command list
```

## データベース構造 (Database Schema)

### fans (ファン情報 / Fan Information)
- id: ユニークID
- discord_id: DiscordユーザーID
- username: ユーザー名
- favorite_team: 好きなチーム
- favorite_players: 好きな選手
- location: 場所
- interests: 興味

### fan_connections (ファン接続 / Fan Connections)
- compatibility_score: 相性スコア
- connection_type: 接続タイプ
- status: ステータス

### watch_parties (観戦パーティー / Watch Parties)
- host_id: ホストID
- title: タイトル
- game_id: 試合ID
- game_time: 試合時間
- max_participants: 最大参加者数

### fan_stories (ファンストーリー / Fan Stories)
- fan_id: ファンID
- title: タイトル
- content: 内容
- game_date: 試合日
- team: チーム
- media_urls: メディアURL

### challenges (チャレンジ / Challenges)
- title: タイトル
- description: 説明
- challenge_type: タイプ
- points_reward: ポイント報酬

### fan_points (ファンポイント / Fan Points)
- fan_id: ファンID
- total_points: 総ポイント
- current_rank: 現在のランク
- badges: バッジ

### engagement_events (エンゲージメントイベント / Engagement Events)
- event_type: イベントタイプ
- fan_id: ファンID
- event_data: イベントデータ

### fan_feedback (ファンフィードバック / Fan Feedback)
- feedback_type: フィードバックタイプ
- rating: 評価
- comments: コメント

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ポイントシステム (Point System)

- チャレンジ完了: 各チャレンジの報酬ポイント
- ストーリー投稿: +5 ポイント
- 観戦パーティー参加: +3 ポイント
- マッチング成功: +2 ポイント

## バッジ・ランク (Badges & Ranks)

- **Bronze**: 0-99 ポイント
- **Silver**: 100-499 ポイント
- **Gold**: 500-999 ポイント
- **Platinum**: 1000+ ポイント

特別バッジ:
- 🏆 MVP: トップ10入賞
- 🌟 Super Fan: 100以上のチャレンジ完了
- 🔥 Streak Master: 連続7日チャレンジ完了

## コントリビューション (Contributing)

プルリクエスト、イシュー、フィードバックを歓迎します！
Pull requests, issues, and feedback are welcome!

## ライセンス (License)

MIT License
