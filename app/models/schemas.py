from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentProfile(BaseModel):
    id: str = Field(..., description="Unique agent identifier (e.g. Arch-01)")
    name: str = Field(..., description="Agent display name")
    role: str = Field(..., description="Agent role and responsibility")
    color: str = Field("#00687a", description="Hex color badge representation")
    capabilities: List[str] = Field(default_factory=list, description="Supported agent tools/capabilities")
    status: str = Field("ready", description="Current agent status: ready, busy, offline")

class ModuleInfo(BaseModel):
    id: str = Field(..., description="Module key id")
    name: str = Field(..., description="Module display title")
    path: str = Field(..., description="Relative HTML template path")
    icon: str = Field("dashboard", description="Material Symbols icon name")
    desc: str = Field("", description="Module description")
    category: str = Field("core", description="Module category grouping")

class HealthStatus(BaseModel):
    status: str = "healthy"
    service: str = "CortxOS Multi-Agent Studio"
    version: str = "2.4.0"
    port: int = 8899
    active_ws_clients: int = 0
    agents: Dict[str, Dict[str, Any]]
    modules_count: int = 10
    execution_engine: str = "dynamic_hybrid"
    timestamp: int

class TaskDispatchRequest(BaseModel):
    agent: str = Field("Arch-01", description="Target agent id")
    prompt: str = Field(..., min_length=1, description="Task instruction prompt")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Execution context & parameters")
    runner: Optional[str] = Field("auto", description="Execution runner engine: auto, ollama, mock, openai, anthropic")

class ExecutionResult(BaseModel):
    source: str = Field(..., description="Execution provider source (e.g. ollama, mock, openai, anthropic)")
    model: str = Field(..., description="Model name or simulator ID")
    response: str = Field(..., description="Generated text output or plan")
    latency_ms: float = Field(..., description="Latency in milliseconds")
    status: str = Field("success", description="Status string: success or error")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional telemetry/trace metadata")

class TaskDispatchResponse(BaseModel):
    status: str = "dispatched"
    agent: str
    result: ExecutionResult
    timestamp: int

class TelemetryPayload(BaseModel):
    type: str = "telemetry"
    fps: int
    latency_ms: int
    tokens: int
    cost: float
    active_threads: int = 4
    subprocesses_healthy: int = 12
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    ram_used_mb: float = 0.0
    disk_percent: float = 0.0
    total_tasks: int = 0
    timestamp: int

class StreamMessage(BaseModel):
    type: str = "agent_stream"
    agent: str
    status: str = Field(..., description="thinking, working, completed, error")
    output: str
    source: Optional[str] = None
    model: Optional[str] = None
    timestamp: int
