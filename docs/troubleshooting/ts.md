# ts

deploy - デプロイ時の問題

## Troubleshooting Guide

Common issues and their solutions for the ts.

---

# ts

deploy - デプロイ時の問題

## トラブルシューティングガイド

ts に関する一般的な問題と解決策。

## Common Issues

### Application Won't Start

**Problem:** Application fails to start

**Possible Causes:**
1. Port already in use
2. Missing dependencies
3. Invalid configuration

**Solutions:**

1. **Check port availability:**
```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

2. **Install missing dependencies:**
```bash
pip install -r requirements.txt
```

3. **Validate configuration:**
```bash
python3 scripts/validate_config.py
```

---

### Database Connection Errors

**Problem:** Cannot connect to database

**Possible Causes:**
1. Database file doesn't exist
2. Incorrect database path
3. File permissions

**Solutions:**

1. **Initialize database:**
```bash
python3 scripts/init_db.py
```

2. **Check database path:**
```bash
# Check config file
cat config/database.yaml

# Verify file exists
ls -la path/to/database.db
```

3. **Fix permissions:**
```bash
chmod 644 path/to/database.db
```

---

### Authentication Failures

**Problem:** JWT authentication failing

**Possible Causes:**
1. Expired token
2. Invalid secret key
3. Token format incorrect

**Solutions:**

1. **Refresh token:**
```python
# Using refresh token
response = requests.post('/api/auth/refresh', json={
    'refresh_token': '<your-refresh-token>'
})
```

2. **Check secret key:**
```bash
# Verify JWT_SECRET is set
echo $JWT_SECRET
```

3. **Validate token:**
```bash
# Decode JWT (for debugging)
echo '<jwt-token>' | jwt decode
```

---

### Performance Issues

**Problem:** Slow response times

**Possible Causes:**
1. Unoptimized queries
2. Missing indexes
3. Memory leaks

**Solutions:**

1. **Enable query logging:**
```python
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

2. **Add indexes:**
```python
# In migration
op.create_index('idx_name', 'table', ['column'])
```

3. **Monitor memory:**
```bash
# Check memory usage
ps aux | grep python

# Profile application
python3 -m cProfile -s cumtime app.py
```

---

## Deployment Issues

### Docker Build Failures

**Problem:** Docker build fails

**Possible Causes:**
1. Base image issues
2. Missing dependencies in Dockerfile
3. Build context issues

**Solutions:**

1. **Pull latest base image:**
```bash
docker pull python:3.10-slim
```

2. **Update Dockerfile:**
```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["python", "-m", "uvicorn", "dashboard.api:app", "--host", "0.0.0.0"]
```

3. **Clean build context:**
```bash
# Create .dockerignore
echo "venv
__pycache__
*.pyc
.env" > .dockerignore
```

---

### Service Startup Failures

**Problem:** Service fails to start in production

**Possible Causes:**
1. Environment variables not set
2. Invalid configuration
3. Port conflicts

**Solutions:**

1. **Check environment variables:**
```bash
# List all environment variables
env | grep <APP_NAME>
```

2. **Validate configuration:**
```bash
python3 scripts/validate_config.py --env production
```

3. **Check service logs:**
```bash
# Systemd
journalctl -u <service-name> -f

# Docker
docker logs <container-id> -f
```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Use Python Debugger

```python
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

### Profile Application

```bash
# Memory profiling
python3 -m memory_profiler app.py

# CPU profiling
python3 -m cProfile -s cumtime app.py
```

## Getting Help

If you can't resolve your issue:

1. Check the [Documentation](/docs)
2. Search [GitHub Issues](https://github.com/YunosukeYoshino/openclaw-workspace/issues)
3. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Error messages
   - Environment details
