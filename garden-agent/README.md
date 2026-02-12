# Garden Agent / 園芸記録エージェント

園芸記録・植物管理を支援するDiscordボットエージェントです。

A Discord bot agent for tracking garden activities and plant management.

## Features / 機能

- **植物管理 / Plant Management**
  - 植物の登録・追跡
  - カテゴリ別整理（野菜、花、ハーブ、木など）
  - 生育状況の記録

- **収穫記録 / Harvest Tracking**
  - 収穫の記録
  - 数量・品質の追跡
  - 収穫履歴の表示

- **園芸活動 / Garden Activities**
  - 種まき、植え替え、雑草取りなど
  - 活動履歴の記録
  - 作業時間の追跡

- **害虫・病気管理 / Pest & Disease Management**
  - 害虫・病気の記録
  - 重要度別管理
  - 対処状況の追跡

- **種子在庫 / Seed Inventory**
  - 種子の管理
  - 購入日・有効期限の記録
  - 保存場所の追跡

- **水やりスケジュール / Watering Schedule**
  - 植物別の水やり予定
  - 頻度設定
  - 次回予定日の管理

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd garden-agent

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
| `!garden summary` | Show garden summary / サマリー表示 |
| `!garden plant <name> <category>` | Add a plant / 植物追加 |
| `!garden plants [category]` | List plants / 植物一覧 |
| `!garden harvest <id> <qty> <unit>` | Add harvest / 収穫記録 |
| `!garden harvests` | List harvests / 収穫一覧 |
| `!garden activity <type>` | Add activity / 活動記録 |
| `!garden activities [type]` | List activities / 活動一覧 |
| `!garden pest <id> <name> <type>` | Add pest/disease / 害虫追加 |
| `!garden pests [status]` | List pests / 害虫一覧 |
| `!garden seed <name> <qty>` | Add seeds / 種子追加 |
| `!garden seeds` | List seeds / 種子在庫 |
| `!garden water <id> [type]` | Add care record / ケア記録 |
| `!garden watering` | List watering schedule / 水やり予定 |
| `!garden help` | Show help / ヘルプ表示 |

## Database Schema / データベース構造

### Tables / テーブル

- **plants**: 植物 (Plants)
- **plant_care**: 植物ケア (Plant care records)
- **harvests**: 収穫記録 (Harvest records)
- **garden_activities**: 園芸活動 (Garden activities)
- **pests_diseases**: 害虫・病気 (Pests and diseases)
- **seeds**: 種子在庫 (Seed inventory)
- **watering_schedule**: 水やりスケジュール (Watering schedule)

## Configuration / 設定

### Environment Variables / 環境変数

- `DISCORD_TOKEN`: Discordボットトークン (必須)

### Categories / カテゴリ

Plants can be categorized as:
- `vegetable`: 野菜 (Vegetables)
- `flower`: 花 (Flowers)
- `herb`: ハーブ (Herbs)
- `tree`: 木 (Trees)
- `shrub`: 低木 (Shrubs)
- `fruit`: 果物 (Fruits)
- `succulent`: 多肉植物 (Succulents)

## Examples / 使用例

```
# Add a plant / 植物追加
!garden plant トマト vegetable
!garden plant バラ flower

# List all plants / 植物一覧
!garden plants
!garden plants vegetable

# Add harvest / 収穫記録
!garden harvest 1 500 g good

# Add garden activity / 園芸活動記録
!garden activity sowing
!garden activity weeding 除草完了

# Add pest record / 害虫記録
!garden pest 1 アブラムシ pest moderate

# List seeds / 種子在庫
!garden seeds

# Record watering / 水やり記録
!garden water 1
!garden water 2 fertilizing 肥料を与えた
```

## Plant Care Types / ケアの種類

- `watering`: 水やり (Watering)
- `fertilizing`: 施肥 (Fertilizing)
- `pruning`: 剪定 (Pruning)
- `pest_control`: 害虫対策 (Pest control)

## Activity Types / 活動の種類

- `sowing`: 種まき (Sowing)
- `transplanting`: 植え替え (Transplanting)
- `weeding`: 雑草取り (Weeding)
- `mulching`: マルチング (Mulching)
- `pruning`: 剪定 (Pruning)
- `watering`: 水やり (Watering)
- `fertilizing`: 施肥 (Fertilizing)
- `harvesting`: 収穫 (Harvesting)

## License / ライセンス

MIT License
