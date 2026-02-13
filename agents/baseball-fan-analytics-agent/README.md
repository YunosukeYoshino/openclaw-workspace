# baseball-fan-analytics-agent

📊 野球ファン分析エージェント / Baseball Fan Analytics Agent

## 概要 (Overview)

このエージェントは、野球ファン同士の交流を促進し、ライブ視聴体験を強化し、ファンコミュニティを活性化します。

This agent promotes interaction between baseball fans, enhances live viewing experiences, and activates fan communities.

## 機能 (Features)

### メイン機能 (Main Features)
- **マッチメイキング (Matchmaking)**: 趣味・チームが似ているファンを自動マッチング
- **観戦パーティー (Watch Parties)**: 仮想視聴パーティーの開催・管理
- **ファンストーリー (Fan Stories)**: 観戦記録、思い出の収集・共有
- **チャレンジ (Challenges)**: ファン向けゲーム、クイズ、タスク
- **分析 (Analytics)**: ファン行動パターンの分析、トレンド抽出

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使い方 (Usage)

### Python API

```python
from agent import BaseballFanAnalyticsAgentAgent

# エージェント初期化
agent = BaseballFanAnalyticsAgentAgent()

# ファン登録
fan_id = agent.register_fan("discord_id_123", "FanName", favorite_team="Giants")

# 観戦パーティー作成
party_id = agent.create_watch_party(fan_id, "Opening Day Party", "Let's watch together!")

# ストーリー作成
story_id = agent.create_fan_story(fan_id, "Great Game!", "Best game ever...", team="Giants")

# チャレンジ完了
agent.complete_challenge(fan_id, challenge_id=1)

# 接続を閉じる
agent.get_close()
```

### Discord Bot Commands

```
!bf register <team> [location] - ユーザー登録
!bf party create <title> - パーティー作成
!bf story post <content> - ストーリー投稿
!bf challenge list - チャレンジ一覧
!bf help - コマンド一覧
```

## データベース構造 (Database Schema)

- **fans**: ファン情報
- **fan_connections**: ファン接続
- **watch_parties**: 観戦パーティー
- **fan_stories**: ファンストーリー
- **challenges**: チャレンジ
- **challenge_completions**: チャレンジ完了記録
- **fan_points**: ファンポイント
- **engagement_events**: エンゲージメントイベント
- **fan_feedback**: ファンフィードバック

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ライセンス (License)

MIT License
