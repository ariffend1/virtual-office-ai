import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent.parent.parent.resolve()

class Settings(BaseModel):
    app_name: str = "CortxOS Multi-Agent Studio - Sandbox Runtime"
    app_version: str = "2.4.0"
    port: int = Field(default_factory=lambda: int(os.environ.get("CORTXOS_PORT", 8899)))
    host: str = Field(default_factory=lambda: os.environ.get("CORTXOS_HOST", "0.0.0.0"))
    debug: bool = Field(default_factory=lambda: os.environ.get("CORTXOS_DEBUG", "false").lower() == "true")
    
    # LLM Runners Configuration
    ollama_url: str = Field(default_factory=lambda: os.environ.get("OLLAMA_URL", "http://localhost:11434"))
    ollama_model: str = Field(default_factory=lambda: os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b"))
    openai_api_key: str = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.environ.get("OPENAI_MODEL", "gpt-4o"))
    anthropic_api_key: str = Field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    anthropic_model: str = Field(default_factory=lambda: os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"))
    
    # Base paths
    base_dir: Path = BASE_DIR
    static_dir: Path = BASE_DIR

settings = Settings()

DEFAULT_AGENT_PROFILES = {
    "Arch-01": {
        "id": "Arch-01",
        "name": "Arch-01 (Lead Systems Engineer)",
        "role": "System Architecture & Kernel Execution",
        "color": "#f97316",
        "capabilities": ["kernel_execution", "system_topology", "process_lifecycle"],
        "status": "ready"
    },
    "Audit-02": {
        "id": "Audit-02",
        "name": "Audit-02 (Security & Compliance)",
        "role": "Static Code Analysis & Byzantine Fault Tolerance Quorum",
        "color": "#10b981",
        "capabilities": ["bft_consensus", "ast_security_audit", "vulnerability_scan"],
        "status": "ready"
    },
    "Search-03": {
        "id": "Search-03",
        "name": "Search-03 (Deep Knowledge Researcher)",
        "role": "RAG Knowledge Graph & Semantic Vector Indexing",
        "color": "#8b5cf6",
        "capabilities": ["vector_rag", "knowledge_mesh", "cross_ref_indexing"],
        "status": "ready"
    },
    "Astra-04": {
        "id": "Astra-04",
        "name": "Astra-04 (WebGPU & Simulation Runtime)",
        "role": "Isometric Canvas, Neural Simulator & Shader Pipeline",
        "color": "#06b6d4",
        "capabilities": ["webgpu_shaders", "iso_canvas_render", "pbr_pipeline"],
        "status": "ready"
    }
}

DEFAULT_MODULES = [
    {
        "id": "studio",
        "name": "Neural Simulation Studio",
        "path": "cortxos_multi_agent_studio_neural_simulation_environment/code.html",
        "icon": "psychology",
        "desc": "3D Isometric multi-agent neural workspace",
        "category": "core"
    },
    {
        "id": "mission",
        "name": "Mission Dispatcher",
        "path": "mission_dispatcher/code.html",
        "icon": "rocket_launch",
        "desc": "Swarm mission planning & task dispatch hub",
        "category": "orchestration"
    },
    {
        "id": "telemetry",
        "name": "Live Telemetry Gateway",
        "path": "telemetry_gateway/code.html",
        "icon": "monitoring",
        "desc": "Real-time telemetry, model gateway & observability",
        "category": "monitoring"
    },
    {
        "id": "workspace_3d",
        "name": "3D Spatial Workspace",
        "path": "3d_workspace/code.html",
        "icon": "view_in_ar",
        "desc": "Spatial agent coordinates & 3D canvas",
        "category": "canvas"
    },
    {
        "id": "collaborative",
        "name": "AI Collaborative Workspace",
        "path": "cortxos_multi_agent_ai_collaborative_workspace/code.html",
        "icon": "hub",
        "desc": "Multi-agent collaborative canvas & IDE",
        "category": "canvas"
    },
    {
        "id": "audit",
        "name": "Audit Pipeline",
        "path": "audit_pipeline/code.html",
        "icon": "verified_user",
        "desc": "Security verification, consensus & audit trail",
        "category": "governance"
    },
    {
        "id": "knowledge",
        "name": "Knowledge Graph",
        "path": "knowledge_graph/code.html",
        "icon": "account_tree",
        "desc": "Vector embeddings & entity relationship mesh",
        "category": "knowledge"
    },
    {
        "id": "integrations",
        "name": "Integrations API Hub",
        "path": "integrations_api_hub/code.html",
        "icon": "api",
        "desc": "REST, Webhook, MCP & Agent protocol gateway",
        "category": "connectivity"
    },
    {
        "id": "training",
        "name": "Agent Training Room",
        "path": "training_room/code.html",
        "icon": "model_training",
        "desc": "Fine-tuning, LoRA evaluation & reinforcement loop",
        "category": "training"
    },
    {
        "id": "wordmark",
        "name": "Brand Design System",
        "path": "cortxos_wordmark_logo/code.html",
        "icon": "palette",
        "desc": "CortxOS Matrix tokens and typography preview",
        "category": "brand"
    }
]
