# Rate Limiting

## Token Bucket Algorithm

```python
from collections import deque

class RateLimiter:
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = deque()

    def is_allowed(self):
        now = time.time()
        while self.requests and self.requests[0] <= now - self.window:
            self.requests.popleft()
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
```