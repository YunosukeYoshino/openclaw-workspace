#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Workflow Engine - Agent workflow management"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Step:
    id: str
    name: str
    action: Callable
    depends_on: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None

    async def execute(self, context: Dict[str, Any]):
        self.status = StepStatus.RUNNING
        try:
            if asyncio.iscoroutinefunction(self.action):
                self.result = await self.action(context)
            else:
                self.result = self.action(context)
            self.status = StepStatus.COMPLETED
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error = str(e)
            raise

@dataclass
class Workflow:
    id: str
    name: str
    description: str
    steps: Dict[str, Step] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.CREATED
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def add_step(self, step: Step):
        self.steps[step.id] = step

    def get_ready_steps(self) -> List[Step]:
        ready = []
        for step in self.steps.values():
            if step.status == StepStatus.PENDING:
                dependencies_completed = all(
                    self.steps[dep_id].status == StepStatus.COMPLETED
                    for dep_id in step.depends_on
                    if dep_id in self.steps
                )
                if dependencies_completed:
                    ready.append(step)
        return ready

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}

    def create_workflow(self, name: str, description: str) -> str:
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description
        )
        self.workflows[workflow_id] = workflow
        return workflow_id

    def add_step(self, workflow_id: str, step: Step):
        if workflow_id in self.workflows:
            self.workflows[workflow_id].add_step(step)

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING

        try:
            while True:
                ready_steps = workflow.get_ready_steps()
                if not ready_steps:
                    break

                tasks = [step.execute(workflow.context) for step in ready_steps]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        workflow.status = WorkflowStatus.FAILED
                        raise result

                if all(s.status in [StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED]
                       for s in workflow.steps.values()):
                    break

            if all(s.status == StepStatus.COMPLETED for s in workflow.steps.values()):
                workflow.status = WorkflowStatus.COMPLETED
            else:
                workflow.status = WorkflowStatus.FAILED

            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "results": {sid: s.result for sid, s in workflow.steps.items()}
            }

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "error": str(e)
            }

workflow_engine = WorkflowEngine()

async def main():
    async def step1(context):
        print("Step 1: Collecting data...")
        await asyncio.sleep(0.1)
        context["data"] = [1, 2, 3]
        return len(context["data"])

    async def step2(context):
        print("Step 2: Processing data...")
        await asyncio.sleep(0.1)
        context["processed"] = sum(context["data"])
        return context["processed"]

    wf_id = workflow_engine.create_workflow("Test Workflow", "Test")

    workflow_engine.add_step(wf_id, Step(
        id="step1",
        name="Data Collection",
        action=step1
    ))

    workflow_engine.add_step(wf_id, Step(
        id="step2",
        name="Data Processing",
        action=step2,
        depends_on=["step1"]
    ))

    result = await workflow_engine.execute_workflow(wf_id)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
