# Integration Agent / 統合エージェント

A Discord bot agent for multi-service integration, data synchronization, and API connections.

## Features / 機能

- **Service Management / サービス管理**: Add and configure external services
- **API Logging / APIロギング**: Track all API calls and responses
- **Data Synchronization / データ同期**: Create and manage sync tasks between services
- **Webhook Support / Webhook対応**: Configure and manage webhooks for event notifications
- **Multi-language Support / 多言語対応**: English and Japanese

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使い方

### Commands / コマンド

#### `!service` - Service Management
```
!service add my_api rest https://api.example.com
!service list
!service info my_api
!service logs my_api
```

#### `!sync` - Data Synchronization
```
!sync create source_service target_service full_sync
!sync status
```

#### `!webhook` - Webhook Management
```
!webhook add notify https://example.com/webhook
!webhook list
!webhook toggle 1 true    # Enable webhook ID 1
!webhook toggle 1 false   # Disable webhook ID 1
```

## Service Types / サービスタイプ

Common service types you can use:
- `rest` - REST API services
- `graphql` - GraphQL endpoints
- `database` - Database connections
- `websocket` - WebSocket connections
- `custom` - Custom integrations

## Sync Types / 同期タイプ

- `full_sync` - Full data synchronization
- `incremental` - Incremental updates only
- `one_way` - One-directional sync
- `bidirectional` - Two-way synchronization

## Running the Bot / ボットの実行

```python
import discord
from discord.ext import commands
from agent import IntegrationAgent

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.add_cog(IntegrationAgent(bot))

# Replace with your token
bot.run('YOUR_BOT_TOKEN')
```

## Database Schema / データベース構造

- `services`: Configured external services
- `api_connections`: API call logs
- `data_syncs`: Data synchronization tasks
- `webhooks`: Webhook configurations

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## License / ライセンス

MIT
