# container-orchestrator-agent

コンテナオーケストレーターエージェント。コンテナのオーケストレーション。

コンテナオーケストレーターエージェント。コンテナのオーケストレーション。

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

クラウドネイティブ・コンテナ化エージェント
