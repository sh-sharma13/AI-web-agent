const BASE_URL = "http://localhost:5000";

document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    setupEventListeners();
    checkBackendConnection();

    const token = await getAuthToken(false);
    if (token) {
        showDashboard(token);
    } else {
        console.log("[BlueLays] User not logged in.");
    }
}

function setupEventListeners() {
    const loginBtn = document.getElementById("login-btn");
    if (loginBtn) {
        loginBtn.addEventListener("click", handleLogin);
    }

    const scanBtn = document.getElementById("scan-btn");
    if (scanBtn) {
        scanBtn.addEventListener("click", handleScanHistory);
    }

    const agentSubmit = document.getElementById("agent-submit");
    if (agentSubmit) {
        agentSubmit.addEventListener("click", handleAgentAction);
    }

    const summaryBtn = document.getElementById("summary-btn");
    if (summaryBtn) {
        summaryBtn.addEventListener("click", handleSummaryAction);
    }
}

async function handleLogin() {
    const token = await getAuthToken(true);
    if (token) {
        showDashboard(token);
    } else {
        showToast("Login failed. Please try again.", "error");
    }
}

function getAuthToken(interactive) {
    return new Promise((resolve) => {
        chrome.identity.getAuthToken({ interactive: interactive }, (token) => {
            if (chrome.runtime.lastError) {
                console.warn("[BlueLays] Auth Error:", chrome.runtime.lastError);
                resolve(null);
            } else {
                resolve(token);
            }
        });
    });
}

function showDashboard(token) {
    document.getElementById("auth-section").classList.add("hidden");
    document.getElementById("dashboard-section").classList.remove("hidden");
}

async function handleScanHistory() {
    const scanBtn = document.getElementById("scan-btn");
    scanBtn.textContent = "Scanning...";
    scanBtn.disabled = true;

    try {
        const history = await getRelevantHistory();
        if (!history || history.length === 0) {
            showToast("No recent study history found.", "warning");
            return;
        }

        const token = await getAuthToken(false);
        const res = await fetch(`${BASE_URL}/ai/analyze_history`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                history: history,
                credentials: { token: token },
                source: "popup_manual"
            })
        });

        if (!res.ok) throw new Error("Analysis failed");

        const data = await res.json();
        renderDashboard(data.dashboard_stats, data.suggested_events);
        showToast("Dashboard updated!", "success");

    } catch (e) {
        console.error(e);
        showToast("Scan failed. Is backend running?", "error");
    } finally {
        scanBtn.textContent = "🔄 Scan Learning History";
        scanBtn.disabled = false;
    }
}

function getRelevantHistory() {
    return new Promise(resolve => {
        const oneWeekAgo = Date.now() - 7 * 24 * 3600 * 1000;
        chrome.history.search({ text: "", maxResults: 100, startTime: oneWeekAgo }, (items) => {
            const relevant = items.filter(i =>
                (i.url.includes("youtube.com/watch") || i.url.includes("udemy.com/course"))
                && i.title
            ).map(h => ({
                title: h.title,
                url: h.url,
                lastVisitTime: h.lastVisitTime
            }));
            resolve(relevant);
        });
    });
}

async function handleAgentAction() {
    const agentInput = document.getElementById("agent-input");
    const agentSubmit = document.getElementById("agent-submit");
    const command = agentInput.value.trim();

    if (!command) return;

    agentSubmit.textContent = "Processing...";
    agentSubmit.disabled = true;
    toggleResponseCard(false);

    try {
        const token = await getAuthToken(false);
        const res = await fetch(`${BASE_URL}/ai/agent_action`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                command: command,
                context: "User is on Chrome Extension Dashboard.",
                credentials: { token: token },
                notion_token: null
            })
        });

        const data = await res.json();
        displayAgentResponse(data);

    } catch (e) {
        showToast("Agent Error: " + e.message, "error");
    } finally {
        agentSubmit.textContent = "Execute";
        agentSubmit.disabled = false;
    }
}

async function handleSummaryAction() {
    const result = await new Promise(resolve => chrome.storage.local.get("lastCompletedVideo", resolve));
    const video = result.lastCompletedVideo;

    if (!video) {
        showToast("No recent video session found to summarize!", "warning");
        return;
    }

    const agentInput = document.getElementById("agent-input");
    agentInput.value = `Summarize this session: ${video.title} (${video.url}) and save as a note in Notion`;

    handleAgentAction();
}

