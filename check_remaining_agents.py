#!/usr/bin/env python3
import os

agents_dir = "agents"
existing_agents = set(os.listdir(agents_dir))
existing_agents.discard("DEVELOPMENT_REPORT.md")
existing_agents.discard("dev-progress.json")

pending_agents = [
    "household-agent",
    "garden-agent",
    "car-agent",
    "insurance-agent",
    "tax-agent",
    "device-agent",
    "software-agent",
    "network-agent",
    "security-agent",
    "cloud-agent",
    "phone-agent",
    "message-agent",
    "calendar-integration-agent",
    "webhook-agent",
    "report-agent",
    "log-agent",
    "debug-agent",
    "test-agent",
    "deploy-agent",
    "monitor-agent",
    "performance-agent",
    "scale-agent",
    "backup-schedule-agent",
    "cleanup-agent",
    "archive-agent",
]

remaining = [a for a in pending_agents if a not in existing_agents]

print(f"既存エージェント数: {len(existing_agents)}")
print(f"未作成エージェント数: {len(remaining)}")
print(f"\n未作成エージェント:")
for a in remaining:
    print(f"  - {a}")
