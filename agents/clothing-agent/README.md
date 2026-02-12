# 服飾管理エージェント (Clothing Agent)

ワードローブ・ファッション管理のためのDiscordボットエージェント

## 機能 / Features

- **アイテム管理**: 衣類・ファッションアイテムの登録と管理
- **カテゴリ別整理**: トップス、ボトムス、アウターなどカテゴリ別に整理
- **アウトフィット作成**: コーディネート（アウトフィット）の登録と管理
- **着用記録**: 着用履歴の追跡と統計
- **買い物リスト**: 欲しいアイテムの管理
- **統計分析**: カテゴリ別のアイテム数、着用回数などの統計

## インストール / Installation

```bash
pip install discord.py
```

## 設定 / Setup

1. Discord Bot Tokenを取得
2. 環境変数を設定:
   ```bash
   export DISCORD_TOKEN="your_bot_token_here"
   ```

## 使用方法 / Usage

### アイテム追加 / Add Item

```
!additem 白いTシャツ トップス ブランド:ユニクロ サイズ:M #夏服
!additem スキニージーンズ ボトムス 色:黒 サイズ:28
```

### アイテム一覧 / List Items

```
!listitems
!listitems トップス
```

### アウトフィット登録 / Add Outfit

```
!outfit 夏のカジュアル 1,3,5 #夏
!outfit ビジネス 2,4,8 #フォーマル
```

### アウトフィット一覧 / List Outfits

```
!listoutfits
```

### 着用記録 / Log Wear

```
!wear 1 今日のカジュアルコーデ
!wear アウトフィット5 今日のオフィス
```

### 買い物リスト / Shopping List

```
!shopping 黒スキニー 予算:5000
!shopping 白シャツ 優先度:高 予算:3000
```

### 統計 / Statistics

```
!stats
```

## コマンド一覧 / Command List

| コマンド | エイリアス | 説明 |
|---------|----------|------|
| `!additem` | `登録`, `アイテム追加` | アイテムを追加 |
| `!listitems` | `アイテム一覧`, `衣類一覧` | アイテム一覧を表示 |
| `!outfit` | `コーデ`, `コーデ登録` | アウトフィットを登録 |
| `!listoutfits` | `コーデ一覧` | アウトフィット一覧を表示 |
| `!wear` | `着用`, `着た` | 着用を記録 |
| `!shopping` | `買い物`, `欲しいもの` | 買い物リストに追加 |
| `!listshopping` | `買い物リスト` | 買い物リストを表示 |
| `!stats` | `統計`, `分析` | 統計情報を表示 |

## カテゴリ / Categories

- トップス (Top/Shirts)
- ボトムス (Bottoms)
- アウター (Outerwear)
- 靴 (Shoes)
- アクセサリー (Accessories)
- インナー (Innerwear)
- バッグ (Bags)
- 帽子 (Hats)
- スカーフ/マフラー (Scarves/Mufflers)

## データベース構造 / Database Structure

### items (アイテム)
- id, name, category, brand, color, size, material, purchase_date, purchase_price, condition, location, image_url, notes, tags

### categories (カテゴリ)
- id, name, color, icon, sort_order

### outfits (アウトフィット)
- id, name, description, items (JSON array of IDs), season, occasion, favorite, last_worn

### wear_logs (着用記録)
- id, item_id, outfit_id, worn_date, notes

### shopping_list (買い物リスト)
- id, name, category, priority, budget, notes, url, purchased, created_at, purchased_at

## ボット起動 / Run Bot

```bash
python agent.py
```

---

Created for AI Agents Project (Agent #67)
