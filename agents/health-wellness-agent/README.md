# Health & Wellness Agent / ヘルス＆ウェルネスエージェント

Health tracking and wellness recommendations

健康追跡とウェルネス推薦

## Features

### Core Features

- **Smart Planning**: Intelligent daily planning and scheduling
- **Priority Management**: Task prioritization and optimization
- **Reminders**: Automated reminders and notifications
- **Analytics**: Data-driven insights and reports
- **Easy Integration**: Seamless integration with other agents

### Available Commands

- **Track**: track management
- **Analyze**: analyze management
- **Recommend**: recommend management
- **Goal**: goal management
- **Report**: report management

## Installation

```bash
pip install -r requirements.txt
python agent.py
```

## Usage

### Add Item

```bash
python agent.py add "Title" "Content"
```

### List Items

```bash
python agent.py list
```

### Get Summary

```bash
python agent.py summary
```

### Discord Bot

```
!heahelp - Show help
!heaadd <title> <content> - Add new item
!healist - List items
!heasummary - Get summary
```

## Database Schema

### health_metrics

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Item title |
| content | TEXT | Item content |
| priority | INTEGER | Priority level |
| status | TEXT | Status |
| metadata | TEXT | Additional data (JSON) |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Update time |

## Integration

Works seamlessly with other lifestyle agents:
- Daily Planner Agent
- Health & Wellness Agent
- Finance Tracker Agent
- Social Connector Agent
- Personal Growth Agent

## License

MIT License
