from typing import Optional, List, Dict, Any
import time
import json
from sqlmodel import SQLModel, Field, Column, JSON

class AgentDB(SQLModel, table=True):
    __tablename__ = "agents"

    id: str = Field(primary_key=True, description="Agent unique ID, e.g., Arch-01")
    name: str = Field(..., description="Display name")
    role: str = Field(..., description="Role and responsibilities")
    color: str = Field("#00687a", description="Hex badge color")
    capabilities: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = Field("ready", description="Status: ready, thinking, working, offline")
    updated_at: int = Field(default_factory=lambda: int(time.time()))

class TaskDB(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(..., index=True, description="Task string identifier")
    agent_id: str = Field(..., foreign_key="agents.id", index=True)
    prompt: str = Field(..., description="Prompt or instruction")
    status: str = Field("queued", description="Status: queued, thinking, working, completed, failed")
    runner: str = Field("auto", description="Runner choice")
    result_output: Optional[str] = Field(default="", description="Generated output or result")
    latency_ms: float = Field(default=0.0)
    created_at: int = Field(default_factory=lambda: int(time.time()))
    completed_at: Optional[int] = Field(default=None)

class DAGExecutionLogDB(SQLModel, table=True):
    __tablename__ = "dag_execution_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    mission_id: str = Field(..., index=True, description="Associated mission/task identifier")
    phase_id: str = Field(..., description="Phase identifier e.g. PHASE_01")
    phase_name: str = Field(..., description="Human readable phase name")
    agent_id: str = Field(..., description="Agent assigned to phase")
    status: str = Field("pending", description="Status: pending, active, streaming, completed, failed")
    payload_diff: Optional[str] = Field(default="", description="JSON or text payload/code diff")
    duration_s: float = Field(default=0.0)
    created_at: int = Field(default_factory=lambda: int(time.time()))

class TokenUsageHistoryDB(SQLModel, table=True):
    __tablename__ = "token_usage_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: str = Field(..., index=True)
    task_id: Optional[str] = Field(default=None, index=True)
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    estimated_cost: float = Field(default=0.0)
    timestamp: int = Field(default_factory=lambda: int(time.time()))
