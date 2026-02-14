# baseball-speed-performance-agent

野球走力パフォーマンス分析エージェント。走塁・盗塁データの分析

## 機能

- 野球走力パフォーマンス分析エージェント。走塁・盗塁データの分析
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
baseball-speed-performance-agent/
├── agent.py       - メインエージェントコード
├── db.py          - データベースモジュール
├── discord.py     - Discordボット
├── README.md      - このファイル
└── requirements.txt
```

## ライセンス

MIT License
