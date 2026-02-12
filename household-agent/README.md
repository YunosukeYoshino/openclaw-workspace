# Household Agent / 家事管理エージェント

家事・メンテナンス・修理を管理するDiscordボットエージェントです。

A Discord bot agent for managing household chores, maintenance, and repairs.

## Features / 機能

- **家事タスク管理 / Chores Management**
  - 家事の追加、完了、一覧表示
  - カテゴリ別整理
  - 優先度設定

- **修理記録 / Repairs**
  - 修理の報告・追跡
  - 重要度別管理
  - 修理状況の追跡

- **メンテナンス / Maintenance**
  - 定期メンテナンスの記録
  - 次回予定日の管理

- **用品在庫 / Supplies Inventory**
  - 用品の追加・更新
  - 在庫切れ警告

- **掃除スケジュール / Cleaning Schedule**
  - 掃除タスクのスケジュール管理
  - 頻度（毎日/毎週/毎月）設定

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd household-agent

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
| `!hh summary` | Show household summary / サマリー表示 |
| `!hh chore <name> <category>` | Add a chore / 家事追加 |
| `!hh chores [status]` | List chores / 家事一覧 |
| `!hh complete <id>` | Complete a chore / 家事完了 |
| `!hh repair <item> <issue>` | Add a repair / 修理追加 |
| `!hh repairs [status]` | List repairs / 修理一覧 |
| `!hh maintenance <item> <task>` | Add maintenance / メンテナンス追加 |
| `!hh maintenances` | List maintenance / メンテナンス一覧 |
| `!hh supply <name> <category> [qty]` | Add supply / 用品追加 |
| `!hh supplies [low]` | List supplies / 在庫一覧 |
| `!hh cleaning <area> <task> <freq>` | Add cleaning task / 掃除追加 |
| `!hh cleanings` | List cleaning schedule / 掃除一覧 |
| `!hh help` | Show help / ヘルプ表示 |

## Database Schema / データベース構造

### Tables / テーブル

- **chores**: 家事タスク (Chores)
- **maintenance**: メンテナンスタスク (Maintenance tasks)
- **repairs**: 修理記録 (Repair records)
- **supplies**: 用品在庫 (Supply inventory)
- **cleaning_schedule**: 掃除スケジュール (Cleaning schedule)

## Configuration / 設定

### Environment Variables / 環境変数

- `DISCORD_TOKEN`: Discordボットトークン (必須)

### Customization / カスタマイズ

You can modify the bot's behavior by editing `agent.py`:
- Change command prefix (default: `!hh `)
- Add custom commands
- Modify database schema in `db.py`

## Examples / 使用例

```
# Add a chore / 家事追加
!hh chore 掃除 リビング

# List all pending chores / 未完了家事一覧
!hh chores pending

# Complete a chore / 家事完了
!hh complete 1

# Add a repair / 修理追加
!hh repair 冷蔵庫 冷えない

# Check low stock supplies / 在庫切れチェック
!hh supplies low

# Add cleaning task / 掃除タスク追加
!hh cleaning キッチン 床拭き weekly
```

## License / ライセンス

MIT License
