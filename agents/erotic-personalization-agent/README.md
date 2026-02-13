# えっちコンテンツパーソナライゼーションエージェント

Erotic Content Personalization Agent

## 概要 (Overview)

えっちコンテンツのパーソナライズされたおすすめ、ユーザー設定を管理するエージェント

## 機能 (Features)

- パーソナライズ
- ユーザー設定
- 学習機能
- おすすめ調整

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

### 基本的な使用 (Basic Usage)

```python
from agent import EroticPersonalizationAgent

agent = EroticPersonalizationAgent()
```

### Discord Botとして使用 (Using as Discord Bot)

```bash
python discord.py
```

## データベース構造 (Database Schema)

### preferences
設定テーブル

### recommendations
おすすめテーブル

## コマンド (Commands)

- `!add_preference <name> <data>` - Add Preference
- `!list_preferencess [limit]` - List All Preferences
- `!add_recommendation <name> <data>` - Add Recommendation
- `!list_recommendationss [limit]` - List All Recommendations

## ライセンス (License)

MIT License
