# メモエージェント #2

AIエージェント100個の2つ目！

## 概要

メモの保存・検索・管理を簡単にできるエージェント。

## 機能

- 📝 メモ追加（タイトル、内容、カテゴリ、タグ）
- 📋 メモ一覧（最新順）
- 🔍 メモ検索（キーワード）
- 📁 カテゴリ管理
- 🏷️ タグ管理

## データベース構造

```
memos (メモ)
  - id, title, content, category_id, created_at, updated_at

categories (カテゴリ)
  - id, name, created_at

tags (タグ)
  - id, name, created_at

memo_tags (メモ・タグ紐付け)
  - memo_id, tag_id
```

## 使い方

### CLI版

```bash
cd /workspace/agents/memo-agent
python3 main.py
```

### Discordから使う

```
メモして: プロジェクトXのアイデア, タグ:project, カテゴリ:アイデア

検索して: プロジェクト

メモ一覧
```

## 例

```
メモして: 新しいアプリのアイデア - 音声で入力できるTODOアプリを作りたい
カテゴリ: アイデア
タグ: app, todo, 音声
```

## 達成状況

- [x] データベース設計
- [x] CLI実装
- [x] 基本機能完了
- [ ] Discord連携
- [ ] Web API化
- [ ] エクスポート/インポート

## 次のステップ

1. Discordから使えるようにする
2. Web API化
3. 検索機能拡張（全文検索、あいまい検索）
4. メモのタグ付け自動化
