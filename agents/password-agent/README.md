# パスワード管理エージェント
# Password Management Agent

AIエージェント100個のうちの1つ！ / One of the 100 AI agents!

## 概要 / Overview

パスワードの安全な保存・管理、強力なパスワード生成を行うエージェント。
An agent for secure password storage, management, and strong password generation.

## 機能 / Features

- 🔐 パスワードの暗号化保存 / Encrypted password storage
- 🆔 サイト名・ユーザー名・URLの管理 / Site name, username, URL management
- 🎲 安全なパスワード生成 / Secure password generation
- 🔍 パスワード検索 / Password search
- 📁 カテゴリ管理 / Category management
- 🏷️ タグ管理 / Tag management
- 💪 パスワード強度チェック / Password strength checker

## セキュリティ / Security

- AES-256-GCM 暗号化 / AES-256-GCM encryption
- PBKDF2 key derivation (100,000 iterations)
- 各パスワードごとに個別のソルト / Individual salt per password
- マスターパスワードで保護 / Protected by master password

## データベース構造 / Database Structure

```
passwords (パスワード)
  - id, site_name, site_url, username, encrypted_password,
    salt, category_id, notes, last_used, created_at, updated_at

categories (カテゴリ)
  - id, name, color, created_at

tags (タグ)
  - id, name, created_at

password_tags (パスワード・タグ紐付け)
  - password_id, tag_id
```

## 使い方 / Usage

### Discordから使う / Using via Discord

```
# パスワード追加 / Add password
パスワード: サイト:example.com, ユーザー:admin, パスワード:pass123
password: site:github.com, username:user1, password:secure123

# パスワード追加（詳細情報）/ Add with details
パスワード: サイト:GitHub, ユーザー:myname, パスワード:securePass123,
           URL:https://github.com, カテゴリ:Work, タグ:code, git, メモ:個人アカウント

# パスワード生成 / Generate password
生成: 20
generate: 16

# パスワード取得 / Get password
取得: 1
get: 2

# 検索 / Search
検索: github
search: example

# 一覧 / List
パスワード一覧
password list

# 更新 / Update
更新: 1, パスワード:newPassword123
update: 2, ユーザー:newuser

# 削除 / Delete
削除: 1
delete: 2

# 強度チェック / Password strength check
強度: myPassword123
strength: TestPass123!

# 統計 / Stats
統計
stats
```

## 例 / Examples

```
# 基本的な追加 / Basic add
パスワード: サイト:Gmail, ユーザー:me@gmail.com, パスワード:securePass123

# パスワード生成して保存 / Generate and save
生成: 24
# 結果を使って保存
パスワード: サイト:NewSite, ユーザー:user, パスワード:[生成されたパスワード]

# 強度チェック / Strength check
強度: weakpass
# フィードバック:
# スコア / Score: 2/7
# レベル / Level: 弱 / Weak
# フィードバック / Feedback:
#   • 8文字以上にしてください
#   • 大文字を含めてください
#   • 記号を含めてください
```

## 達成状況 / Progress

- [x] データベース設計 / Database design
- [x] AES-256-GCM 暗号化 / AES-256-GCM encryption
- [x] パスワード生成機能 / Password generation
- [x] パスワード強度チェック / Password strength checker
- [x] Discord連携 / Discord integration
- [x] 日本語・英語対応 / Japanese & English support
- [ ] マスターパスワード変更機能 / Master password change
- [ ] エクスポート/インポート（暗号化）/ Encrypted export/import
- [ ] 2FA/OTPサポート / 2FA/OTP support
- [ ] ブラウザ拡張連携 / Browser extension integration

## 次のステップ / Next Steps

1. マスターパスワード変更機能 / Master password change feature
2. 暗号化されたエクスポート/インポート / Encrypted export/import
3. パスワード有効期限管理 / Password expiration management
4. 異常なログイン検知 / Suspicious login detection
5. Web API化 / Web API
