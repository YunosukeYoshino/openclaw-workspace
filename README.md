# AI Agent Management System

A comprehensive system for creating, managing, and orchestrating AI agents.

---

# AI Agent Management System

AIエージェントを作成・管理・オーケストレーションするための包括的なシステム。

## Overview

This system provides:
- **65+ AI Agents** for various tasks
- **Web Dashboard** for monitoring and control
- **Event Bus** for agent communication
- **Workflow Engine** for complex automation
- **External Integrations** (Google Calendar, Notion, Slack, Teams)
- **Comprehensive Testing** suite

## Quick Start

```bash
# Clone repository
git clone https://github.com/YunosukeYoshino/openclaw-workspace.git
cd openclaw-workspace

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 scripts/init_db.py

# Run server
python3 -m uvicorn dashboard.api:app --reload

# Open dashboard
# Navigate to http://localhost:8000
```

## Features

### AI Agents

- **65+ pre-built agents** for common tasks
- **Custom agent creation** with minimal code
- **Agent discovery** and management
- **Lifecycle management** (start, stop, restart)

### Web Dashboard

- Real-time agent monitoring
- Status visualization with charts
- Agent control interface
- Real-time log viewing
- Activity history tracking

### Event System

- **Pub/Sub event bus** for communication
- **Event logging** and history
- **Workflow triggers** based on events
- **Agent event subscriptions**

### External Integrations

- Google Calendar API
- Notion API
- Slack integration
- Teams integration
- Webhook support

## Documentation

- [API Documentation](docs/api_docs)
- [Architecture Documentation](docs/architecture_docs)
- [Developer Guide](docs/dev_guide)
- [Troubleshooting Guide](docs/troubleshooting)
- [FAQ](docs/faq)

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test suite
pytest tests/unit_tests/ -v
pytest tests/integration_tests/ -v
pytest tests/e2e_tests/ -v
```

## Deployment

### Docker

```bash
# Build image
docker build -t ai-agents .

# Run container
docker-compose up -d
```

### Production

See [Deployment Guide](docs/dev_guide/dev-setup) for production deployment instructions.

## Project Structure

```
openclaw-workspace/
├── agents/              # AI agent implementations (65+)
├── dashboard/           # Web dashboard (FastAPI + Vue.js)
├── integrations/         # External service integrations
├── event_bus/           # Event bus system
├── message_bus/         # Message bus system
├── workflow_engine/     # Workflow engine
├── agent_discovery/     # Agent discovery service
├── tests/               # Test suites
│   ├── unit_tests/      # Unit tests (10)
│   ├── integration_tests/ # Integration tests (8)
│   ├── e2e_tests/       # E2E tests (6)
│   └── load_tests/      # Load tests (4)
├── docs/                # Documentation
└── scripts/             # Utility scripts
```

## Architecture

```
Frontend (Dashboard)
    ↓
API Layer (FastAPI)
    ↓
Service Layer (Agent Manager, Workflow Engine)
    ↓
Event Bus → Message Bus
    ↓
Data Layer (SQLite, Redis)
```

See [Architecture Documentation](docs/architecture_docs) for detailed information.

## Contributing

We welcome contributions! Please see [Contributing Guide](docs/dev_guide/dev-coding).

## License

MIT License - see LICENSE file for details.

## Support

- [Documentation](docs)
- [GitHub Issues](https://github.com/YunosukeYoshino/openclaw-workspace/issues)
- [Discord Community](https://discord.gg/clawd)

## Status

✅ AI Agent Development: 65/65
✅ Agent Completion: 119/119
✅ Web Dashboard: 9/9
✅ Agent Integration: 5/5
✅ External Integrations: 5/5
✅ Long-term Projects: 9/9
✅ Test & Deployment Prep: 4/4
✅ Next Phase: 25/25
✅ Test Suite: 30/30
✅ Documentation: 15/15

**Total Progress**: 276 tasks completed

---

## Roadmap

- [ ] Production deployment
- [ ] Performance optimization
- [ ] Additional integrations
- [ ] Mobile app
- [ ] Advanced analytics
