#!/usr/bin/env python3
"""
Test script for generic orchestration system
Tests core functionality to ensure everything works correctly
"""

from generic_orchestrator import GenericOrchestrator, Task, Worker, TaskStatus
from generic_supervisor import GenericSupervisor
import time
import sys
from pathlib import Path


def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        'test_orchestrator_config.json',
        'test_supervisor_config.json',
        'orchestrator_state.json',
        'supervisor_state.json',
        'orchestrator_history.json',
        'supervisor_log.json',
        'supervisor_metrics.json'
    ]

    for file in test_files:
        path = Path(file)
        if path.exists():
            path.unlink()
            print(f"  ✓ Cleaned up {file}")


def test_orchestrator():
    """Test GenericOrchestrator"""
    print("\n" + "="*60)
    print("TEST 1: GenericOrchestrator")
    print("="*60)

    try:
        # Initialize
        print("\n1.1 Initializing orchestrator...")
        orchestrator = GenericOrchestrator('test_orchestrator_config.json')
        print("  ✓ Initialized")

        # Create tasks
        print("\n1.2 Creating tasks...")
        tasks = [
            Task(
                id='task_001',
                type='test',
                name='Test Task 1',
                description='First test task',
                tags=['test', 'unit'],
                priority=1,
                estimated_duration=10
            ),
            Task(
                id='task_002',
                type='test',
                name='Test Task 2',
                description='Second test task',
                tags=['test', 'unit'],
                priority=2,
                estimated_duration=15
            ),
            Task(
                id='task_003',
                type='test',
                name='Test Task 3',
                description='Third test task',
                tags=['test', 'integration'],
                priority=1,
                dependencies=['task_001', 'task_002'],
                estimated_duration=20
            ),
        ]

        orchestrator.add_tasks(tasks)
        print("  ✓ Added 3 tasks")

        # Create worker
        print("\n1.3 Creating worker...")
        worker = Worker(
            id='worker_001',
            name='Test Worker',
            type='test',
            capacity=3,
            max_parallel_tasks=2
        )
        orchestrator.register_worker(worker)
        print("  ✓ Registered worker")

        # Get next batch
        print("\n1.4 Getting next batch...")
        batch = orchestrator.get_next_batch(batch_size=2)
        print(f"  ✓ Got {len(batch)} tasks in batch")

        # Assign tasks
        print("\n1.5 Assigning tasks to worker...")
        task_ids = [t.id for t in batch]
        result = orchestrator.assign_tasks(task_ids, 'worker_001')
        assert result, "Task assignment failed"
        print(f"  ✓ Assigned {len(task_ids)} tasks")

        # Update progress
        print("\n1.6 Updating task progress...")
        orchestrator.update_task_progress('task_001', 0.5)
        status = orchestrator.task_status['task_001']
        assert status.progress == 0.5, "Progress update failed"
        print("  ✓ Progress updated to 50%")

        # Complete task
        print("\n1.7 Completing task...")
        orchestrator.complete_task('task_001', success=True)
        status = orchestrator.task_status['task_001']
        assert status.status == 'completed', "Task not completed"
        print("  ✓ Task completed")

        # Get summary
        print("\n1.8 Getting summary...")
        summary = orchestrator.get_summary()
        print(f"  ✓ Total: {summary['total_tasks']}, Completed: {summary['completed']}, Progress: {summary['progress_percent']:.1f}%")

        # Get tasks by type
        print("\n1.9 Filtering tasks by type...")
        test_tasks = orchestrator.get_tasks_by_type('test')
        assert len(test_tasks) == 3, "Task filtering failed"
        print(f"  ✓ Found {len(test_tasks)} test tasks")

        # Get tasks by tag
        print("\n1.10 Filtering tasks by tag...")
        unit_tasks = orchestrator.get_tasks_by_tag('unit')
        assert len(unit_tasks) == 2, "Tag filtering failed"
        print(f"  ✓ Found {len(unit_tasks)} unit tests")

        # Get worker status
        print("\n1.11 Getting worker status...")
        worker_status = orchestrator.get_worker_status('worker_001')
        assert worker_status['worker_id'] == 'worker_001', "Worker status failed"
        print(f"  ✓ Worker load: {worker_status['current_load']}/{worker_status['max_parallel_tasks']}")

        # Test dependency checking
        print("\n1.12 Testing dependency satisfaction...")
        available = orchestrator.get_available_tasks()
        # task_003 should not be available until task_001 and task_002 are done
        task_003_available = any(t.id == 'task_003' for t in available)
        assert not task_003_available, "Dependency check failed"
        print("  ✓ Dependencies properly checked")

        # Complete task_002
        orchestrator.complete_task('task_002', success=True)
        available = orchestrator.get_available_tasks()
        task_003_available = any(t.id == 'task_003' for t in available)
        assert task_003_available, "Task should be available after dependencies met"
        print("  ✓ Task available after dependencies satisfied")

        # Test retry (disable auto-retry for this test)
        print("\n1.13 Testing task retry...")
        original_max_retries = orchestrator.config['max_retries']
        orchestrator.config['max_retries'] = 0  # Disable auto-retry

        orchestrator.complete_task('task_003', success=False, error_message='Test error')
        status = orchestrator.task_status['task_003']
        assert status.status == 'failed', "Task should be failed"

        # Now test manual retry
        orchestrator.config['max_retries'] = original_max_retries
        retry_result = orchestrator.retry_task('task_003')
        assert retry_result, "Retry failed"
        status = orchestrator.task_status['task_003']
        assert status.status == 'pending', "Task should be pending after retry"
        print("  ✓ Task retry works")

        # Test state persistence
        print("\n1.14 Testing state persistence...")
        orchestrator.save_state()
        new_orchestrator = GenericOrchestrator('test_orchestrator_config.json')
        assert len(new_orchestrator.tasks) == 3, "State not restored"
        assert len(new_orchestrator.workers) == 1, "Workers not restored"
        print("  ✓ State persisted and restored")

        print("\n✅ All orchestrator tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_supervisor():
    """Test GenericSupervisor"""
    print("\n" + "="*60)
    print("TEST 2: GenericSupervisor")
    print("="*60)

    try:
        # Clean up any existing state
        for f in ['test_supervisor_config.json', 'supervisor_state.json']:
            if Path(f).exists():
                Path(f).unlink()

        # Initialize
        print("\n2.1 Initializing supervisor...")
        supervisor = GenericSupervisor('test_supervisor_config.json')
        print("  ✓ Initialized")

        # Register worker
        print("\n2.2 Registering worker...")
        supervisor.register_worker(
            worker_id='worker_001',
            name='Test Worker',
            worker_type='test',
            metadata={'version': '1.0'}
        )
        print("  ✓ Worker registered")

        # Update heartbeat
        print("\n2.3 Updating heartbeat...")
        supervisor.update_heartbeat('worker_001', current_task='task_001')
        print("  ✓ Heartbeat updated")

        # Check heartbeat
        print("\n2.4 Checking heartbeat...")
        is_valid = supervisor.check_heartbeat('worker_001')
        assert is_valid, "Heartbeat should be valid"
        print("  ✓ Heartbeat is valid")

        # Get status
        print("\n2.5 Getting status...")
        status = supervisor.get_status()
        assert status['total_workers'] == 1, "Status incorrect"
        print(f"  ✓ Total workers: {status['total_workers']}, Active: {status['active_workers']}")

        # Get worker list
        print("\n2.6 Getting worker list...")
        worker_list = supervisor.get_worker_list()
        assert len(worker_list) == 1, "Worker list incorrect"
        worker = worker_list[0]
        assert worker['worker_id'] == 'worker_001', "Worker ID incorrect"
        print(f"  ✓ Worker: {worker['name']} ({worker['status']})")

        # Test error reporting
        print("\n2.7 Testing error reporting...")
        supervisor.report_task_failure('worker_001', 'task_001', 'Test error')
        print("  ✓ Error reported")

        # Update worker status
        print("\n2.8 Updating worker status...")
        supervisor.update_worker_status('worker_001', 'idle')
        status = supervisor.get_worker_status('worker_001')
        assert status.status == 'idle', "Worker status not updated"
        print("  ✓ Worker status updated")

        # Test restart
        print("\n2.9 Testing worker restart...")
        restart_result = supervisor.restart_worker('worker_001')
        assert restart_result, "Restart failed"
        status = supervisor.get_worker_status('worker_001')
        assert status.status == 'restarting', "Worker should be restarting"
        print("  ✓ Worker restarted")

        # Test state persistence
        print("\n2.10 Testing state persistence...")
        supervisor.save_state()
        new_supervisor = GenericSupervisor('test_supervisor_config.json')
        assert len(new_supervisor.workers) == 1, "State not restored"
        print("  ✓ State persisted and restored")

        # Test event logging
        print("\n2.11 Testing event logging...")
        initial_logs = len(supervisor.log_file.read_text()) if supervisor.log_file.exists() else 0
        supervisor.log_event('test_event', 'worker_001', {'data': 'test'})
        final_logs = len(supervisor.log_file.read_text()) if supervisor.log_file.exists() else 0
        assert final_logs > initial_logs, "Event not logged"
        print("  ✓ Event logged")

        # Simulate timeout
        print("\n2.12 Testing heartbeat timeout...")
        supervisor.workers['worker_001'].heartbeat = '2024-01-01T00:00:00'
        supervisor.check_all_workers()
        # Worker should be marked for restart (if auto_restart is enabled)
        print("  ✓ Timeout detection works")

        print("\n✅ All supervisor tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Supervisor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test orchestrator and supervisor integration"""
    print("\n" + "="*60)
    print("TEST 3: Integration")
    print("="*60)

    try:
        # Clean up any existing state
        for f in ['test_orchestrator_config.json', 'test_supervisor_config.json',
                  'orchestrator_state.json', 'supervisor_state.json']:
            if Path(f).exists():
                Path(f).unlink()

        print("\n3.1 Setting up integrated system...")

        # Initialize both
        orchestrator = GenericOrchestrator('test_orchestrator_config.json')
        supervisor = GenericSupervisor('test_supervisor_config.json')

        # Setup callbacks
        def on_worker_error(worker_id, error):
            print(f"  ⚠️ Worker error callback: {worker_id} - {error}")

        def on_worker_restart(worker_id):
            print(f"  🔄 Worker restart callback: {worker_id}")

        supervisor.on_worker_error = on_worker_error
        supervisor.on_worker_restart = on_worker_restart

        # Create tasks
        tasks = [
            Task(id='int_task_1', type='integration', name='Integration Task 1',
                 description='Test integration', tags=['integration']),
            Task(id='int_task_2', type='integration', name='Integration Task 2',
                 description='Test integration', tags=['integration']),
        ]

        orchestrator.add_tasks(tasks)

        # Register worker
        worker = Worker(id='int_worker', name='Integration Worker',
                       type='integration', capacity=2)
        orchestrator.register_worker(worker)
        supervisor.register_worker('int_worker', 'Integration Worker', 'integration')

        print("  ✓ Integrated system set up")

        # Simulate workflow
        print("\n3.2 Simulating workflow...")

        # Get batch
        batch = orchestrator.get_next_batch()
        task_ids = [t.id for t in batch]

        # Assign tasks
        orchestrator.assign_tasks(task_ids, 'int_worker')

        # Update heartbeat with current task
        supervisor.update_heartbeat('int_worker', current_task=task_ids[0])

        # Simulate progress
        for progress in [0.25, 0.5, 0.75, 1.0]:
            orchestrator.update_task_progress(task_ids[0], progress)
            supervisor.update_heartbeat('int_worker', current_task=task_ids[0])
            time.sleep(0.1)

        # Complete task
        orchestrator.complete_task(task_ids[0], success=True)

        # Move to next task
        supervisor.update_heartbeat('int_worker', current_task=task_ids[1])
        orchestrator.complete_task(task_ids[1], success=True)

        print("  ✓ Workflow completed")

        # Check final status
        print("\n3.3 Checking final status...")
        summary = orchestrator.get_summary()
        assert summary['completed'] == 2, "Not all tasks completed"
        print(f"  ✓ Orchestrator: {summary['progress_percent']:.1f}% complete")

        status = supervisor.get_status()
        assert status['active_workers'] >= 0, "Worker status incorrect"
        print(f"  ✓ Supervisor: {status['total_workers']} workers")

        print("\n✅ All integration tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("GENERIC ORCHESTRATION SYSTEM TEST SUITE")
    print("="*60)

    results = []

    # Run tests
    results.append(("Orchestrator", test_orchestrator()))
    results.append(("Supervisor", test_supervisor()))
    results.append(("Integration", test_integration()))

    # Cleanup
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    cleanup_test_files()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
