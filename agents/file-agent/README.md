# File Management Agent / ファイル管理エージェント

## 概要 / Overview

ファイルの登録・検索・管理を簡単にできるエージェント。
Easily register, search, and manage files.

## 機能 / Features

- 📁 **ファイル登録** (File Registration)
  - ファイル名・パス・カテゴリ・タグ・説明を記録
  - Track filename, path, category, tags, and description

- 🔍 **ファイル検索** (File Search)
  - キーワードでファイルを検索
  - Search files by keyword
  - タグで絞り込み検索
  - Filter search by tag

- 📋 **ファイル一覧** (File List)
  - すべてのファイルを表示
  - Display all files
  - カテゴリ別に表示
  - Display by category

- 📊 **統計情報** (Statistics)
  - ファイル数、サイズ、ダウンロード回数などの統計
  - Statistics including file count, size, download count, etc.

## データベース構造 / Database Schema

```sql
files (ファイル)
  - id, filename, filepath, category, tags, description
  - file_size, file_type, upload_date, download_count, status

categories (カテゴリ)
  - id, name, description, created_at

tags (タグ)
  - id, name, created_at
```

## 使い方 / Usage

### Japanese / 日本語

```
ファイル: ドキュメント.pdf, パス:/docs/document.pdf, カテゴリ:仕事, タグ:work,pdf
ファイル: 写真.jpg, パス:/photos/photo.jpg, タグ:photo
検索: ドキュメント
タグ: work
ファイル一覧
カテゴリ: 仕事
カテゴリ追加: 仕事, 説明: 仕事関連のファイル
統計
```

### English / 英語

```
file: document.pdf, path:/docs/document.pdf, category:work, tags:work,pdf
file: photo.jpg, path:/photos/photo.jpg, tags:photo
search: document
tag: work
files
category: work
add category: work, description: Work-related files
stats
```

## 例 / Examples

### Japanese

```
ファイル: プロジェクト計画書.docx, パス:/work/project-plan.docx, カテゴリ:仕事, タグ:project,docx
ファイル: 夏休みの写真.jpg, パス:/photos/summer.jpg, カテゴリ:写真, タグ:summer,vacation
検索: プロジェクト
タグ: summer
```

### English

```
file: project-plan.docx, path:/work/project-plan.docx, category:work, tags:project,docx
file: summer-vacation.jpg, path:/photos/summer.jpg, category:photos, tags:summer,vacation
search: project
tag: summer
```

## コマンド一覧 / Command List

| 日本語 | English | 説明 / Description |
|--------|---------|---------------------|
| ファイル: ... | file: ... | ファイルを登録 / Register file |
| 検索: ... | search: ... | キーワードで検索 / Search by keyword |
| タグ: ... | tag: ... | タグで検索 / Search by tag |
| ファイル一覧 | files / list | ファイル一覧を表示 / List files |
| カテゴリ: ... | category: ... | カテゴリ別に表示 / List by category |
| カテゴリ追加: ... | add category: ... | カテゴリを追加 / Add category |
| 統計 | stats | 統計情報を表示 / Show statistics |

## 開発状況 / Development Status

- [x] データベース設計 / Database design
- [x] CLI実装 / CLI implementation
- [x] Discord連携 / Discord integration
- [ ] ファイル管理機能の強化 / Enhanced file management
- [ ] Web API化 / Web API
- [ ] ファイルのアップロード/ダウンロード実装 / File upload/download implementation

## 次のステップ / Next Steps

1. 実際のファイルアップロード/ダウンロード機能の実装
2. ウェブインターフェースの追加
3. ファイルのバージョン管理機能
4. 自動分類機能の実装
