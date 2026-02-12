#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agent Discovery - Dynamic agent detection system"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AgentInfo:
    id: str
    name: str
    type: str
    status: str
    capabilities: List[str]
    endpoint: Optional[str] = None
    last_seen: Optional[datetime] = None
    metadata: Dict = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "capabilities": self.capabilities,
            "endpoint": self.endpoint,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "metadata": self.metadata or {}
        }

class AgentDiscovery:
    def __init__(self, workspace="/workspace/agents"):
        self.workspace = workspace
        self.agents: Dict[str, AgentInfo] = {}
        self.load_agents()

    def load_agents(self):
        if not os.path.exists(self.workspace):
            return

        for agent_dir in os.listdir(self.workspace):
            agent_path = os.path.join(self.workspace, agent_dir)
            if os.path.isdir(agent_path):
                agent_info = self._load_agent_info(agent_path, agent_dir)
                if agent_info:
                    self.agents[agent_info.id] = agent_info

    def _load_agent_info(self, agent_path: str, agent_name: str) -> Optional[AgentInfo]:
        readme_path = os.path.join(agent_path, "README.md")
        if not os.path.exists(readme_path):
            return None

        with open(readme_path, "r") as f:
            readme = f.read()

        capabilities = []
        if "管理" in readme:
            capabilities.append("management")
        if "記録" in readme:
            capabilities.append("recording")
        if "通知" in readme:
            capabilities.append("notification")

        return AgentInfo(
            id=agent_name,
            name=agent_name.replace("-", " ").title(),
            type=self._infer_agent_type(readme),
            status="stopped",
            capabilities=capabilities,
            endpoint=None,
            last_seen=None,
            metadata={"path": agent_path}
        )

    def _infer_agent_type(self, readme: str) -> str:
        if "監視" in readme or "モニタ" in readme:
            return "monitoring"
        elif "管理" in readme:
            return "management"
        elif "記録" in readme or "トラック" in readme:
            return "tracker"
        else:
            return "general"

    def register_agent(self, agent_info: AgentInfo):
        self.agents[agent_info.id] = agent_info
        print(f"[Discovery] Registered: {agent_info.name}")

    def unregister_agent(self, agent_id: str):
        if agent_id in self.agents:
            del self.agents[agent_id]
            print(f"[Discovery] Unregistered: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[AgentInfo]:
        return list(self.agents.values())

    def find_by_capability(self, capability: str) -> List[AgentInfo]:
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]

    def update_status(self, agent_id: str, status: str):
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].last_seen = datetime.now()

agent_discovery = AgentDiscovery()

def main():
    agents = agent_discovery.get_all_agents()
    print(f"Discovered agents: {len(agents)}")
    for agent in agents[:5]:
        print(f"  - {agent.name} ({agent.type}): {agent.capabilities}")

if __name__ == "__main__":
    main()
