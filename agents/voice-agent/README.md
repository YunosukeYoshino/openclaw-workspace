# Voice Assistant Agent / 音声アシスタントエージェント

## 概要 / Overview

音声認識・音声合成・音声コマンド管理機能を備えた音声アシスタントエージェント。
Voice assistant agent with speech recognition, text-to-speech synthesis, and voice command management.

## 機能 / Features

- 🎤 **音声認識** (Speech Recognition)
  - 音声コマンドの登録と管理
  - Register and manage voice commands
  - パターンマッチングによるコマンド認識
  - Command recognition through pattern matching

- 🔊 **音声合成** (Text-to-Speech)
  - テキストの音声出力
  - Text-to-speech output
  - 音声設定のカスタマイズ
  - Customize voice settings

- 📜 **履歴管理** (History Management)
  - 音声認識履歴の保存と表示
  - Save and display speech recognition history
  - TTS履歴の記録
  - Record TTS history

- 📚 **カスタム語彙** (Custom Vocabulary)
  - 専門用語の発音登録
  - Register pronunciation of technical terms
  - カテゴリ別の語彙管理
  - Manage vocabulary by category

- ⚙️ **音声設定** (Voice Settings)
  - 認識言語の設定
  - Set recognition language
  - TTS音声・速度・ピッチの調整
  - Adjust TTS voice, speed, and pitch

## データベース構造 / Database Schema

```sql
voice_commands (音声コマンド)
  - id, command_name, command_pattern, action_type, action_params
  - description, created_at, usage_count, active

voice_history (音声履歴)
  - id, transcription, recognized_command_id, action_executed, success, timestamp

tts_history (TTS履歴)
  - id, text, voice_id, duration, file_path, created_at

voice_settings (音声設定)
  - id, user_id, recognition_language, tts_voice_id, tts_speed, tts_pitch, auto_response

custom_vocabulary (カスタム語彙)
  - id, word, pronunciation, category, created_at
```

## 使い方 / Usage

### Japanese / 日本語

```
コマンド追加: 挨拶, パターン: おはよう, アクション: greeting
コマンド一覧
コマンド削除: 挨拶
音声履歴
TTS履歴
語彙追加: AIエージェント, 発音: エーアイエージェント, カテゴリ: テクニカル
語彙一覧
語彙一覧: テクニカル
設定: 認識: ja-JP, 音声: default, 速度: 1.0
統計
```

### English / 英語

```
add command: greeting, pattern: good morning, action: greeting
commands
delete command: greeting
voice history
tts history
add vocab: AI agent, pronunciation: AI agent, category: technical
vocabulary
vocabulary: technical
setting: recognition: ja-JP, voice: default, speed: 1.0
stats
```

## 例 / Examples

### Japanese

```
コマンド追加: 天気予報, パターン: 天気教えて, アクション: weather, パラメータ: 今日
コマンド追加: ミュージック, パターン: 音楽再生, アクション: play_music
語彙追加: OpenAI, 発音: オープンエーアイ, カテゴリ: 企業名
```

### English

```
add command: weather report, pattern: what's the weather, action: weather, params: today
add command: music, pattern: play music, action: play_music
add vocab: OpenAI, pronunciation: Open AI, category: company
```

## コマンド一覧 / Command List

| 日本語 | English | 説明 / Description |
|--------|---------|---------------------|
| コマンド追加: ... | add command: ... | 音声コマンドを追加 / Add voice command |
| コマンド一覧 | commands / list commands | コマンド一覧を表示 / List commands |
| コマンド削除: ... | delete command: ... | コマンドを削除 / Delete command |
| 音声履歴 | voice history / history | 音声認識履歴を表示 / Show voice history |
| TTS履歴 | tts history / speech history | TTS履歴を表示 / Show TTS history |
| 語彙追加: ... | add vocab: ... | 語彙を追加 / Add vocabulary |
| 語彙一覧 | vocab / vocabulary | 語彙一覧を表示 / List vocabulary |
| 設定: ... | setting: ... | 音声設定を変更 / Change voice settings |
| 統計 | stats | 統計情報を表示 / Show statistics |

## 開発状況 / Development Status

- [x] データベース設計 / Database design
- [x] CLI実装 / CLI implementation
- [x] Discord連携 / Discord integration
- [ ] 実際の音声認識・TTS統合 / Real speech recognition & TTS integration
- [ ] Web API化 / Web API
- [ ] 音声コマンドの実行機能 / Voice command execution

## 次のステップ / Next Steps

1. Google Speech-to-Text APIとの統合
2. ElevenLabs、Google TTS、またはAzure TTSとの統合
3. リアルタイム音ストリーミング機能
4. 音声コマンドの実行エンジンの実装
5. ウェブインターフェースの追加
6. マルチユーザー対応の強化

## 注 / Note

現在、音声認識・音声合成機能はプレースホルダーです。実際の機能には、Google Speech-to-Text API、Google TTS、ElevenLabsなどのサービスとの統合が必要です。
Currently, speech recognition and text-to-speech functions are placeholders. For actual functionality, integration with services like Google Speech-to-Text API, Google TTS, ElevenLabs, etc. is required.
