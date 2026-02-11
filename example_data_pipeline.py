#!/usr/bin/env python3
"""
Example: Data Pipeline Orchestration
Demonstrates using the generic orchestrator for a data processing pipeline
"""

from generic_orchestrator import GenericOrchestrator, Task, Worker
from generic_supervisor import GenericSupervisor
import time


def main():
    """Run data pipeline example"""

    print("\n" + "="*60)
    print("📊 DATA PIPELINE ORCHESTRATION EXAMPLE")
    print("="*60)

    # Initialize orchestrator
    orchestrator = GenericOrchestrator('data_pipeline_config.json')

    # Define pipeline tasks
    tasks = [
        Task(
            id='extract_data',
            type='extract',
            name='Extract Data from Source',
            description='Load raw data from external source',
            tags=['ingestion', 'source-a'],
            priority=3,
            estimated_duration=120
        ),
        Task(
            id='validate_data',
            type='validate',
            name='Validate Data Schema',
            description='Check data quality and schema',
            dependencies=['extract_data'],
            tags=['quality', 'validation'],
            priority=2,
            estimated_duration=60
        ),
        Task(
            id='transform_data',
            type='transform',
            name='Transform Data',
            description='Apply transformations to data',
            dependencies=['validate_data'],
            tags=['etl', 'processing'],
            priority=2,
            estimated_duration=180
        ),
        Task(
            id='load_data',
            type='load',
            name='Load to Warehouse',
            description='Load processed data to warehouse',
            dependencies=['transform_data'],
            tags=['etl', 'warehouse'],
            priority=3,
            estimated_duration=90
        ),
        Task(
            id='generate_report',
            type='output',
            name='Generate Reports',
            description='Create analytics reports',
            dependencies=['load_data'],
            tags=['reporting', 'analytics'],
            priority=1,
            estimated_duration=120
        ),
        Task(
            id='send_notification',
            type='notify',
            name='Send Notifications',
            description='Notify stakeholders',
            dependencies=['generate_report'],
            tags=['notification', 'email'],
            priority=1,
            estimated_duration=30
        ),
    ]

    # Add tasks to orchestrator
    orchestrator.add_tasks(tasks)

    # Register workers
    workers = [
        Worker(
            id='etl_worker',
            name='ETL Processing Worker',
            type='etl',
            capacity=3,
            max_parallel_tasks=2,
            metadata={'version': '2.0', 'region': 'us-east'}
        ),
        Worker(
            id='report_worker',
            name='Report Generation Worker',
            type='reporting',
            capacity=2,
            max_parallel_tasks=1,
            metadata={'version': '1.5'}
        )
    ]

    for worker in workers:
        orchestrator.register_worker(worker)

    # Display initial status
    orchestrator.display_status()

    # Simulate pipeline execution
    print("\n🚀 Starting pipeline execution...\n")

    while True:
        summary = orchestrator.get_summary()

        # Check if all tasks completed
        if summary['completed'] == summary['total_tasks']:
            print("\n✅ Pipeline completed successfully!")
            break

        # Get next batch
        next_batch = orchestrator.get_next_batch()

        if next_batch:
            print(f"\n📋 Next batch ({len(next_batch)} tasks):")
            for task in next_batch:
                print(f"  - [{task.type}] {task.name} (Priority: {task.priority})")

                # Assign to appropriate worker
                worker_id = 'etl_worker' if task.type in ['extract', 'validate', 'transform', 'load'] else 'report_worker'

                if orchestrator.assign_tasks([task.id], worker_id):
                    print(f"    → Assigned to {worker_id}")

                    # Simulate task execution
                    time.sleep(0.5)

                    # Mark as completed
                    orchestrator.complete_task(task.id, success=True)

                    # Show progress
                    new_summary = orchestrator.get_summary()
                    print(f"    ✅ Completed ({new_summary['progress_percent']:.1f}%)")

        time.sleep(1)

    # Display final status
    orchestrator.display_status()

    # Get critical path
    critical_path = orchestrator.get_critical_path()
    if critical_path:
        print(f"\n🔗 Critical path: {' → '.join(critical_path)}")


if __name__ == '__main__':
    main()
