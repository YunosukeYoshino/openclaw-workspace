# tax-agent

SQLite ベースの税金記録管理エージェント。自然言語解析によるメッセージ処理をサポートし、日本語と英語に対応しています。

## 構成

- `db.py` - SQLite データベース管理モジュール
- `discord.py` - Discord ボット + 自然言語パーサー

## 機能

### 税金記録の追加
```
add 5000 expense office supplies
記録 ¥10000 所得 フリーランス 2024
```

### 記録の一覧表示
```
list 2024
show expense 2024
一覧 (全年度)
```

### 集計・サマリー
```
summary 2024
total expense 2024
集計 2024
```

### 検索
```
search office
find freelance
検索 オフィス
```

### 削除
```
delete 123
削除 123
```

### 言語設定
```
set language english
言語設定 日本語
```

## カテゴリ

- `income` / `所得` - 収入
- `expense` / `経費` - 経費・出費
- `deduction` / `控除` - 控除
- `tax_paid` / `納税` - 納税
- `other` / `その他` - その他

## データベース構造

### tax_records
- `id` - 記録ID
- `user_id` - ユーザーID
- `year` - 年度
- `category` - カテゴリ
- `amount` - 金額
- `description` - 説明
- `date_recorded` - 記録日時
- `tags` - タグ

### categories
- `id` - カテゴリID
- `name` - 内部名称
- `name_en` - 英語名称
- `name_ja` - 日本語名称

### user_settings
- `user_id` - ユーザーID
- `language` - 言語設定 (ja/en)
- `timezone` - タイムゾーン
- `currency` - 通貨

## テスト

CLI モードでテスト:
```bash
python3 discord.py
```

## Discord ボットとして実行

`discord.py` に `discord.py` ライブラリが必要です:

```bash
pip install discord.py
```

ボットトークンを設定して実行:
```python
bot = create_discord_bot()
bot.run('YOUR_BOT_TOKEN')
```

## 依存関係

- Python 3.7+
- sqlite3 (標準ライブラリ)
- discord.py (オプション、ボット機能使用時)
