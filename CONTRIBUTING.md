# 🤝 Contributing to CortxOS

We welcome contributions from human engineers and autonomous AI agents (Google Jules, Claude Code, Cursor, OpenCode, Hermes).

---

## 🛠️ Development Workflow

1. **Fork & Clone**:
   ```bash
   git clone https://github.com/your-org/cortxos.git
   cd cortxos
   ```

2. **Set up Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Run Verification Test Suite**:
   ```bash
   python3 tests/test_api.py
   ```

---

## 📐 Agent & Developer Pull Request Checklist

Before submitting a PR, ensure:
- [ ] Code passes test suite (`python3 tests/test_api.py`).
- [ ] No regression in existing endpoints (`/api/health`, `/api/modules`, `/api/dispatch`, `/ws/stream`).
- [ ] All new data schemas are declared in `app/models/schemas.py`.
- [ ] New execution engines inherit from `BaseAgentRunner` in `app/execution/base.py`.
- [ ] Documentation and comments are concise and free of unnecessary fluff.

---

## 🔒 Security & Safe Execution
CortxOS operates with a sandboxed isolation mindset. Never expose internal host system execution primitives over unprotected HTTP endpoints without authentication or sandbox wrapping.
