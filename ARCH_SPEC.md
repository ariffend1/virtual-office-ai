# 📐 CortxOS Architecture & System Specification

This document defines the architectural patterns, runtime invariants, and execution models for the **CortxOS Multi-Agent Studio**.

---

## 1. Architectural Philosophy
CortxOS is engineered as a **modular, event-driven multi-agent operating framework**. Its primary design goals are:
- **Low-Latency Streaming**: Bidirectional WebSocket telemetry and execution traces.
- **Provider Agnostic**: Seamless hot-swapping between Local Ollama models, Cloud LLMs (OpenAI, Anthropic), and deterministic offline neural simulators.
- **Zero-Trust Resilience**: Fallback safety nets ensuring zero downtime even during model network timeouts or local node reboots.
- **Isomorphic Design System**: Clean separation of frontend UI views and backend business logic.

---

## 2. Directory Layout & Module Responsibilities

```
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # Typed REST API endpoints
│   │   ├── websocket.py       # Live streaming WS gateway
│   │   └── views.py           # Unified Shell & module view renderers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Settings, environment variables, default state
│   │   └── websocket_manager.py # WS connection hub & background telemetry loop
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── base.py            # BaseAgentRunner abstract contract
│   │   ├── mock_runner.py     # Deterministic simulation engine
│   │   ├── ollama_runner.py   # Ollama local LLM integration
│   │   ├── cloud_runner.py    # OpenAI & Anthropic Cloud runners
│   │   └── dispatcher.py      # Multi-runner strategy engine
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models for REST & WS events
│   └── main.py                # FastAPI Application Factory
├── tests/
│   └── test_api.py            # Integration & unit test suite
├── 3d_workspace/              # 3D Spatial Canvas Module
├── audit_pipeline/            # Security & Compliance Module
├── cortxos_multi_agent_*/     # Neural Simulation & Collab Modules
├── knowledge_graph/           # Vector & Graph Topology Module
├── mission_dispatcher/        # Swarm Task Dispatcher Module
├── telemetry_gateway/         # Observability Module
├── training_room/             # Agent LoRA & Training Module
├── server.py                  # Standard CLI entry point
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Local stack orchestration
├── pyproject.toml             # Standardized packaging
└── requirements.txt           # Locked production dependencies
```

---

## 3. Data & Communication Protocol

### WebSocket Event Structure
Every WebSocket payload adheres to the `StreamMessage` or `TelemetryPayload` schema:

```json
{
  "type": "agent_stream",
  "agent": "Arch-01",
  "status": "completed",
  "source": "ollama",
  "model": "qwen2.5-coder:7b",
  "output": "=== [Arch-01 EXECUTION STREAM] ===\n...",
  "timestamp": 1726296000
}
```

### Agent State Transitions
Agents cycle through four deterministic lifecycle states:
1. `idle`: Ready for task ingestion.
2. `thinking`: Analyzing directive and forming AST execution plan.
3. `working`: Multi-threaded synthesis, tool invocation, or quorum consensus.
4. `completed`: Telemetry emitted, result verified, and broadcasted to clients.

---

## 4. Coding Conventions for AI Agents (Jules, Claude Code, Cursor)

1. **Strict Type Annotations**: All function signatures must include Python 3.10+ type hints.
2. **Pydantic Validation**: Never parse raw `dict` objects in API controllers. Use typed models from `app.models.schemas`.
3. **Async Everywhere**: All I/O operations (HTTP requests, WebSocket events, database queries) must be asynchronous (`async def` / `httpx.AsyncClient`).
4. **Resilient Fallbacks**: New execution runners must catch provider errors and return a clean `ExecutionResult(status="error")` rather than bubbling unhandled 500s.
