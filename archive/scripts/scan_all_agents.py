#!/usr/bin/env python3
import os

agents_dir = "agents"
existing_agents = sorted(os.listdir(agents_dir))
existing_agents = [a for a in existing_agents if os.path.isdir(os.path.join(agents_dir, a))]

print(f"全エージェント ({len(existing_agents)}個):")
for i, a in enumerate(existing_agents, 1):
    print(f"{i:3d}. {a}")