function renderDashboard(stats, events) {
    const container = document.getElementById("topics-container");
    container.innerHTML = "";

    if (!stats || stats.length === 0) {
        container.innerHTML = "<p style='text-align:center; color: var(--text-secondary);'>No topics identified yet.</p>";
    } else {
        stats.forEach(topic => {
            const card = document.createElement("div");
            card.className = "topic-card";
            card.innerHTML = `
                <div class="topic-header">
                    <span class="topic-title">${topic.topic}</span>
                    <span style="font-size: 0.9em; color: var(--accent);">${topic.progress}%</span>
                </div>
                <div class="topic-progress-bar">
                    <div class="topic-progress-fill" style="width: ${topic.progress}%"></div>
                </div>
                <div class="topic-meta">
                    <div style="margin-bottom:4px;">📺 ${topic.recent_resource ? topic.recent_resource.substring(0, 30) + '...' : 'N/A'}</div>
                    <div>
                        ${topic.url ?
                    `<a href="${topic.url}" target="_blank" style="color: #58a6ff; text-decoration: none; font-weight:500;">⏭️ ${topic.next_step} &rarr;</a>` :
                    `<span>⏭️ ${topic.next_step}</span>`
                }
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    }

    const list = document.getElementById("rec-list");
    list.innerHTML = "";
    if (events && events.length > 0) {
        events.forEach(ev => {
            const li = document.createElement("li");
            const isScheduled = ev.status === "scheduled";
            const icon = isScheduled ? "✅" : "📅";
            li.innerHTML = `
                <span style="font-size:1.2em;">${icon}</span>
                <div>
                    <div style="font-weight:500; color: var(--text-primary);">${ev.summary}</div>
                    <div style="font-size:0.85em; color: var(--text-secondary);">${new Date(ev.start_time).toLocaleString()}</div>
                </div>
            `;
            list.appendChild(li);
        });
    }
}

function displayAgentResponse(data) {
    const responseContent = document.getElementById("response-content");
    let html = "";

    if (data.status === "success" && data.execution_result) {
        const result = data.execution_result;

        if (result.includes("Note saved")) {
            html = `
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 8px;">📝</div>
                    <div style="font-weight: 600; font-size: 1.1em; color: var(--text-primary);">Note Saved to Notion!</div>
                    <p style="font-size: 0.9em; color: var(--text-secondary); margin-top:5px;">${result}</p>
                </div>`;
        } else if (result.includes("Event created")) {
            html = `
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 8px;">📅</div>
                    <div style="font-weight: 600; font-size: 1.1em; color: var(--text-primary);">Session Scheduled!</div>
                    <p style="font-size: 0.9em; color: var(--text-secondary); margin-top:5px;">${result}</p>
                </div>`;
        } else {
            html = `<div style="white-space: pre-wrap; font-family: monospace; font-size: 0.9em;">${result}</div>`;
        }
    } else {
        const error = data.error || data.details || "Unknown Error";
        html = `
            <div style="color: #ff7b72; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 5px;">⚠️</div>
                <div>${error}</div>
            </div>`;
    }

    responseContent.innerHTML = html;
    toggleResponseCard(true);
}

function toggleResponseCard(show) {
    const card = document.getElementById("agent-response");
    if (show) card.classList.remove("hidden");
    else card.classList.add("hidden");
}

function showToast(message, type = "info") {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.style.cssText = `
            position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
            padding: 10px 20px; border-radius: 20px; color: white;
            font-size: 0.9em; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: opacity 0.3s; opacity: 0; pointer-events: none;
        `;
        document.body.appendChild(toast);
    }

    const colors = {
        "error": "#da3633",
        "success": "#238636",
        "warning": "#d29922",
        "info": "#1f6feb"
    };

    toast.style.backgroundColor = colors[type];
    toast.textContent = message;
    toast.style.opacity = "1";

    setTimeout(() => {
        toast.style.opacity = "0";
    }, 3000);
}

async function checkBackendConnection() {
    const statusEl = document.getElementById("connection-status");
    try {
        const res = await fetch(`${BASE_URL}/`);
        if (res.ok) {
            statusEl.classList.replace("offline", "online");
            statusEl.title = "Backend Online";
        }
    } catch (e) {
        statusEl.classList.replace("online", "offline");
        statusEl.title = "Backend Offline";
    }
}
