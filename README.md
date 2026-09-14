# 🧠 CortxOS — Next-Gen Multi-Agent Operating System & Neural Simulation Studio

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![WebSocket](https://img.shields.io/badge/WebSocket-Live%20Stream-orange?style=flat-square)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
[![Architecture](https://img.shields.io/badge/Architecture-Modular%20Layered-purple?style=flat-square)](#architecture)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

**CortxOS** is an autonomous multi-agent operating system and neural simulation environment. It provides real-time telemetry streaming, a 3D isometric simulation studio, Byzantine Fault Tolerance (BFT) consensus pipelines, dynamic agent dispatching, and native tool execution support across local models (Ollama) and cloud APIs (OpenAI, Anthropic).

---

## 🏗️ Architecture Overview

```
                          ┌────────────────────────┐
                          │  Web Browser / Client  │
                          └───────────┬────────────┘
                                      │ HTTP / WebSocket
                                      ▼
               ┌────────────────────────────────────────────────┐
               │         CortxOS Application Gateway            │
               │         (FastAPI + WebSocketManager)           │
               └───────┬──────────────┬──────────────┬──────────┘
                       │              │              │
            ┌──────────▼───┐   ┌──────▼─────┐   ┌────▼─────────┐
            │  REST Router │   │ WS Stream  │   │ Static Shell │
            │  /api/*      │   │ /ws/stream │   │ / & /view/*  │
            └──────────┬───┘   └──────┬─────┘   └──────────────┘
                       │              │
                       └──────┬───────┘
                              ▼
            ┌───────────────────────────────────┐
            │     EngineDispatcher Layer        │
            └───────┬───────────┬───────────┬───┘
                    │           │           │
          ┌─────────▼──┐   ┌────▼─────┐  ┌──▼─────────────┐
          │   Ollama   │   │  Cloud   │  │  Mock Neural   │
          │ Local LLM  │   │  OpenAI/ │  │   Sim Engine   │
          │ (qwen/etc) │   │ Anthropic│  │ (Deterministic)│
          └────────────┘   └──────────┘  └────────────────┘
```

### Key Components

- **`app/main.py`**: Clean application factory pattern with router aggregation.
- **`app/api/`**: 
  - `routes.py`: Typed REST endpoints (`/api/health`, `/api/modules`, `/api/agents`, `/api/dispatch`).
  - `websocket.py`: Live bidirectional WebSocket stream (`/ws/stream`).
  - `views.py`: Modular static and template view rendering.
- **`app/core/`**: Centralized configuration (`config.py`) and WebSocket state management (`websocket_manager.py`).
- **`app/execution/`**: Extensible runner hierarchy (`BaseAgentRunner`, `OllamaRunner`, `CloudLLMRunner`, `MockNeuralRunner`, `EngineDispatcher`).
- **`app/models/`**: Strongly typed Pydantic models for REST & WebSocket payloads.

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.10+
- (Optional) Docker & Docker Compose
- (Optional) Ollama running locally (`ollama run qwen2.5-coder:7b`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-org/cortxos.git
cd cortxos

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Server
```bash
python3 server.py
# Or via uvicorn directly:
uvicorn app.main:app --host 0.0.0.0 --port 8899 --reload
```
Navigate to **`http://localhost:8899`** in your browser.

### 4. Running with Docker
```bash
docker-compose up -d --build
```

---

## 📡 API Specification

### REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Comprehensive cluster health, agents, module count, and active WS clients |
| `GET` | `/api/modules` | List of 10 CortxOS interactive design modules |
| `GET` | `/api/agents` | Agent profiles, roles, and capability matrices |
| `POST` | `/api/dispatch` | Dispatch task directive to specific agent with runner fallback |
| `GET` | `/view/{path}` | Serve standalone module canvas views |
| `GET` | `/docs` | Interactive Swagger / OpenAPI documentation |

#### Example Dispatch Payload (`POST /api/dispatch`)
```json
{
  "agent": "Audit-02",
  "prompt": "Run Byzantine Fault Tolerance audit on task DAG",
  "runner": "auto"
}
```

### WebSocket Protocol (`/ws/stream`)
- **Handshake**: Client connects and receives `system_handshake` with active agents.
- **Telemetry Heartbeat**: Emitted every 1.0s (`fps`, `latency_ms`, `tokens`, `cost`, `threads`).
- **Task Dispatch**: Send `{"type": "dispatch_task", "agent": "Arch-01", "prompt": "..."}` to trigger streaming thoughts and execution results.

---

## 🤖 Google Jules & AI Agent Collaboration

This repository is optimized for autonomous agents (Google Jules, Claude Code, OpenCode, Codex).

### Agent Guidelines
1. **Pydantic Schemas First**: Always update `app/models/schemas.py` when modifying request/response structures.
2. **Execution Runner Extensibility**: Implement new model providers by subclassing `BaseAgentRunner` in `app/execution/`.
3. **Automated Verification**: Run `python3 tests/test_api.py` before submitting any pull request.
4. **Architecture Spec**: Read [ARCH_SPEC.md](ARCH_SPEC.md) for deeper design invariants.

---

## 🧪 Test Suite

```bash
python3 tests/test_api.py
```

All 5 core test suites run asynchronously and test:
- `/api/health` status and schema conformance.
- Module discovery across all 10 views.
- HTML view static rendering.
- REST dispatch with deterministic mock simulation fallback.
- Unified Shell index interface.

---

## 🗺️ Roadmap
- [x] Modular FastAPI backend architecture (`app/`).
- [x] Multi-runner execution engine (Ollama, Cloud, Mock).
- [x] Real-time WebSocket telemetry HUD & Live Stream Log.
- [ ] Model Context Protocol (MCP) tool integration bridge.
- [ ] SQLite/PostgreSQL persistent task execution log.
- [ ] WebGPU Shader canvas hardware acceleration.

---

## 📄 License
MIT License. Created for the CortxOS Multi-Agent Ecosystem.
