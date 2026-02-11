# Assistant Agent / アシスタントエージェント

A Discord bot agent for general Q&A, multi-agent integration, and context management.

## Features / 機能

- **General Q&A / 汎用的な質問応答**: Answer questions and provide information
- **Multi-Agent Integration / 複数エージェントの統合**: Coordinate between different agents
- **Context Management / コンテキストの管理**: Store and retrieve conversation context
- **Knowledge Base / 知識ベース**: Search and manage information
- **Conversation History / 会話履歴**: Track and review past conversations
- **Multi-language Support / 多言語対応**: English and Japanese

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使い方

### Commands / コマンド

#### `!ask` - Ask Questions
```
!ask how do I analyze data?
!ask データ分析はどうやればいいですか？
```
Ask the assistant any question. It will search the knowledge base and provide relevant answers.

#### `!agents` - List Available Agents
```
!agents
```
Display all available agents and their commands.

#### `!context` - Manage Context
```
!context set project_name my_project
!context get project_name
!context
```
Store and retrieve conversation context for continuity.

#### `!history` - View Conversation History
```
!history
!history 20
```
View past conversation messages.

#### `!kb` - Knowledge Base
```
!kb search monitoring
```
Search the knowledge base for information.

#### `!help` - Help
```
!help
```
Display help for all assistant commands.

#### `!stats` - Statistics
```
!stats
```
View assistant usage statistics.

## Context Management / コンテキスト管理

The assistant maintains context across conversations:

- **Persistent Context**: Store key-value pairs that persist across sessions
- **Conversation History**: Track all messages in a conversation
- **Multi-language Detection**: Automatically detect English or Japanese

## Integrated Agents / 統合エージェント

The assistant provides access to:

- **Analytics Agent**: Data analysis, reports, visualizations
- **Monitoring Agent**: System monitoring, alerts, performance
- **Integration Agent**: Service integration, data sync, webhooks
- **Automation Agent**: Tasks, workflows, triggers

## Running the Bot / ボットの実行

```python
import discord
from discord.ext import commands
from agent import AssistantAgent

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.add_cog(AssistantAgent(bot))

# Replace with your token
bot.run('YOUR_BOT_TOKEN')
```

## Database Schema / データベース構造

- `conversations`: User conversations
- `messages`: Conversation messages
- `context`: Context key-value pairs
- `agent_commands`: Commands from other agents
- `knowledge`: Knowledge base entries

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## License / ライセンス

MIT
