# Audio Agent / 音楽エージェント

## 概要 / Overview

音楽ファイルの管理、プレイリスト作成、録音管理を行うエージェント。
Agent for managing audio files, creating playlists, and managing recordings.

## 機能 / Features

- 🎵 **音楽ファイル管理** (Audio File Management)
  - 音楽ファイルの追加・更新・削除
  - Add, update, and delete audio files
  - カテゴリとタグによる整理
  - Organize by category and tags

- 📋 **プレイリスト** (Playlists)
  - プレイリストの作成と管理
  - Create and manage playlists
  - 音楽の追加・削除
  - Add and remove audio from playlists

- 🎙️ **録音管理** (Recording Management)
  - 録音の保存と履歴管理
  - Save and manage recording history
  - メモと説明の記録
  - Record notes and descriptions

- 🔍 **検索** (Search)
  - タイトル・タグ・説明による検索
  - Search by title, tags, and description

## データベース構造 / Database Schema

```sql
audio_files (音楽ファイル)
  - id, title, file_path, duration, format, bitrate
  - category, tags, description, created_at, updated_at

playlists (プレイリスト)
  - id, name, description, created_at, updated_at

playlist_items (プレイリスト項目)
  - id, playlist_id, audio_id, position

recordings (録音)
  - id, title, file_path, duration, format, recorded_at, notes
```

## 使い方 / Usage

### Japanese / 日本語

```
追加: 好きな曲, カテゴリ: J-POP, タグ: お気に入り
追加: My Favorite Song, カテゴリ: Pop, タグ: favorite
更新: 1, タグ: お気に入り, 推奨
削除: 1
一覧
一覧: J-POP
検索: 好き
プレイリスト: 作成: My Playlist, 説明: 好きな曲たち
プレイリスト: 1, 追加: 2
プレイリスト一覧
録音: ボイスメモ, ファイル: /path/to/file.mp3, 長さ: 30, 形式: mp3
録音一覧
統計
```

### English / 英語

```
add: Favorite Song, category: Pop, tags: favorite
update: 1, tags: favorite, recommended
delete: 1
list
list: Pop
search: favorite
playlist create: My Playlist, description: Favorite songs
playlist: 1, add: 2
playlists
record: Voice memo, file: /path/to/file.mp3, duration: 30, format: mp3
recordings
stats
```

## コマンド一覧 / Command List

| 日本語 | English | 説明 / Description |
|--------|---------|---------------------|
| 追加: ... | add: ... | 音楽を追加 / Add audio file |
| 更新: ... | update: ... | 音楽を更新 / Update audio file |
| 削除: ... | delete: ... | 音楽を削除 / Delete audio file |
| 一覧 | list / audio | 音楽一覧を表示 / List audio files |
| 検索: ... | search: ... | 音楽を検索 / Search audio files |
| プレイリスト: 作成: ... | playlist create: ... | プレイリスト作成 / Create playlist |
| プレイリスト: ... | playlist: ... | プレイリストに追加 / Add to playlist |
| プレイリスト一覧 | playlists | プレイリスト一覧 / List playlists |
| 録音: ... | record: ... | 録音を追加 / Add recording |
| 録音一覧 | recordings | 録音一覧 / List recordings |
| 統計 | stats | 統計情報を表示 / Show statistics |

## 開発状況 / Development Status

- [x] データベース設計 / Database design
- [x] CLI実装 / CLI implementation
- [x] Discord連携 / Discord integration
- [ ] 音声ファイル解析機能 / Audio file parsing
- [ ] 自動タグ付け / Auto-tagging
- [ ] Web API化 / Web API
