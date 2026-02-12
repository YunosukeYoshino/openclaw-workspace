#!/usr/bin/env python3
"""
Generic Task Orchestrator
- Manages batch processing of tasks
- Tracks overall progress
- Dynamically adjusts batch sizes
- Supports task dependencies
- Provides progress visualization
- Generic and reusable across projects
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Any, Callable
from dataclasses import dataclass, asdict
import heapq


@dataclass
class Task:
    """Generic task definition"""
    id: str
    type: str
    name: str
    description: str
    tags: List[str] = None
    dependencies: List[str] = None
    priority: int = 0
    metadata: Dict[str, Any] = None
    estimated_duration: int = 60  # in seconds

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Worker:
    """Generic worker/processor definition"""
    id: str
    name: str
    type: str
    capacity: int = 1
    max_parallel_tasks: int = 1
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TaskStatus:
    """Task execution status"""
    task_id: str
    status: str  # pending, running, completed, failed, cancelled
    worker_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    progress: float = 0.0  # 0.0 to 1.0


class GenericOrchestrator:
    """Generic task orchestrator"""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the orchestrator

        Args:
            config_file: Path to configuration file (optional)
        """
        self.tasks: Dict[str, Task] = {}
        self.workers: Dict[str, Worker] = {}
        self.task_status: Dict[str, TaskStatus] = {}
        self.worker_tasks: Dict[str, Set[str]] = {}

        # Configuration
        self.config_file = config_file or Path(__file__).parent / "orchestrator_config.json"
        self.state_file = Path(self.config_file).parent / "orchestrator_state.json"
        self.history_file = Path(self.config_file).parent / "orchestrator_history.json"

        self.config = {
            'default_batch_size': 5,
            'min_batch_size': 1,
            'max_batch_size': 20,
            'auto_adjust_batch_size': True,
            'max_retries': 3,
            'heartbeat_timeout': 600,  # 10 minutes
            'progress_update_interval': 30,  # seconds
        }

        self.load_config()
        self.load_state()

    def load_config(self):
        """Load configuration from file"""
        if Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)

                # Restore tasks
                for task_data in state.get('tasks', []):
                    task = Task(**task_data)
                    self.tasks[task.id] = task

                # Restore workers
                for worker_data in state.get('workers', []):
                    worker = Worker(**worker_data)
                    self.workers[worker.id] = worker

                # Restore task status
                for status_data in state.get('task_status', []):
                    status = TaskStatus(**status_data)
                    self.task_status[status.task_id] = status

                # Restore worker tasks mapping
                self.worker_tasks = state.get('worker_tasks', {})

    def save_state(self):
        """Save state to file"""
        state = {
            'last_updated': datetime.now().isoformat(),
            'tasks': [asdict(t) for t in self.tasks.values()],
            'workers': [asdict(w) for w in self.workers.values()],
            'task_status': [asdict(s) for s in self.task_status.values()],
            'worker_tasks': {k: list(v) for k, v in self.worker_tasks.items()},
            'config': self.config
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def add_task(self, task: Task):
        """Add a task to the orchestrator"""
        self.tasks[task.id] = task
        self.task_status[task.id] = TaskStatus(task_id=task.id, status='pending')
        self.save_state()

    def add_tasks(self, tasks: List[Task]):
        """Add multiple tasks"""
        for task in tasks:
            self.add_task(task)

    def remove_task(self, task_id: str):
        """Remove a task"""
        if task_id in self.tasks:
            # Cancel if running
            status = self.task_status.get(task_id)
            if status and status.status == 'running':
                self.cancel_task(task_id)

            del self.tasks[task_id]
            del self.task_status[task_id]
            self.save_state()

    def register_worker(self, worker: Worker):
        """Register a worker"""
        self.workers[worker.id] = worker
        self.worker_tasks[worker.id] = set()
        self.save_state()

    def get_available_tasks(self) -> List[Task]:
        """Get tasks that are ready to be processed (dependencies satisfied)"""
        available = []

        for task_id, status in self.task_status.items():
            if status.status != 'pending':
                continue

            task = self.tasks[task_id]

            # Check dependencies
            dependencies_met = all(
                self.task_status.get(dep_id, TaskStatus(task_id=dep_id, status='failed')).status == 'completed'
                for dep_id in task.dependencies
            )

            if dependencies_met:
                available.append(task)

        # Sort by priority (higher first)
        available.sort(key=lambda t: t.priority, reverse=True)
        return available

    def get_next_batch(self, batch_size: Optional[int] = None) -> List[Task]:
        """
        Get next batch of tasks to process

        Args:
            batch_size: Override default batch size (optional)

        Returns:
            List of tasks ready for processing
        """
        if batch_size is None:
            batch_size = self.config['default_batch_size']

        # Auto-adjust batch size based on worker capacity
        if self.config.get('auto_adjust_batch_size', False):
            total_capacity = sum(w.capacity for w in self.workers.values())
            batch_size = max(self.config['min_batch_size'],
                           min(batch_size, total_capacity, self.config['max_batch_size']))

        available = self.get_available_tasks()
        return available[:batch_size]

    def assign_tasks(self, task_ids: List[str], worker_id: str) -> bool:
        """
        Assign tasks to a worker

        Args:
            task_ids: List of task IDs to assign
            worker_id: Worker ID to assign to

        Returns:
            True if successful
        """
        if worker_id not in self.workers:
            return False

        worker = self.workers[worker_id]
        current_load = len(self.worker_tasks.get(worker_id, []))

        if current_load + len(task_ids) > worker.max_parallel_tasks:
            return False

        for task_id in task_ids:
            if task_id not in self.tasks:
                continue

            status = self.task_status[task_id]
            if status.status != 'pending':
                continue

            status.status = 'running'
            status.worker_id = worker_id
            status.started_at = datetime.now().isoformat()

            self.worker_tasks[worker_id].add(task_id)

        self.save_state()
        return True

    def update_task_progress(self, task_id: str, progress: float):
        """Update task progress (0.0 to 1.0)"""
        if task_id in self.task_status:
            status = self.task_status[task_id]
            status.progress = max(0.0, min(1.0, progress))
            self.save_state()

    def complete_task(self, task_id: str, success: bool = True, error_message: str = None):
        """Mark a task as completed or failed"""
        if task_id not in self.task_status:
            return

        status = self.task_status[task_id]

        if success:
            status.status = 'completed'
            status.completed_at = datetime.now().isoformat()
            status.progress = 1.0
        else:
            status.status = 'failed'
            status.error_message = error_message
            status.completed_at = datetime.now().isoformat()

            # Auto-retry if configured
            if status.retry_count < self.config.get('max_retries', 3):
                self.retry_task(task_id)

        # Remove from worker's task list
        if status.worker_id and status.worker_id in self.worker_tasks:
            self.worker_tasks[status.worker_id].discard(task_id)

        self.save_state()
        self.log_history(task_id, 'completed' if success else 'failed', error_message)

    def retry_task(self, task_id: str) -> bool:
        """Retry a failed task"""
        if task_id not in self.task_status:
            return False

        status = self.task_status[task_id]

        if status.retry_count >= self.config.get('max_retries', 3):
            return False

        status.status = 'pending'
        status.retry_count += 1
        status.worker_id = None
        status.started_at = None
        status.progress = 0.0
        status.error_message = None

        self.save_state()
        return True

    def cancel_task(self, task_id: str):
        """Cancel a task"""
        if task_id in self.task_status:
            status = self.task_status[task_id]
            status.status = 'cancelled'
            status.completed_at = datetime.now().isoformat()

            if status.worker_id and status.worker_id in self.worker_tasks:
                self.worker_tasks[status.worker_id].discard(task_id)

            self.save_state()
            self.log_history(task_id, 'cancelled')

    def get_summary(self) -> Dict:
        """Get overall summary"""
        total = len(self.tasks)
        completed = sum(1 for s in self.task_status.values() if s.status == 'completed')
        running = sum(1 for s in self.task_status.values() if s.status == 'running')
        failed = sum(1 for s in self.task_status.values() if s.status == 'failed')
        pending = sum(1 for s in self.task_status.values() if s.status == 'pending')

        return {
            'total_tasks': total,
            'completed': completed,
            'running': running,
            'failed': failed,
            'pending': pending,
            'progress_percent': (completed / total * 100) if total > 0 else 0,
            'total_workers': len(self.workers),
            'active_workers': sum(1 for t in self.worker_tasks.values() if len(t) > 0)
        }

    def get_tasks_by_type(self, task_type: str) -> List[Task]:
        """Get tasks filtered by type"""
        return [t for t in self.tasks.values() if t.type == task_type]

    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get tasks filtered by tag"""
        return [t for t in self.tasks.values() if tag in t.tags]

    def get_worker_status(self, worker_id: str) -> Dict:
        """Get worker status"""
        if worker_id not in self.workers:
            return {}

        worker = self.workers[worker_id]
        task_ids = self.worker_tasks.get(worker_id, set())

        return {
            'worker_id': worker.id,
            'name': worker.name,
            'type': worker.type,
            'capacity': worker.capacity,
            'current_load': len(task_ids),
            'task_ids': list(task_ids),
            'max_parallel_tasks': worker.max_parallel_tasks
        }

    def log_history(self, task_id: str, event: str, data: Any = None):
        """Log event to history"""
        history = []

        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)

        history.append({
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'event': event,
            'data': data
        })

        # Keep last 1000 entries
        if len(history) > 1000:
            history = history[-1000:]

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def display_status(self):
        """Display current status"""
        summary = self.get_summary()

        print("\n" + "="*50)
        print("📊 ORCHESTRATOR STATUS")
        print("="*50)
        print(f"\nTasks:")
        print(f"  Total:     {summary['total_tasks']}")
        print(f"  Completed: {summary['completed']} ✅")
        print(f"  Running:   {summary['running']} 🔄")
        print(f"  Failed:    {summary['failed']} ❌")
        print(f"  Pending:   {summary['pending']} ⏳")
        print(f"  Progress:  {summary['progress_percent']:.1f}%")

        print(f"\nWorkers:")
        print(f"  Total:     {summary['total_workers']}")
        print(f"  Active:    {summary['active_workers']}")

        # Show worker details
        if self.workers:
            print(f"\nWorker Details:")
            for worker_id in self.workers:
                status = self.get_worker_status(worker_id)
                print(f"  [{status['type']}] {status['name']}: {status['current_load']}/{status['max_parallel_tasks']} tasks")

        print("="*50)

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get task dependency graph"""
        graph = {}
        for task_id, task in self.tasks.items():
            graph[task_id] = task.dependencies
        return graph

    def get_critical_path(self) -> List[str]:
        """Get critical path (longest chain of dependent tasks)"""
        def get_chain_length(task_id: str, visited: Set[str]) -> int:
            if task_id in visited:
                return 0

            visited.add(task_id)

            if task_id not in self.tasks:
                return 0

            task = self.tasks[task_id]
            if not task.dependencies:
                return 1

            max_len = 0
            for dep_id in task.dependencies:
                max_len = max(max_len, get_chain_length(dep_id, visited.copy()))

            return max_len + 1

        max_length = 0
        start_task = None

        for task_id in self.tasks:
            length = get_chain_length(task_id, set())
            if length > max_length:
                max_length = length
                start_task = task_id

        return [start_task] if start_task else []


if __name__ == '__main__':
    # Example usage
    orchestrator = GenericOrchestrator()

    # Add some example tasks
    tasks = [
        Task(id='task1', type='data', name='Load data', description='Load initial dataset', priority=1),
        Task(id='task2', type='process', name='Process data', description='Process the loaded data',
             dependencies=['task1'], priority=2),
        Task(id='task3', type='process', name='Transform data', description='Transform processed data',
             dependencies=['task2'], priority=2),
        Task(id='task4', type='output', name='Save results', description='Save final results',
             dependencies=['task3'], priority=3),
    ]

    orchestrator.add_tasks(tasks)

    # Register a worker
    worker = Worker(id='worker1', name='Processing Worker', type='default', capacity=5)
    orchestrator.register_worker(worker)

    # Display status
    orchestrator.display_status()

    # Get next batch
    next_batch = orchestrator.get_next_batch()
    if next_batch:
        print(f"\nNext batch ({len(next_batch)} tasks):")
        for task in next_batch:
            print(f"  - [{task.type}] {task.name}: {task.description}")
