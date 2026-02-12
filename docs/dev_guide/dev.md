# dev

testing - テストガイド

## Development Guide

This guide helps developers contribute to the dev.

---

# dev

testing - テストガイド

## 開発者ガイド

このガイドは dev の開発に貢献する開発者をサポートします。

## Prerequisites

### Required Software

- Python 3.10+
- Node.js 18+
- Git
- Docker (optional)

### Required Knowledge

- Python programming
- REST API concepts
- Database basics
- Git workflow

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/YunosukeYoshino/openclaw-workspace.git
cd openclaw-workspace
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Initialize Database

```bash
python3 scripts/init_db.py
```

### 5. Run Development Server

```bash
python3 -m uvicorn dashboard.api:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
openclaw-workspace/
├── agents/              # AI agent implementations
├── dashboard/           # Web dashboard
├── integrations/        # External service integrations
├── event_bus/          # Event bus implementation
├── message_bus/         # Message bus implementation
├── workflow_engine/     # Workflow engine
├── agent_discovery/     # Agent discovery service
├── tests/               # Test suites
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── requirements.txt     # Python dependencies
```

## Coding Standards

### Python Code Style

Follow PEP 8 guidelines:
- Use 4 spaces for indentation
- Maximum line length: 88 characters
- Use snake_case for variables and functions
- Use CamelCase for classes

Example:
```python
from typing import Optional

class AgentManager:
    """Manages agent lifecycle."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.agents = {}

    def start_agent(self, agent_id: str) -> bool:
        """Start an agent by ID."""
        if agent_id not in self.agents:
            return False
        self.agents[agent_id].start()
        return True
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type hints

Example:
```python
def process_data(data: dict) -> dict:
    """Process input data and return results.

    Args:
        data: Input data dictionary.

    Returns:
        Processed data dictionary.

    Raises:
        ValueError: If data is invalid.
    """
    if not data:
        raise ValueError("Data cannot be empty")
    return processed_data
```

### Git Conventional Commits

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Example:
```
feat(agents): add support for new agent type

Add new agent type for handling scheduled tasks.

Closes #123
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suite

```bash
# Unit tests only
pytest tests/unit_tests/ -v

# Integration tests only
pytest tests/integration_tests/ -v

# E2E tests only
pytest tests/e2e_tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Write Tests

Follow the test structure:

```python
import pytest
from unittest.mock import Mock

class TestAgentManager:
    """Test AgentManager class."""

    def setup_method(self):
        """Setup before each test."""
        self.manager = AgentManager()

    def test_start_agent(self):
        """Test starting an agent."""
        self.manager.agents["test"] = Mock()
        result = self.manager.start_agent("test")
        assert result is True
```

## Debugging

### Enable Debug Mode

Set environment variable:
```bash
export DEBUG=true
python3 -m uvicorn dashboard.api:app --reload
```

### Debug Tests

```bash
pytest tests/ -v -s --pdb
```

## Common Issues

### Import Errors

Ensure virtual environment is activated and dependencies are installed:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Database Locks

Stop all running services and remove lock files:
```bash
rm -f *.db-shm *.db-wal
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Run tests and ensure they pass
6. Commit your changes
7. Push to your fork
8. Create a Pull Request

## Resources

- [Project Documentation](/docs)
- [API Documentation](/docs/api_docs)
- [Architecture Documentation](/docs/architecture_docs)
- [Troubleshooting Guide](/docs/troubleshooting)
