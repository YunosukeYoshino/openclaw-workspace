#!/usr/bin/env python3
"""
Example: Web Scraping Orchestration
Demonstrates using the generic orchestrator for web scraping tasks
"""

from generic_orchestrator import GenericOrchestrator, Task, Worker
from generic_supervisor import GenericSupervisor
import time


def main():
    """Run web scraping example"""

    print("\n" + "="*60)
    print("🌐 WEB SCRAPING ORCHESTRATION EXAMPLE")
    print("="*60)

    # Initialize orchestrator
    orchestrator = GenericOrchestrator('scraping_config.json')

    # Define scraping tasks for different sites
    target_sites = [
        ('news_site', 'https://news.example.com', 'news'),
        ('blog_site', 'https://blog.example.com', 'blog'),
        ('product_site', 'https://products.example.com', 'ecommerce'),
        ('forum_site', 'https://forum.example.com', 'forum'),
        ('social_site', 'https://social.example.com', 'social'),
        ('media_site', 'https://media.example.com', 'media'),
        ('docs_site', 'https://docs.example.com', 'documentation'),
        ('api_site', 'https://api.example.com', 'api'),
        ('search_site', 'https://search.example.com', 'search'),
        ('archive_site', 'https://archive.example.com', 'archive'),
    ]

    tasks = []
    for idx, (site_name, url, site_type) in enumerate(target_sites):
        tasks.append(Task(
            id=f'scrape_{site_name}',
            type='scrape',
            name=f'Scrape {site_name.replace("_", " ").title()}',
            description=f'Extract data from {url}',
            tags=[site_type, 'scraping'],
            priority=2 if site_type in ['news', 'blog'] else 1,
            metadata={'url': url, 'site_type': site_type},
            estimated_duration=30
        ))

    # Add processing tasks
    for idx in range(3):
        tasks.append(Task(
            id=f'process_batch_{idx}',
            type='process',
            name=f'Process Data Batch {idx+1}',
            description='Process and clean scraped data',
            tags=['processing', 'cleaning'],
            priority=2,
            estimated_duration=45
        ))

    # Add storage task (depends on all scraping being done)
    scrape_task_ids = [t.id for t in tasks if t.type == 'scrape']
    tasks.append(Task(
        id='store_data',
        type='store',
        name='Store to Database',
        description='Save processed data to database',
        dependencies=scrape_task_ids,
        tags=['database', 'storage'],
        priority=3,
        estimated_duration=60
    ))

    # Add tasks to orchestrator
    orchestrator.add_tasks(tasks)

    # Register workers with different capabilities
    workers = [
        Worker(
            id='scraper_worker_1',
            name='High-Speed Scraper 1',
            type='scraper',
            capacity=5,
            max_parallel_tasks=3,
            metadata={'rate_limit': 10, 'user_agent': 'scraper-bot/1'}
        ),
        Worker(
            id='scraper_worker_2',
            name='High-Speed Scraper 2',
            type='scraper',
            capacity=5,
            max_parallel_tasks=3,
            metadata={'rate_limit': 10, 'user_agent': 'scraper-bot/2'}
        ),
        Worker(
            id='processor_worker',
            name='Data Processor',
            type='processor',
            capacity=3,
            max_parallel_tasks=2,
            metadata={'memory': '2GB', 'cpu': '2 cores'}
        ),
        Worker(
            id='storage_worker',
            name='Database Writer',
            type='storage',
            capacity=2,
            max_parallel_tasks=1,
            metadata={'connection_pool': '5'}
        )
    ]

    for worker in workers:
        orchestrator.register_worker(worker)

    # Display initial status
    orchestrator.display_status()

    # Simulate scraping execution
    print("\n🚀 Starting web scraping...\n")

    completed_batches = 0
    processing_task_idx = 0

    while True:
        summary = orchestrator.get_summary()

        # Check if all tasks completed
        if summary['completed'] == summary['total_tasks']:
            print("\n✅ Scraping completed successfully!")
            break

        # Get next batch
        next_batch = orchestrator.get_next_batch()

        if next_batch:
            print(f"\n📋 Next batch ({len(next_batch)} tasks):")

            for task in next_batch:
                print(f"  - [{task.type}] {task.name}")

                # Determine appropriate worker
                if task.type == 'scrape':
                    worker_id = 'scraper_worker_1' if len(orchestrator.worker_tasks.get('scraper_worker_1', set())) < 3 else 'scraper_worker_2'
                elif task.type == 'process':
                    worker_id = 'processor_worker'
                    processing_task_idx += 1
                elif task.type == 'store':
                    worker_id = 'storage_worker'
                else:
                    worker_id = 'scraper_worker_1'

                # Try to assign task
                if orchestrator.assign_tasks([task.id], worker_id):
                    print(f"    → Assigned to {worker_id}")

                    # Simulate task execution
                    time.sleep(0.3)

                    # Mark as completed
                    orchestrator.complete_task(task.id, success=True)

                    # Show progress
                    new_summary = orchestrator.get_summary()
                    print(f"    ✅ Completed ({new_summary['progress_percent']:.1f}%)")

                    # Check if we should trigger a processing batch
                    if task.type == 'scrape':
                        completed_batches += 1
                        if completed_batches >= 4 and processing_task_idx < 3:
                            proc_task_id = f'process_batch_{processing_task_idx}'
                            if proc_task_id in orchestrator.task_status:
                                orchestrator.update_task_progress(proc_task_id, completed_batches / 10)

        time.sleep(0.5)

    # Display final status
    orchestrator.display_status()

    # Show tasks by type
    print("\n📊 Tasks by Type:")
    for task_type in ['scrape', 'process', 'store']:
        type_tasks = orchestrator.get_tasks_by_type(task_type)
        print(f"  {task_type}: {len(type_tasks)} tasks")

    # Show tasks by tag
    print("\n🏷️  Tasks by Tag:")
    for tag in ['scraping', 'processing', 'storage', 'database']:
        tag_tasks = orchestrator.get_tasks_by_tag(tag)
        if tag_tasks:
            print(f"  #{tag}: {len(tag_tasks)} tasks")


if __name__ == '__main__':
    main()
