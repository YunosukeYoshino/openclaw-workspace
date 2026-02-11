# Translation Agent / 翻訳エージェント

## 概要 / Overview

多言語翻訳・翻訳履歴管理・定型文管理機能を備えた翻訳エージェント。
Translation agent with multi-language translation, history management, and common phrase management.

## 機能 / Features

- 🌐 **翻訳** (Translation)
  - 多言語間の翻訳
  - Multi-language translation
  - 自動言語検出
  - Automatic language detection

- 📜 **翻訳履歴** (Translation History)
  - すべての翻訳履歴を表示
  - Display all translation history
  - 翻訳の検索とフィルタリング
  - Search and filter translations

- ⭐ **ブックマーク** (Bookmarks)
  - よく使う翻訳をブックマーク
  - Bookmark frequently used translations
  - カスタム名とメモの追加
  - Add custom names and notes

- 📚 **定型文** (Common Phrases)
  - よく使う定型文を管理
  - Manage commonly used phrases
  - 使用頻度の追跡
  - Track usage frequency

- ⚙️ **言語設定** (Language Preferences)
  - デフォルトの翻訳言語設定
  - Set default translation languages
  - ユーザーごとの設定保存
  - Save settings per user

## データベース構造 / Database Schema

```sql
translation_history (翻訳履歴)
  - id, source_text, translated_text, source_lang, target_lang
  - translation_timestamp, bookmarked

bookmarked_translations (ブックマーク)
  - id, translation_id, name, note, created_at

language_preferences (言語設定)
  - id, user_id, source_lang, target_lang, updated_at

common_translations (定型文)
  - id, phrase, source_lang, translated, target_lang, usage_count
```

## 使い方 / Usage

### Japanese / 日本語

```
翻訳: Hello World -> 日本語
翻訳: from 日本語 to English: こんにちは
翻訳履歴
ブックマーク
ブックマーク: 1, 名前: あいさつ
定型文: 日本語 -> 英語
検索: こんにちは
設定: 日本語 -> 英語
統計
```

### English / 英語

```
translate: Hello World -> Japanese
translate: from Japanese to English: こんにちは
history
bookmarks
bookmark: 1, name: greetings
common phrases: Japanese -> English
search: こんにちは
set lang: Japanese -> English
stats
```

## 例 / Examples

### Japanese

```
翻訳: こんにちは世界 -> 英語
翻訳: from English to Japanese: Good morning
翻訳履歴
ブックマーク: 1, 名前: 挨拶
定型文: 日本語 -> 英語
```

### English

```
translate: こんにちは世界 -> English
translate: from English to Japanese: Good morning
history
bookmark: 1, name: greetings
common phrases: Japanese -> English
```

## 対応言語 / Supported Languages

| 日本語 | English | Code |
|--------|---------|------|
| 日本語 | Japanese | ja |
| 英語 | English | en |
| 中国語 | Chinese | zh |
| 韓国語 | Korean | ko |
| フランス語 | French | fr |
| ドイツ語 | German | de |
| スペイン語 | Spanish | es |
| イタリア語 | Italian | it |
| ポルトガル語 | Portuguese | pt |
| ロシア語 | Russian | ru |

## コマンド一覧 / Command List

| 日本語 | English | 説明 / Description |
|--------|---------|---------------------|
| 翻訳: X -> Y | translate: X -> Y | 翻訳 / Translate |
| from X to Y | from X to Y | 翻訳 / Translate |
| 翻訳履歴 | history / translation history | 履歴を表示 / Show history |
| ブックマーク | bookmarks / saved | ブックマークを表示 / Show bookmarks |
| ブックマーク: ID | bookmark: ID | ブックマーク追加 / Add bookmark |
| 定型文: X -> Y | common phrases: X -> Y | 定型文を表示 / Show common phrases |
| 検索: ... | search: ... | 検索 / Search |
| 設定: X -> Y | set lang: X -> Y | 言語設定 / Set language |
| 統計 | stats | 統計情報 / Statistics |

## 開発状況 / Development Status

- [x] データベース設計 / Database design
- [x] CLI実装 / CLI implementation
- [x] Discord連携 / Discord integration
- [ ] 実際の翻訳API統合 / Real translation API integration
- [ ] Web API化 / Web API
- [ ] 定型文の自動学習機能 / Automatic phrase learning

## 次のステップ / Next Steps

1. Google Translate APIまたはDeepL APIとの統合
2. リアルタイム翻訳機能の実装
3. OCRを用いた画像翻訳
4. 音声翻訳機能
5. ウェブインターフェースの追加

## 注 / Note

現在、翻訳機能はプレースホルダーです。実際の翻訳には、Google Translate APIやDeepL APIなどのサービスとの統合が必要です。
Currently, the translation function is a placeholder. For actual translation, integration with services like Google Translate API or DeepL API is required.
