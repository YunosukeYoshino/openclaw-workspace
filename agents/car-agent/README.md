# Car Agent / 車管理エージェント

車のメンテナンス、燃料、修理を管理するDiscordボットエージェントです。

A Discord bot agent for managing vehicle maintenance, fuel, and repairs.

## Features / 機能

- **車両情報管理 / Vehicle Management**
  - 車両の登録・追跡
  - 車種、年式、ナンバープレート情報
  - オドメーター記録

- **メンテナンス / Maintenance**
  - 定期メンテナンスの記録
  - オイル交換、タイヤ交換など
  - 次回予定日の管理

- **燃料記録 / Fuel Tracking**
  - 給油記録
  - 燃費計算
  - 燃料費の追跡

- **修理記録 / Repairs**
  - 修理の記録
  - 費用の追跡
  - 修理履歴の表示

- **保険・車検 / Insurance & Inspection**
  - 保険の期限管理
  - 車検の予定
  - 登録情報の管理

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd car-agent

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
| `!car summary` | Show car summary / サマリー表示 |
| `!car add <make> <model> <year>` | Add vehicle / 車両追加 |
| `!car odometer <value>` | Update odometer / 走行距離更新 |
| `!car fuel <amount> <price>` | Add fuel record / 給油記録 |
| `!car maintenance <type>` | Add maintenance / メンテナンス追加 |
| `!car repairs` | List repairs / 修理一覧 |
| `!car insurance <provider> <expiry>` | Set insurance / 保険設定 |
| `!car inspection <date>` | Set inspection date / 車検予定 |
| `!car help` | Show help / ヘルプ表示 |

## Database Schema / データベース構造

### Tables / テーブル

- **vehicles**: 車両情報 (Vehicle information)
- **odometer**: オドメーター記録 (Odometer readings)
- **fuel_records**: 給油記録 (Fuel records)
- **maintenance**: メンテナンス記録 (Maintenance records)
- **repairs**: 修理記録 (Repair records)
- **insurance**: 保険情報 (Insurance information)

## Configuration / 設定

### Environment Variables / 環境変数

- `DISCORD_TOKEN`: Discordボットトークン (必須)

## Examples / 使用例

```
# Add vehicle / 車両追加
!car add Toyota Camry 2020

# Update odometer / 走行距離更新
!car odometer 50000

# Add fuel record / 給油記録
!car fuel 40 1500

# Add maintenance / メンテナンス追加
!car maintenance オイル交換

# Set insurance / 保険設定
!car insurance 任意自動車 2025-12-31
```

## License / ライセンス

MIT License
