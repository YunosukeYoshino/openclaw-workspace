# Caching Strategy

## Redis Caching

```python
import redis
from functools import wraps

cache = redis.Redis(host='localhost', port=6379, db=0)

def cached(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            result = cache.get(key)
            if result is None:
                result = func(*args, **kwargs)
                cache.setex(key, ttl, result)
            return result
        return wrapper
    return decorator
```

## Cache Invalidation

```python
# Invalidate on write operations
def create_agent(data):
    agent = Agent.objects.create(**data)
    cache.delete_pattern(f"agent:*")
    return agent
```