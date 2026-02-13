# Erotic Content Integration Agent / えっちコンテンツ統合エージェント

Integrates all erotic content agents for unified content management

えっちコンテンツ関連エージェントを統合して、統一されたコンテンツ管理を提供

## Features

### Core Features

- **Unified Data Management**: Centralized data management across all agents
- **Cross-Category Sync**: Synchronize data between different categories
- **Intelligent Search**: Search across multiple categories at once
- **Dashboard Integration**: Visual dashboard for monitoring
- **API Integration**: RESTful API for external integration

### Specific Features

- **Artwork**: artwork management
- **Fanart**: fanart management
- **Character**: character management
- **Artist**: artist management
- **Tag**: tag management
- **Fandom**: fandom management
- **Favorites**: favorites management
- **Rating**: rating management
- **Bookmark**: bookmark management
- **History**: history management
- **Trending**: trending management
- **Recommendation**: recommendation management
- **Creator**: creator management
- **Series**: series management
- **Community**: community management
- **Curation**: curation management
- **Feedback**: feedback management
- **Social**: social management

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
!erohelp - Show help
!eroadd <title> <content> - Add new item
!erolist - List items
!erosearch <query> - Search items
!erosync <source> <target> - Sync categories
!erodashboard - Get dashboard data
```

## Database Schema

### erotic_integrations Table

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
