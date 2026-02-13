# drift-detector-agent

ドリフト検出エージェント。実際のインフラとコードの差異を検出。

ドリフト検出エージェント。実際のインフラとコードの差異を検出。

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

インフラストラクチャコード化・Terraformエージェント
