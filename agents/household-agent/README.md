# 家事管理エージェント (Household Agent)

家事タスク・メンテナンス管理のためのDiscordボットエージェント

## 機能 / Features

- **家事タスク管理**: 日常的な家事タスクの登録・追跡
- **リマインダー**: 期限付きタスク管理
- **繰り返しタスク**: 定期的な家事（毎週・毎月など）
- **メンテナンス管理**: 家具・設備のメンテナンス予定
- **統計分析**: 未完了タスク数、メンテナンス予定数などの統計

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

### 家事タスク追加 / Add Chore

```
!addchore 掃除機 掃除 毎週
!addchore 洗濯 毎日
```

### 家事一覧 / List Chores

```
!listchores
```

### タスク完了 / Complete Chore

```
!complete 1
```

### メンテナンス追加 / Add Maintenance

```
!maintenance エアコン 点検 2026-05-01
!maintenance 冷蔵庫 清掃 毎年6月
```

### 統計 / Statistics

```
!stats
```

## コマンド一覧 / Command List

| コマンド | エイリアス | 説明 |
|---------|----------|------|
| `!addchore` | `家事追加`, `タスク追加` | 家事タスクを追加 |
| `!listchores` | `家事一覧`, `タスク一覧` | 未完了タスク一覧を表示 |
| `!complete` | `完了`, `done` | タスクを完了にする |
| `!maintenance` | `メンテナンス` | メンテナンスを追加 |
| `!listmaintenance` | `メンテ一覧` | メンテナンス一覧を表示 |
| `!stats` | `統計` | 統計情報を表示 |

## カテゴリ / Categories

- 掃除 (Cleaning)
- 洗濉 (Laundry)
- 料理 (Cooking)
- 買い物 (Shopping)
- 片付け (Organizing)
- クリーニング (Dry Cleaning)

## ボット起動 / Run Bot

```bash
python agent.py
```

---

Created for AI Agents Project (Agent #68)
