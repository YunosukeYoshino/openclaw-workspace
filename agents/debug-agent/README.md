# Debug Agent / デバッグ管理エージェント

デバッグセッション、課題、トラブルシューティングを管理するDiscordボットエージェントです。

A Discord bot agent for managing debug sessions, issues, and troubleshooting.

## Features / 機能

- **デバッグセッション / Debug Sessions**
  - デバッグセッションの記録
  - 開始・終了時間の追跡
  - セッションのノート記録

- **課題管理 / Issue Tracking**
  - バグ・課題の報告
  - 重要度・ステータス管理
  - 解決状況の追跡

- **トラブルシューティング / Troubleshooting**
  - 問題の手順記録
  - 解決策の記録
  - ベストプラクティスの保存

- **エラーログ / Error Logs**
  - エラーの記録・追跡
  - 再現手順の保存
  - 関連課題との紐付け

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd debug-agent

# Install dependencies
pip install -r requirements.txt

# Set Discord token
export DISCORD_TOKEN=your_bot_token_here

# Run the bot
python agent.py
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|-------------------|---------------------|
| `!debug summary` | Show debug summary / サマリー表示 |
| `!debug session <title>` | Start debug session / セッション開始 |
| `!debug session end <id>` | End session / セッション終了 |
| `!debug issue <title> <priority>` | Add issue / 課題追加 |
| `!debug issues [status]` | List issues / 課題一覧 |
| `!debug fix <id>` | Mark issue as fixed / 修正完了 |
| `!debug error <message>` | Add error record / エラー記録 |
| `!debug errors` | List errors / エラー一覧 |
| `!debug solution <id> <solution>` | Add solution / 解決策追加 |
| `!debug help` | Show help / ヘルプ表示 |

## Database Schema / データベース構造

### Tables / テーブル

- **debug_sessions**: デバッグセッション (Debug sessions)
- **issues**: 課題 (Issues)
- **error_logs**: エラーログ (Error logs)
- **solutions**: 解決策 (Solutions)
- **troubleshooting_notes**: トラブルシューティングノート (Troubleshooting notes)

## Configuration / 設定

### Environment Variables / 環境変数

- `DISCORD_TOKEN`: Discordボットトークン (必須)

### Priority Levels / 重要度レベル

- `critical`: 致命的 (Critical - blocks deployment)
- `high`: 高 (High - affects major functionality)
- `medium`: 中 (Medium - minor issues)
- `low`: 低 (Low - cosmetic or documentation)

### Issue Status / 課題ステータス

- `open`: 未解決 (Open)
- `in_progress`: 進行中 (In Progress)
- `resolved`: 解決済み (Resolved)
- `closed`: クローズ済み (Closed)

## Examples / 使用例

```
# Start debug session / セッション開始
!debug session ログインバグの調査

# Add issue / 課題追加
!debug issue ユーザー認証が失敗する high

# List open issues / 未解決課題一覧
!debug issues open

# Add error record / エラー記録
!debug error 401 Unauthorized error on /api/login

# Mark issue as fixed / 修正完了
!debug fix 1

# Add solution / 解決策追加
!debug solution 1 JWTトークンの有効期限を延長する
```

## License / ライセンス

MIT License
