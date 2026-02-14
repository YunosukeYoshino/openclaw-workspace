# erotic-audit-agent

えっちコンテンツ監査エージェント。監査の管理・実施

## 機能

- えっちコンテンツ監査エージェント。監査の管理・実施
- Discordボット連携
- データベース管理

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python agent.py
```

## コマンド

- `!help` - ヘルプを表示
- `!status` - ステータスを表示

## 設定

環境変数を設定してください：

```bash
export DISCORD_TOKEN="your_discord_token"
```

## ディレクトリ構造

```
erotic-audit-agent/
├── agent.py       - メインエージェントコード
├── db.py          - データベースモジュール
├── discord.py     - Discordボット
├── README.md      - このファイル
└── requirements.txt
```

## ライセンス

MIT License
