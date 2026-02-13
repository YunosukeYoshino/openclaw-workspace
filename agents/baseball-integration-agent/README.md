# Baseball Integration Agent / 野球統合エージェント

Integrates all baseball-related agents for unified baseball data management

野球関連エージェントを統合して、統一された野球データ管理を提供

## Features

### Core Features

- **Unified Data Management**: Centralized data management across all agents
- **Cross-Category Sync**: Synchronize data between different categories
- **Intelligent Search**: Search across multiple categories at once
- **Dashboard Integration**: Visual dashboard for monitoring
- **API Integration**: RESTful API for external integration

### Specific Features

- **Score**: score management
- **News**: news management
- **Stats**: stats management
- **Schedule**: schedule management
- **Prediction**: prediction management
- **Team**: team management
- **Player**: player management
- **History**: history management
- **Chart**: chart management
- **Fan**: fan management

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python agent.py
```

## Usage

### CLI Usage

```bash
# Add new item
python agent.py add "Title" "Content"

# List items
python agent.py list

# Search items
python agent.py search "query"
```

### Discord Bot Usage

```
!bashelp - Show help
!basadd <title> <content> - Add new item
!baslist - List items
!bassearch <query> - Search items
!bassync <source> <target> - Sync categories
!basdashboard - Get dashboard data
```

## Database Schema

### baseball_integrations Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Item title |
| content | TEXT | Item content |
| source | TEXT | Source of the item |
| category | TEXT | Category |
| status | TEXT | Status (active/archived) |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Update time |

### entries Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| type | TEXT | Entry type |
| title | TEXT | Entry title |
| content | TEXT | Entry content |
| status | TEXT | Status |
| priority | INTEGER | Priority level |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Update time |

## API Endpoints

- `GET /api/integrations` - List all integrations
- `POST /api/integrations` - Create new integration
- `GET /api/integrations/:id` - Get single integration
- `PUT /api/integrations/:id` - Update integration
- `DELETE /api/integrations/:id` - Delete integration
- `GET /api/search` - Search across categories
- `POST /api/sync` - Sync categories

## Configuration

Environment variables:

- `DATABASE_PATH`: Path to database file
- `DISCORD_TOKEN`: Discord bot token
- `API_PORT`: API server port (default: 8000)

## Development

```bash
# Run tests
pytest

# Format code
black .
```

## License

MIT License
