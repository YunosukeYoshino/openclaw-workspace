# Workout Agent

**ワークアウト記録エージェント**

---

## 概要 / Overview

Workout Agentは、ワークアウトの記録と追跡を管理するAIエージェントです。エクササイズの種類、セット数、レップ数、重量などのデータを管理し、進捗を追跡します。

Workout Agent is an AI agent for managing and tracking workout records. It manages exercise data including types, sets, reps, and weight, and tracks progress.

---

## 機能 / Features

### 日本語 / Japanese
- ワークアウトの記録と追跡
- エクササイズの種類管理
- セット数、レップ数、重量の記録
- 進捗の統計表示
- 履歴の参照

### English
- Record and track workouts
- Manage exercise types
- Log sets, reps, and weight
- Display progress statistics
- View workout history

---

## インストール / Installation

```bash
pip install -r requirements.txt
```

---

## 使用方法 / Usage

### コマンド / Commands

#### 日本語 / Japanese
- `!workout add <name> -s <sets> -r <reps> -w <weight>` - ワークアウトを追加
- `!workout list` - ワークアウト一覧を表示
- `!workout stats` - 統計を表示
- `!workout history` - 履歴を表示

#### English
- `!workout add <name> -s <sets> -r <reps> -w <weight>` - Add a workout
- `!workout list` - List workouts
- `!workout stats` - Show statistics
- `!workout history` - Show history

---

## 自動言語検出 / Automatic Language Detection

エージェントは入力メッセージの言語を自動的に検出し、適切な言語で応答します。
The agent automatically detects the language of input messages and responds in the appropriate language.
