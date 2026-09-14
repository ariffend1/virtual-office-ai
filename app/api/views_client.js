/* CortxOS Studio Unified Live Dynamic WebSocket & REST Client Engine */
(function() {
    console.log("[CortxOS] Initializing Studio Dynamic Live Engine...");

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    let ws = null;
    let reconnectTimer = null;

    // Helper functions for DOM updates across module views
    function updateMetric(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    function appendFeedLog(containerId, text, source = "SWARM") {
        const feed = document.getElementById(containerId);
        if (!feed) return;

        const timeStr = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = "p-1.5 bg-surface-container-low rounded hover:bg-surface-container transition-colors flex items-start gap-2 font-mono text-xs";
        entry.innerHTML = `
            <span class="text-on-surface-variant">${timeStr}</span>
            <span class="px-1 rounded bg-secondary/15 text-secondary font-semibold">${source}</span>
            <span class="text-on-surface flex-1 break-words">${text}</span>
        `;
        feed.appendChild(entry);
        feed.scrollTop = feed.scrollHeight;
    }

    // Connect to global WebSocket stream
    function initWebSocket() {
        if (!host) return;
        ws = new WebSocket(`${protocol}//${host}/ws/stream`);

        ws.onopen = function() {
            console.log("[CortxOS WS] Connected to live stream gateway.");
            updateMetric("ws-status-text", "CONNECTED");
            const dot = document.getElementById("ws-status-dot");
            if (dot) dot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-pulse";
        };

        ws.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);

                if (data.type === "telemetry") {
                    updateMetric("hud-fps", data.fps);
                    updateMetric("hud-lat", data.latency_ms + "ms");
                    updateMetric("hud-tokens", (data.tokens || 48219).toLocaleString());
                    updateMetric("hud-cost", "$" + (data.cost || 0.076).toFixed(3));
                }
                else if (data.type === "agent_stream") {
                    console.log(`[CortxOS WS Stream @${data.agent}]`, data.output);

                    // Update RPC feeds and terminal logs across modules
                    appendFeedLog("rpc-log-feed", `[@${data.agent} - ${data.status.toUpperCase()}]: ${data.output}`, data.agent);
                    appendFeedLog("terminal-logs", `[@${data.agent}]: ${data.output}`, data.agent);

                    // Update live agents count / badges if available
                    const activeAgentBadge = document.getElementById(`agent-badge-${data.agent}`);
                    if (activeAgentBadge) {
                        activeAgentBadge.className = "px-1.5 py-0.5 rounded text-xs font-semibold bg-emerald-500/20 text-emerald-400";
                    }
                }
            } catch (e) {
                console.warn("[CortxOS WS] Error parsing payload:", e);
            }
        };

        ws.onclose = function() {
            console.log("[CortxOS WS] Closed. Reconnecting in 3s...");
            updateMetric("ws-status-text", "RECONNECTING");
            const dot = document.getElementById("ws-status-dot");
            if (dot) dot.className = "w-2 h-2 rounded-full bg-amber-500 animate-ping";
            reconnectTimer = setTimeout(initWebSocket, 3000);
        };

        ws.onerror = function(err) {
            console.error("[CortxOS WS] Error:", err);
        };
    }

    // Fetch live agents & tasks from REST API
    async function syncBackendData() {
        try {
            const healthRes = await fetch('/api/health');
            if (healthRes.ok) {
                const health = await healthRes.json();
                updateMetric("active-agents-count", Object.keys(health.agents).length);
            }

            const tasksRes = await fetch('/api/tasks');
            if (tasksRes.ok) {
                const tasksData = await tasksRes.json();
                const feed = document.getElementById("task-history-list");
                if (feed && tasksData.tasks) {
                    feed.innerHTML = "";
                    tasksData.tasks.forEach(t => {
                        const row = document.createElement('div');
                        row.className = "p-2 bg-surface-container-low rounded flex items-center justify-between text-xs font-mono mb-1";
                        row.innerHTML = `
                            <div class="flex items-center gap-2">
                                <span class="px-1.5 py-0.5 rounded font-bold bg-secondary/15 text-secondary">${t.agent_id}</span>
                                <span class="truncate max-w-xs text-on-surface">${t.prompt}</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="px-1.5 py-0.5 rounded text-[10px] uppercase ${t.status === 'completed' ? 'bg-emerald-500/15 text-emerald-600' : 'bg-amber-500/15 text-amber-600'}">${t.status}</span>
                                <span class="text-on-surface-variant">${t.latency_ms}ms</span>
                            </div>
                        `;
                        feed.appendChild(row);
                    });
                }
            }
        } catch (e) {
            console.warn("[CortxOS REST Sync] Failed:", e);
        }
    }

    // Bind dispatch buttons across module views
    function bindInteractiveControls() {
        // Task Dispatch button
        const deployBtn = document.getElementById("btn-deploy-task") || document.getElementById("btn-dispatch-task");
        if (deployBtn) {
            deployBtn.onclick = async function() {
                const inputEl = document.getElementById("task-directive-input") || document.getElementById("quick-prompt-input");
                const prompt = inputEl ? inputEl.value.trim() : "";
                if (!prompt) return;

                appendFeedLog("rpc-log-feed", `Dispatching directive: "${prompt}"`, "USER");

                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: "dispatch_task",
                        agent: "Arch-01",
                        prompt: prompt
                    }));
                } else {
                    // Fallback to REST dispatch
                    try {
                        const res = await fetch('/api/dispatch', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ agent: "Arch-01", prompt: prompt })
                        });
                        const data = await res.json();
                        appendFeedLog("rpc-log-feed", `Result: ${data.result.response}`, "REST");
                    } catch (e) {
                        alert("Dispatch failed: " + e.message);
                    }
                }
                if (inputEl) inputEl.value = "";
                setTimeout(syncBackendData, 1000);
            };
        }

        // Quick send RPC bar
        const quickSendBtn = document.getElementById("btn-quick-send");
        const quickInput = document.getElementById("rpc-quick-msg");
        if (quickSendBtn && quickInput) {
            const handleQuick = () => {
                const val = quickInput.value.trim();
                if (!val) return;
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: "dispatch_task", agent: "Audit-02", prompt: val }));
                }
                quickInput.value = "";
            };
            quickSendBtn.onclick = handleQuick;
            quickInput.onkeydown = (e) => { if (e.key === 'Enter') handleQuick(); };
        }
    }

    // Auto-init on DOM Ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initWebSocket();
            syncBackendData();
            bindInteractiveControls();
        });
    } else {
        initWebSocket();
        syncBackendData();
        bindInteractiveControls();
    }
})();
