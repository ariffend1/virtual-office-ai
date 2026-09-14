from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.core.config import settings, DEFAULT_MODULES

views_router = APIRouter(tags=["CortxOS Studio Views"])

def render_shell(selected_module_id: str = "studio") -> str:
    selected_module = next((m for m in DEFAULT_MODULES if m["id"] == selected_module_id), DEFAULT_MODULES[0])
    
    module_buttons = ""
    for m in DEFAULT_MODULES:
        is_active = (m["id"] == selected_module["id"])
        active_cls = "bg-secondary-container text-on-secondary-container font-semibold border-l-4 border-secondary" if is_active else "text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
        module_buttons += f"""
        <a href="/?module={m['id']}" class="flex items-center gap-2.5 px-3 py-2 rounded text-xs transition-all {active_cls}">
            <span class="material-symbols-outlined text-[18px]">{m['icon']}</span>
            <div class="flex-1 truncate">
                <div class="font-medium truncate">{m['name']}</div>
            </div>
        </a>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>CortxOS Multi-Agent Studio | Port {settings.port}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: "class",
            theme: {{
                extend: {{
                    colors: {{
                        surface: "#f8f9ff",
                        "surface-dim": "#cbdbf5",
                        "surface-container-lowest": "#ffffff",
                        "surface-container-low": "#eff4ff",
                        "surface-container": "#e5eeff",
                        "surface-container-high": "#dce9ff",
                        "surface-container-highest": "#d3e4fe",
                        "on-surface": "#0b1c30",
                        "on-surface-variant": "#45464d",
                        primary: "#000000",
                        "on-primary": "#ffffff",
                        "primary-container": "#131b2e",
                        secondary: "#00687a",
                        "secondary-container": "#57dffe",
                        "on-secondary-container": "#006172",
                        "tertiary-container": "#23005c",
                        "on-tertiary-container": "#9466ff",
                        error: "#ba1a1a",
                        "error-container": "#ffdad6"
                    }},
                    fontFamily: {{
                        sans: ["Inter", "sans-serif"],
                        mono: ["JetBrains Mono", "monospace"]
                    }}
                }}
            }}
        }}
    </script>
    <style>
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #eff4ff; }}
        ::-webkit-scrollbar-thumb {{ background: #cbdbf5; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #565e74; }}
    </style>
</head>
<body class="bg-surface text-on-surface font-sans h-screen flex flex-col overflow-hidden">
    <!-- Top Global Header -->
    <header class="h-12 border-b border-surface-container-high bg-surface-container-lowest px-4 flex items-center justify-between shrink-0 z-30 shadow-sm">
        <div class="flex items-center gap-3">
            <div class="w-7 h-7 rounded bg-primary-container flex items-center justify-center text-secondary-container font-mono font-bold text-sm">
                CX
            </div>
            <div class="flex items-center gap-2">
                <span class="font-bold tracking-tight text-sm font-mono">CortxOS</span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-mono font-semibold">STUDIO SANDBOX</span>
                <span class="text-xs text-on-surface-variant font-mono">PORT:{settings.port}</span>
            </div>
        </div>

        <!-- Realtime Telemetry HUD (Direct from WebSocket) -->
        <div class="flex items-center gap-4 text-xs font-mono">
            <div class="flex items-center gap-1.5 bg-surface-container px-2.5 py-1 rounded">
                <span id="ws-status-dot" class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
                <span id="ws-status-text" class="text-on-surface-variant">Connecting WS...</span>
            </div>
            <div class="hidden sm:flex items-center gap-3 text-on-surface-variant bg-surface-container-low px-3 py-1 rounded">
                <div>FPS: <span id="hud-fps" class="text-on-surface font-semibold">--</span></div>
                <div class="text-surface-dim">|</div>
                <div>LATENCY: <span id="hud-lat" class="text-secondary font-semibold">-- ms</span></div>
                <div class="text-surface-dim">|</div>
                <div>TOKENS: <span id="hud-tokens" class="text-on-surface font-semibold">--</span></div>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="toggleTerminal()" class="px-2.5 py-1 bg-surface-container hover:bg-surface-container-high rounded text-xs font-mono font-medium flex items-center gap-1">
                    <span class="material-symbols-outlined text-[14px]">terminal</span>
                    <span>Live Stream Log</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Studio Split View -->
    <div class="flex-1 flex overflow-hidden">
        <!-- Sidebar Navigation Drawer -->
        <aside class="w-64 border-r border-surface-container-high bg-surface-container-lowest flex flex-col shrink-0">
            <div class="p-3 border-b border-surface-container-high">
                <div class="text-[11px] font-mono font-semibold uppercase tracking-wider text-on-surface-variant">Studio Modules</div>
            </div>
            <nav class="flex-1 p-2 space-y-1 overflow-y-auto">
                {module_buttons}
            </nav>

            <!-- Agent Quick Dispatcher Dock -->
            <div class="p-3 border-t border-surface-container-high bg-surface-container-low">
                <div class="text-[11px] font-mono font-semibold uppercase tracking-wider text-on-surface-variant mb-2">Instant Dispatch</div>
                <div class="space-y-2">
                    <select id="quick-agent-select" class="w-full text-xs font-mono bg-surface-container-lowest border border-surface-container-high rounded p-1.5 text-on-surface">
                        <option value="Arch-01">Arch-01 (Systems Eng)</option>
                        <option value="Audit-02">Audit-02 (Security/BFT)</option>
                        <option value="Search-03">Search-03 (Researcher)</option>
                        <option value="Astra-04">Astra-04 (WebGPU/PBR)</option>
                    </select>
                    <div class="flex gap-1">
                        <input id="quick-prompt-input" type="text" placeholder="Send prompt to agent..." class="flex-1 text-xs px-2 py-1.5 bg-surface-container-lowest border border-surface-container-high rounded font-mono focus:outline-none focus:border-secondary" onkeydown="if(event.key==='Enter') dispatchQuickTask()"/>
                        <button onclick="dispatchQuickTask()" class="px-2.5 py-1.5 bg-primary text-on-primary rounded text-xs hover:opacity-90">
                            <span class="material-symbols-outlined text-[14px]">send</span>
                        </button>
                    </div>
                </div>
            </div>
        </aside>

        <!-- Module Content Area (Iframe embed of the selected standalone view) -->
        <main class="flex-1 relative flex flex-col overflow-hidden bg-surface">
            <iframe id="module-frame" src="/view/{selected_module['path']}" class="w-full flex-1 border-0"></iframe>

            <!-- Collapsible Live Stream Terminal Console Overlay -->
            <div id="live-terminal-panel" class="h-56 bg-primary-container text-surface border-t-2 border-secondary flex flex-col font-mono text-xs transition-all duration-200">
                <div class="h-7 bg-[#0b1322] px-3 flex items-center justify-between border-b border-surface-container-high/30 select-none">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                        <span class="text-[11px] font-semibold text-secondary-container">WEBSOCKET AGENT RUNTIME STREAM (ws://localhost:{settings.port}/ws/stream)</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <button onclick="clearTerminal()" class="text-[10px] text-on-surface-variant hover:text-white px-2 py-0.5 rounded bg-white/5">Clear</button>
                        <button onclick="toggleTerminal()" class="text-[10px] text-on-surface-variant hover:text-white px-2 py-0.5 rounded bg-white/5">Close</button>
                    </div>
                </div>
                <div id="terminal-logs" class="flex-1 p-3 overflow-y-auto space-y-1 text-xs leading-relaxed select-text">
                    <div class="text-secondary-container">[*] CortxOS Multi-Agent Runtime Initialized. Modular architecture v{settings.app_version} ready.</div>
                </div>
            </div>
        </main>
    </div>

    <!-- Client-side WebSocket & Bridge Handler -->
    <script>
        let ws;
        const port = {settings.port};
        const logsEl = document.getElementById('terminal-logs');
        const statusDot = document.getElementById('ws-status-dot');
        const statusText = document.getElementById('ws-status-text');
        const hudFps = document.getElementById('hud-fps');
        const hudLat = document.getElementById('hud-lat');
        const hudTokens = document.getElementById('hud-tokens');

        function appendLog(text, colorClass = "text-white") {{
            const line = document.createElement('div');
            line.className = colorClass;
            const time = new Date().toLocaleTimeString();
            line.textContent = `[${{time}}] ${{text}}`;
            logsEl.appendChild(line);
            logsEl.scrollTop = logsEl.scrollHeight;
        }}

        function clearTerminal() {{
            logsEl.innerHTML = '<div class="text-secondary-container">[*] Terminal cleared. Connected to ws://localhost:{settings.port}/ws/stream</div>';
        }}

        function toggleTerminal() {{
            const panel = document.getElementById('live-terminal-panel');
            if (panel.style.display === 'none') {{
                panel.style.display = 'flex';
            }} else {{
                panel.style.display = 'none';
            }}
        }}

        function connectWebSocket() {{
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${{protocol}}//${{window.location.host}}/ws/stream`;
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {{
                statusDot.className = "w-2 h-2 rounded-full bg-emerald-500";
                statusText.textContent = "WS ACTIVE";
                appendLog("WebSocket connection established with CortxOS Bridge", "text-emerald-400");
            }};

            ws.onmessage = (event) => {{
                try {{
                    const msg = JSON.parse(event.data);
                    if (msg.type === "telemetry") {{
                        if (hudFps) hudFps.textContent = msg.fps;
                        if (hudLat) hudLat.textContent = msg.latency_ms + " ms";
                        if (hudTokens) hudTokens.textContent = msg.tokens.toLocaleString();
                    }} else if (msg.type === "agent_stream") {{
                        const color = msg.status === "completed" ? "text-emerald-300 font-medium" : (msg.status === "thinking" ? "text-amber-300" : "text-sky-300");
                        appendLog(`[@${{msg.agent}} - ${{msg.status.toUpperCase()}}]: ${{msg.output}}`, color);
                    }} else if (msg.type === "system_handshake") {{
                        appendLog(`[SYSTEM]: ${{msg.message}} (Agents: ${{msg.agents.join(', ')}})`, "text-secondary-container");
                    }}
                }} catch (e) {{
                    appendLog("RAW: " + event.data, "text-gray-400");
                }}
            }};

            ws.onclose = () => {{
                statusDot.className = "w-2 h-2 rounded-full bg-red-500";
                statusText.textContent = "DISCONNECTED";
                appendLog("WebSocket connection closed. Reconnecting in 2s...", "text-red-400");
                setTimeout(connectWebSocket, 2000);
            }};

            ws.onerror = (err) => {{
                console.error("WS error:", err);
            }};
        }}

        function dispatchQuickTask() {{
            const agent = document.getElementById('quick-agent-select').value;
            const promptInput = document.getElementById('quick-prompt-input');
            const prompt = promptInput.value.trim();
            if (!prompt) return;

            if (ws && ws.readyState === WebSocket.OPEN) {{
                ws.send(JSON.stringify({{
                    type: "dispatch_task",
                    agent: agent,
                    prompt: prompt
                }}));
                appendLog(`[DISPATCH] Sent directive to ${{agent}}: "${{prompt}}"`, "text-yellow-200");
                promptInput.value = "";
            }} else {{
                appendLog("[ERROR] WebSocket is not connected.", "text-red-400");
            }}
        }}

        window.addEventListener('DOMContentLoaded', connectWebSocket);
    </script>
</body>
</html>
"""

@views_router.get("/", response_class=HTMLResponse)
async def get_index(module: Optional[str] = "studio"):
    """Serves the unified multi-agent shell interface."""
    return HTMLResponse(content=render_shell(module))

@views_router.get("/view/{file_path:path}", response_class=HTMLResponse)
async def serve_view_file(file_path: str):
    """Serves individual standalone interactive design module HTML files with client engine injected."""
    target_path = settings.base_dir / file_path
    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail=f"Module view path not found: {file_path}")
    
    content = target_path.read_text(encoding="utf-8", errors="ignore")
    # Inject unified client script before </body> tag if present
    injection = '<script src="/static/app/api/views_client.js"></script>'
    if "</body>" in content:
        content = content.replace("</body>", f"{injection}\n</body>")
    else:
        content += f"\n{injection}"

    return HTMLResponse(content=content)
