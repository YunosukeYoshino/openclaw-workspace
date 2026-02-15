#!/usr/bin/env python3
import os
import json

agents_dir = "agents"
existing_agents = set(os.listdir(agents_dir))
existing_agents.discard("DEVELOPMENT_REPORT.md")
existing_agents.discard("dev-progress.json")

with open("dev_progress.json") as f:
    data = json.load(f)

pending = [a for a in data['pending']]
print("Pending agents and status:")
for agent in pending:
    agent_name = agent[1]
    exists = agent_name in existing_agents
    status = "✓ exists" if exists else "✗ missing"
    print(f"  {agent[0]:3d}. {agent_name} - {status}")
