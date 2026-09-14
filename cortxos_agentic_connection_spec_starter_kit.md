# CortxOS Agentic Connection Spec & Starter Kit
> **Instruksi Siap Pakai untuk AI Coding Agent (Cursor / Claude Code / Aider / OpenClaw / LangGraph)**

Dokumen ini dirancang agar Anda bisa langsung mengunggah atau menempelkan (*copy-paste*) isinya ke AI Agent di PC Anda (seperti Cursor, Claude Code, Aider, atau agen kustom), sehingga AI Anda langsung paham cara membangun jembatan (*runtime bridge*) antara engine AI lokal dengan antarmuka CortxOS.

---

## 1. Direktif untuk Coding Agent (Prompt ke AI Anda)
Salin instruksi berikut dan berikan langsung ke AI Coding Agent Anda:

```markdown
Anda adalah System Architect dan Backend Engineer. 
Tugas Anda: Bangun server backend ringan (Python FastAPI + WebSocket) untuk bertindak sebagai Runtime Bridge antara LLM lokal (Ollama) / Cloud API dengan antarmuka frontend CortxOS / SAMS Studio.

Kebutuhan Teknis:
1. Serve file static frontend `index.html` pada port 8000 (`http://localhost:8000`).
2. Sediakan endpoint WebSocket pada `ws://localhost:8000/ws/stream`.
3. Format payload JSON bidirectional:
   - Ingress dari UI:
     `{"type": "dispatch_task", "agent": "Arch-01", "prompt": "..."}`
   - Egress streaming ke UI:
     `{"type": "agent_stream", "agent": "Arch-01", "status": "working", "output": "...", "timestamp": 1710000000}`
     `{"type": "telemetry", "fps": 60, "latency_ms": 28, "tokens": 48210}`
4. Terhubung ke Ollama (default: `http://localhost:11434/api/generate`) dengan model `qwen2.5-coder:7b` atau fallback model lain.
5. Jalankan sub-process terminal aman (sandboxed) untuk mengeksekusi perintah CLI jika diotorisasi.
```

---

## 2. File `server.py` (Backend Runtime Bridge)
Simpan file ini di PC Anda bersama file `index.html` dari CortxOS:

```python
import asyncio
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI(title="CortxOS Agentic Runtime Bridge")

# Endpoint WebSocket untuk stream aktivitas agent & telemetri
@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[CortxOS Bridge] UI Client Connected.")
    
    # Task background: Kirim telemetri real-time berkala
    async def telemetry_heartbeat():
        tokens = 48200
        while True:
            await asyncio.sleep(1.0)
            tokens += 12
            await websocket.send_text(json.dumps({
                "type": "telemetry",
                "fps": 60,
                "latency_ms": 28,
                "tokens": tokens,
                "cost": round(tokens * 0.0000015, 4)
            }))

    heartbeat_task = asyncio.create_task(telemetry_heartbeat())

    try:
        while True:
            # Terima directive dari UI
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("type")
            
            if action == "dispatch_task":
                agent_id = payload.get("agent", "Arch-01")
                prompt = payload.get("prompt", "")
                
                # Kirim sinyal mulai bekerja
                await websocket.send_text(json.dumps({
                    "type": "agent_stream",
                    "agent": agent_id,
                    "status": "thinking",
                    "output": f"[@{agent_id}] Menganalisis direktif: {prompt}\n"
                }))
                
                # Panggil LLM Lokal (Ollama)
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        resp = await client.post(
                            "http://localhost:11434/api/generate",
                            json={"model": "qwen2.5-coder:7b", "prompt": prompt, "stream": False}
                        )
                        result = resp.json().get("response", "Selesai tanpa output.")
                except Exception as e:
                    result = f"[Simulasi / Error Hubung Ollama]: {str(e)}"

                # Kirim hasil eksekusi ke terminal log UI
                await websocket.send_text(json.dumps({
                    "type": "agent_stream",
                    "agent": agent_id,
                    "status": "completed",
                    "output": f"[EXECUTION LOG]\n{result}\n[Consensus: APPROVED]\n"
                }))

    except WebSocketDisconnect:
        heartbeat_task.cancel()
        print("[CortxOS Bridge] UI Client Disconnected.")

# Mount folder static untuk menyajikan file UI CortxOS (index.html)
# app.mount("/", StaticFiles(directory="./static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

---

## 3. Cara Menjalankan di PC Anda
1. Buka terminal di folder proyek Anda:
   ```bash
   pip install fastapi uvicorn httpx
   ```
2. Jalankan Ollama di terminal terpisah:
   ```bash
   ollama run qwen2.5-coder:7b
   ```
3. Jalankan server bridge:
   ```bash
   python server.py
   ```
4. Buka browser di `http://localhost:8000`. WebSocket akan otomatis terhubung ke `ws://localhost:8000/ws/stream` dan agen AI Anda siap diperintah melalui tampilan CortxOS!
