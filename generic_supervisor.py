#!/usr/bin/env python3
"""
Generic Worker Supervisor
- Monitors worker health and status
- Detects and handles errors
- Implements automatic recovery mechanisms
- Tracks resource usage (optional)
- Provides monitoring loop
- Generic and reusable across projects
"""

import json
import time
import signal
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum


class WorkerStatus(Enum):
    """Worker status enumeration"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    RESTARTING = "restarting"
    STOPPED = "stopped"
    TERMINATED = "terminated"


@dataclass
class WorkerInfo:
    """Worker information"""
    worker_id: str
    name: str
    type: str
    status: str
    heartbeat: str = None
    last_heartbeat: str = None
    restart_count: int = 0
    registered_at: str = None
    last_error: str = None
    metadata: Dict[str, Any] = None
    current_task: Optional[str] = None

    def __post_init__(self):
        now = datetime.now().isoformat()
        if self.registered_at is None:
            self.registered_at = now
        if self.last_heartbeat is None:
            self.last_heartbeat = now
        if self.heartbeat is None:
            self.heartbeat = now
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SupervisorConfig:
    """Supervisor configuration"""
    heartbeat_interval: int = 300  # seconds between heartbeats
    heartbeat_timeout: int = 600  # seconds before worker considered dead
    max_restarts: int = 3
    restart_delay: int = 5  # seconds before restart
    monitor_interval: int = 60  # seconds between monitoring checks
    log_retention_days: int = 30
    auto_restart: bool = True
    resource_monitoring: bool = False


class GenericSupervisor:
    """Generic worker supervisor"""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the supervisor

        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = config_file or Path(__file__).parent / "supervisor_config.json"
        self.state_file = Path(self.config_file).parent / "supervisor_state.json"
        self.log_file = Path(self.config_file).parent / "supervisor_log.json"
        self.metrics_file = Path(self.config_file).parent / "supervisor_metrics.json"

        self.workers: Dict[str, WorkerInfo] = {}
        self.config = SupervisorConfig()
        self.running = False
        self._stop_event = False

        # Callbacks
        self.on_worker_error: Optional[Callable[[str, str], None]] = None
        self.on_worker_restart: Optional[Callable[[str], None]] = None
        self.on_worker_timeout: Optional[Callable[[str], None]] = None
        self.on_task_failure: Optional[Callable[[str, str], None]] = None

        self.load_config()
        self.load_state()

    def load_config(self):
        """Load configuration from file"""
        if Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(asdict(self.config), f, indent=2)

    def load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)

                # Restore workers
                for worker_data in state.get('workers', []):
                    worker = WorkerInfo(**worker_data)
                    self.workers[worker.worker_id] = worker

    def save_state(self):
        """Save state to file"""
        state = {
            'last_updated': datetime.now().isoformat(),
            'workers': [asdict(w) for w in self.workers.values()]
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def register_worker(self, worker_id: str, name: str, worker_type: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Register a new worker

        Args:
            worker_id: Unique worker identifier
            name: Worker display name
            worker_type: Worker type/category
            metadata: Optional metadata dictionary

        Returns:
            True if registered successfully
        """
        if worker_id in self.workers:
            # Update existing worker
            self.workers[worker_id].name = name
            self.workers[worker_id].type = worker_type
            if metadata:
                self.workers[worker_id].metadata.update(metadata)
            return True

        self.workers[worker_id] = WorkerInfo(
            worker_id=worker_id,
            name=name,
            type=worker_type,
            status=WorkerStatus.INITIALIZING.value,
            heartbeat=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        self.save_state()
        self.log_event('worker_registered', worker_id, {'name': name, 'type': worker_type})
        print(f"✅ Worker '{name}' ({worker_id}) registered")
        return True

    def update_heartbeat(self, worker_id: str, current_task: Optional[str] = None) -> bool:
        """
        Update worker heartbeat

        Args:
            worker_id: Worker ID
            current_task: Current task ID being processed (optional)

        Returns:
            True if updated successfully
        """
        if worker_id not in self.workers:
            return False

        now = datetime.now().isoformat()
        self.workers[worker_id].heartbeat = now
        self.workers[worker_id].last_heartbeat = now

        if current_task is not None:
            self.workers[worker_id].current_task = current_task

        # Update status based on heartbeat
        if self.workers[worker_id].status == WorkerStatus.INITIALIZING.value:
            self.workers[worker_id].status = WorkerStatus.IDLE.value
        elif current_task and self.workers[worker_id].status != WorkerStatus.BUSY.value:
            self.workers[worker_id].status = WorkerStatus.BUSY.value

        self.save_state()
        return True

    def check_heartbeat(self, worker_id: str) -> bool:
        """
        Check if worker heartbeat is valid

        Args:
            worker_id: Worker ID

        Returns:
            True if heartbeat is valid (not timed out)
        """
        if worker_id not in self.workers:
            return False

        worker = self.workers[worker_id]
        if not worker.heartbeat:
            return False

        heartbeat_time = datetime.fromisoformat(worker.heartbeat)
        age_seconds = (datetime.now() - heartbeat_time).total_seconds()

        return age_seconds < self.config.heartbeat_timeout

    def get_worker_status(self, worker_id: str) -> Optional[WorkerInfo]:
        """Get worker information"""
        return self.workers.get(worker_id)

    def update_worker_status(self, worker_id: str, status: str, error_message: str = None) -> bool:
        """
        Update worker status

        Args:
            worker_id: Worker ID
            status: New status
            error_message: Optional error message

        Returns:
            True if updated successfully
        """
        if worker_id not in self.workers:
            return False

        self.workers[worker_id].status = status

        if error_message:
            self.workers[worker_id].last_error = error_message
            self.log_event('worker_error', worker_id, {'error': error_message})

        self.save_state()
        return True

    def report_task_failure(self, worker_id: str, task_id: str, error: str) -> bool:
        """
        Report a task failure

        Args:
            worker_id: Worker ID
            task_id: Task ID that failed
            error: Error message

        Returns:
            True if reported successfully
        """
        self.log_event('task_failure', worker_id, {'task_id': task_id, 'error': error})

        # Call callback if registered
        if self.on_task_failure:
            try:
                self.on_task_failure(task_id, error)
            except Exception as e:
                print(f"⚠️ Error in on_task_failure callback: {e}")

        return True

    def restart_worker(self, worker_id: str, delay: Optional[int] = None) -> bool:
        """
        Restart a worker

        Args:
            worker_id: Worker ID
            delay: Delay before restart (seconds), uses config default if None

        Returns:
            True if restart initiated successfully
        """
        if worker_id not in self.workers:
            print(f"❌ Worker '{worker_id}' not found")
            return False

        worker = self.workers[worker_id]

        # Check restart limit
        if worker.restart_count >= self.config.max_restarts:
            print(f"❌ Worker '{worker_id}' reached max restart limit ({self.config.max_restarts})")
            self.update_worker_status(worker_id, WorkerStatus.TERMINATED.value,
                                     "Max restart limit reached")
            self.log_event('worker_terminated', worker_id,
                          {'reason': 'max_restarts', 'restart_count': worker.restart_count})
            return False

        # Update status
        worker.status = WorkerStatus.RESTARTING.value
        worker.restart_count += 1

        restart_delay = delay or self.config.restart_delay

        print(f"🔄 Restarting worker '{worker_id}' (attempt {worker.restart_count}/{self.config.max_restarts})")
        print(f"   Delay: {restart_delay} seconds")

        self.log_event('worker_restarting', worker_id,
                      {'attempt': worker.restart_count, 'delay': restart_delay})

        # Call callback if registered
        if self.on_worker_restart:
            try:
                self.on_worker_restart(worker_id)
            except Exception as e:
                print(f"⚠️ Error in on_worker_restart callback: {e}")

        # Note: Actual restart logic should be implemented in subclass or via callback
        # This is a placeholder for the restart mechanism
        self.save_state()
        return True

    def stop_worker(self, worker_id: str) -> bool:
        """
        Stop a worker

        Args:
            worker_id: Worker ID

        Returns:
            True if stopped successfully
        """
        if worker_id not in self.workers:
            return False

        worker = self.workers[worker_id]
        worker.status = WorkerStatus.STOPPED.value

        self.log_event('worker_stopped', worker_id)
        self.save_state()
        return True

    def remove_worker(self, worker_id: str) -> bool:
        """Remove a worker from supervision"""
        if worker_id in self.workers:
            del self.workers[worker_id]
            self.save_state()
            self.log_event('worker_removed', worker_id)
            return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get overall supervisor status"""
        total = len(self.workers)
        idle = sum(1 for w in self.workers.values() if w.status == WorkerStatus.IDLE.value)
        busy = sum(1 for w in self.workers.values() if w.status == WorkerStatus.BUSY.value)
        error = sum(1 for w in self.workers.values() if w.status == WorkerStatus.ERROR.value)
        restarting = sum(1 for w in self.workers.values() if w.status == WorkerStatus.RESTARTING.value)
        stopped = sum(1 for w in self.workers.values() if w.status == WorkerStatus.STOPPED.value)
        terminated = sum(1 for w in self.workers.values() if w.status == WorkerStatus.TERMINATED.value)

        # Check for dead workers (timeout but not marked as dead)
        dead = 0
        for worker_id, worker in self.workers.items():
            if worker.status in [WorkerStatus.IDLE.value, WorkerStatus.BUSY.value]:
                if not self.check_heartbeat(worker_id):
                    dead += 1

        return {
            'total_workers': total,
            'idle': idle,
            'busy': busy,
            'error': error,
            'restarting': restarting,
            'stopped': stopped,
            'terminated': terminated,
            'dead_heartbeat': dead,
            'active_workers': idle + busy
        }

    def get_worker_list(self) -> List[Dict]:
        """Get list of all workers with details"""
        workers_list = []

        for worker_id, worker in self.workers.items():
            is_heartbeat_valid = self.check_heartbeat(worker_id)

            workers_list.append({
                'worker_id': worker_id,
                'name': worker.name,
                'type': worker.type,
                'status': worker.status,
                'heartbeat_valid': is_heartbeat_valid,
                'last_heartbeat': worker.last_heartbeat,
                'restart_count': worker.restart_count,
                'current_task': worker.current_task,
                'last_error': worker.last_error
            })

        return workers_list

    def monitor_loop(self, callback: Optional[Callable[[], None]] = None):
        """
        Main monitoring loop

        Args:
            callback: Optional callback function called each iteration
        """
        self.running = True
        self._stop_event = False

        print("\n👁️ Supervisor monitoring loop started...")
        print(f"   Monitor interval: {self.config.monitor_interval}s")
        print(f"   Heartbeat timeout: {self.config.heartbeat_timeout}s")
        print(f"   Auto-restart: {self.config.auto_restart}")

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            print("\n🛑 Shutdown signal received")
            self._stop_event = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        while not self._stop_event:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Get status
                status = self.get_status()

                # Display status
                print(f"\n[{timestamp}] 📊 Supervisor Status:")
                print(f"   Total: {status['total_workers']} | Active: {status['active_workers']} | "
                      f"Idle: {status['idle']} | Busy: {status['busy']}")
                if status['error'] > 0:
                    print(f"   ⚠️ Errors: {status['error']}")
                if status['restarting'] > 0:
                    print(f"   🔄 Restarting: {status['restarting']}")
                if status['dead_heartbeat'] > 0:
                    print(f"   ❌ Dead heartbeats: {status['dead_heartbeat']}")

                # Check worker heartbeats and handle errors
                self.check_all_workers()

                # Call callback if provided
                if callback:
                    try:
                        callback()
                    except Exception as e:
                        print(f"⚠️ Error in monitor callback: {e}")

            except KeyboardInterrupt:
                print("\n🛑 Keyboard interrupt received")
                break
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                self.log_event('monitor_error', 'supervisor', {'error': str(e)})

            # Wait for next iteration
            time.sleep(self.config.monitor_interval)

        self.running = False
        print("\n✅ Supervisor monitoring loop stopped")

    def check_all_workers(self):
        """Check all workers and handle issues"""
        for worker_id, worker in self.workers.items():
            # Skip workers in stopped/terminated state
            if worker.status in [WorkerStatus.STOPPED.value, WorkerStatus.TERMINATED.value]:
                continue

            # Check heartbeat
            if worker.status in [WorkerStatus.IDLE.value, WorkerStatus.BUSY.value]:
                if not self.check_heartbeat(worker_id):
                    print(f"⚠️ Worker '{worker_id}' heartbeat timeout")
                    self.log_event('heartbeat_timeout', worker_id, {
                        'last_heartbeat': worker.last_heartbeat
                    })

                    if self.on_worker_timeout:
                        try:
                            self.on_worker_timeout(worker_id)
                        except Exception as e:
                            print(f"⚠️ Error in on_worker_timeout callback: {e}")

                    if self.config.auto_restart:
                        self.restart_worker(worker_id)

            # Check for errors
            if worker.status == WorkerStatus.ERROR.value:
                print(f"⚠️ Worker '{worker_id}' is in ERROR state")

                if self.on_worker_error:
                    try:
                        self.on_worker_error(worker_id, worker.last_error or "Unknown error")
                    except Exception as e:
                        print(f"⚠️ Error in on_worker_error callback: {e}")

                if self.config.auto_restart:
                    self.restart_worker(worker_id)

    def log_event(self, event_type: str, worker_id: str, data: Dict[str, Any] = None):
        """Log an event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'worker_id': worker_id,
            'data': data or {}
        }

        logs = []

        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        # Clean old logs based on retention policy
        cutoff_date = datetime.now() - timedelta(days=self.config.log_retention_days)
        logs = [log for log in logs
                if datetime.fromisoformat(log['timestamp']) > cutoff_date]

        # Keep at most 1000 entries regardless of date
        if len(logs) > 1000:
            logs = logs[-1000:]

        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def display_status(self):
        """Display current status"""
        status = self.get_status()
        workers = self.get_worker_list()

        print("\n" + "="*50)
        print("👁️ SUPERVISOR STATUS")
        print("="*50)

        print(f"\nSummary:")
        print(f"  Total Workers:     {status['total_workers']}")
        print(f"  Idle:              {status['idle']} 🟢")
        print(f"  Busy:              {status['busy']} 🟡")
        print(f"  Error:             {status['error']} 🔴")
        print(f"  Restarting:        {status['restarting']} 🔄")
        print(f"  Stopped:           {status['stopped']} ⏸️")
        print(f"  Dead Heartbeats:   {status['dead_heartbeat']} ❌")

        if workers:
            print(f"\nWorkers:")
            for worker in workers:
                status_icon = {
                    'idle': '🟢',
                    'busy': '🟡',
                    'error': '🔴',
                    'restarting': '🔄',
                    'stopped': '⏸️',
                    'initializing': '⏳',
                    'terminated': '❌'
                }.get(worker['status'], '❓')

                heartbeat_status = "✅" if worker['heartbeat_valid'] else "❌"

                print(f"  {status_icon} [{worker['type']}] {worker['name']} ({worker['worker_id']})")
                print(f"     Status: {worker['status']} | Heartbeat: {heartbeat_status} | Restarts: {worker['restart_count']}")
                if worker['current_task']:
                    print(f"     Current Task: {worker['current_task']}")
                if worker['last_error']:
                    print(f"     Last Error: {worker['last_error']}")

        print("="*50)

    def cleanup_old_logs(self):
        """Clean old log files"""
        cutoff_date = datetime.now() - timedelta(days=self.config.log_retention_days)

        # Clean supervisor logs
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                logs = json.load(f)

            logs = [log for log in logs
                    if datetime.fromisoformat(log['timestamp']) > cutoff_date]

            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)


if __name__ == '__main__':
    # Example usage
    supervisor = GenericSupervisor()

    # Register a worker
    supervisor.register_worker(
        worker_id='worker1',
        name='Processing Worker',
        worker_type='default',
        metadata={'version': '1.0', 'owner': 'system'}
    )

    # Update heartbeat
    supervisor.update_heartbeat('worker1', current_task='task1')

    # Display status
    supervisor.display_status()

    # Simulate worker timeout (set old heartbeat)
    # supervisor.workers['worker1'].heartbeat = '2024-01-01T00:00:00'
    # supervisor.check_all_workers()

    # supervisor.display_status()
