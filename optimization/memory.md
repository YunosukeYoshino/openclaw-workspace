# Memory Optimization

## Memory Profiling

```python
import tracemalloc

tracemalloc.start()
# ... code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
```


## Object Pooling

```python
class ObjectPool:
    def __init__(self, factory, max_size=100):
        self.factory = factory
        self.pool = []
        self.max_size = max_size

    def acquire(self):
        return self.pool.pop() if self.pool else self.factory()

    def release(self, obj):
        if len(self.pool) < self.max_size:
            self.pool.append(obj)
```