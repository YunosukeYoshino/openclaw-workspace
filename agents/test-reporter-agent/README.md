# test-reporter-agent

テストレポーターエージェント。テスト結果の収集とレポート作成。

テストレポーターエージェント。テスト結果の収集とレポート作成。

## Files

- `agent.py` - メインエージェントコード
- `db.py` - データベースモジュール
- `discord.py` - Discord Botモジュール
- `requirements.txt` - Python依存パッケージ

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Agent

```bash
python agent.py
```

### Database

```bash
python db.py
```

### Discord Bot

```bash
python discord.py
```

## Commands

- `!status` - Show bot status
- `!add <title> <content>` - Add an entry
- `!list [limit]` - List entries

## Project

テスト自動化・品質保証エージェント
