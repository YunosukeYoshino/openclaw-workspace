# faq

technical - 技術的な質問

## Frequently Asked Questions

Common questions about the faq.

---

# faq

technical - 技術的な質問

## よくある質問

faq に関するよくある質問。

## General Questions

### What is this system?

**A:** This is an AI agent management system that allows you to create, manage, and orchestrate AI agents for various tasks. It provides a web dashboard for monitoring and control.

---

### What are the system requirements?

**A:** Minimum requirements:
- Python 3.10+
- 2GB RAM
- 1GB disk space
- Network connection (for integrations)

Recommended requirements:
- Python 3.11+
- 4GB RAM
- 5GB disk space
- Stable internet connection

---

### Is it free to use?

**A:** Yes, this system is open source and free to use. Some external integrations (Google Calendar, Slack, etc.) may require their own accounts.

---

### How do I get started?

**A:**
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize the database: `python3 scripts/init_db.py`
4. Run the server: `python3 -m uvicorn dashboard.api:app --reload`
5. Open http://localhost:8000 in your browser

---

## Technical Questions

### What database does it use?

**A:** SQLite is the default database. It's lightweight and requires no additional setup. For production, PostgreSQL or MySQL can be configured.

---

### How do I add a new agent?

**A:**
1. Create a new directory in `agents/`
2. Add `agent.py` with your agent implementation
3. Add `db.py` for database operations
4. Add `README.md` with documentation
5. The agent will be automatically discovered

---

### Can I run multiple instances?

**A:** Yes, the system is designed for horizontal scaling. You can run multiple instances behind a load balancer. Database and Redis should be shared across instances.

---

### How do I integrate with external services?

**A:** External integrations are in the `integrations/` directory. Each integration has its own client and configuration. Add your API credentials to the environment variables.

---

### What's the difference between unit, integration, and E2E tests?

**A:**
- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test how components work together
- **E2E tests**: Test the entire system from user perspective

---

### How do I deploy to production?

**A:**
1. Set environment variables for production
2. Update configuration files
3. Build Docker image: `docker build -t app .`
4. Run containers: `docker-compose -f docker-compose.prod.yml up -d`
5. Set up reverse proxy (nginx)
6. Configure SSL/TLS

---

## Troubleshooting

### Why is my agent not responding?

**A:** Check:
1. Is the agent running? Check agent status in dashboard
2. Are there errors in the logs?
3. Is the agent properly configured?
4. Does the agent have required dependencies?

---

### Why am I getting authentication errors?

**A:** Common causes:
1. Token expired: Refresh your token
2. Invalid credentials: Check username/password
3. Secret key mismatch: Verify JWT_SECRET environment variable

---

### Why is the dashboard slow?

**A:** Performance issues could be due to:
1. Too many active agents: Consider scaling
2. Database needs optimization: Add indexes
3. High latency: Check network connection
4. Resource constraints: Monitor CPU/Memory usage

---

### How do I reset the system?

**A:**
```bash
# Stop the application
# Remove database files
rm -f *.db

# Clear cache
rm -rf .cache

# Reinitialize
python3 scripts/init_db.py

# Restart the application
```

**Warning:** This will delete all data!

---

## Feature Requests

### Can I request a new feature?

**A:** Yes! Please create an issue on GitHub with a detailed description of the feature you'd like to see. We welcome contributions.

### How do I contribute code?

**A:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [Contributing Guide](/docs/dev_guide/dev-coding) for more details.

---

## Support

### Where can I get help?

**A:**
- [Documentation](/docs)
- [GitHub Issues](https://github.com/YunosukeYoshino/openclaw-workspace/issues)
- [Discord Community](https://discord.gg/clawd)

### How do I report a bug?

**A:** Create a GitHub issue with:
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs
