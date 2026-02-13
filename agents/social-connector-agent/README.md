# Social Connector Agent / ソーシャルコネクターエージェント

Social relationship management and reminders

ソーシャル関係管理とリマインダー

## Features

### Core Features

- **Smart Planning**: Intelligent daily planning and scheduling
- **Priority Management**: Task prioritization and optimization
- **Reminders**: Automated reminders and notifications
- **Analytics**: Data-driven insights and reports
- **Easy Integration**: Seamless integration with other agents

### Available Commands

- **Connect**: connect management
- **Remember**: remember management
- **Remind**: remind management
- **Event**: event management
- **Network**: network management

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
!sochelp - Show help
!socadd <title> <content> - Add new item
!soclist - List items
!socsummary - Get summary
```

## Database Schema

### contacts

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
