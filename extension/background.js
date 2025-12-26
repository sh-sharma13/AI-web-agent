const BASE_URL = "http://localhost:5000";
const ICON_URL = "images/icon128.png";
const LOG_PREFIX = "[BlueLays BG]";

chrome.runtime.onInstalled.addListener(() => {
    console.log(`${LOG_PREFIX} Installed.`);
    setupAlarms();
});

function setupAlarms() {
    chrome.alarms.get("autoScan", (alarm) => {
        if (!alarm) {
            chrome.alarms.create("autoScan", { periodInMinutes: 60 });
            console.log(`${LOG_PREFIX} Alarm 'autoScan' created.`);
        }
    });
}

chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === "autoScan") {
        console.log(`${LOG_PREFIX} Triggering Auto-scan...`);
        performScan();
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log(`${LOG_PREFIX} Msg Received:`, request.action);

    if (request.action === "getAuthToken") {
        chrome.identity.getAuthToken({ interactive: true }, (token) => {
            sendResponse({ token: token });
        });
        return true;
    }

    if (request.action === "VIDEO_COMPLETED") {
        handleVideoCompletion(request.data);
    }
});

async function performScan() {
    chrome.identity.getAuthToken({ interactive: false }, async (token) => {
        if (!token) {
            console.log(`${LOG_PREFIX} No token for background scan. Skipping.`);
            return;
        }

        const history = await getRecentHistory();
        if (history.length === 0) return;

        try {
            await fetch(`${BASE_URL}/ai/analyze_history`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    history: history,
                    credentials: { token: token },
                    source: "background_auto"
                })
            });
            console.log(`${LOG_PREFIX} Background scan data sent.`);
        } catch (e) {
            console.error(`${LOG_PREFIX} Scan Failed:`, e);
        }
    });
}

function handleVideoCompletion(data) {
    if (!data || !data.title) return;

    console.log(`${LOG_PREFIX} Video Completed: ${data.title}`);

    chrome.storage.local.set({ lastCompletedVideo: data }, () => {
        chrome.action.setBadgeText({ text: "!" });
        chrome.action.setBadgeBackgroundColor({ color: "#238636" });
    });
}

function getRecentHistory() {
    return new Promise(resolve => {
        chrome.history.search({
            text: "",
            maxResults: 100,
            startTime: Date.now() - 7 * 24 * 3600 * 1000
        }, (items) => {
            resolve(items.filter(i =>
                i.url.includes("youtube.com/watch") ||
                i.url.includes("udemy.com/course")
            ).map(h => ({
                title: h.title,
                url: h.url,
                lastVisitTime: h.lastVisitTime
            })));
        });
    });
}
