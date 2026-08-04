// COMPAREX Extension Background Service Worker (Manifest V3)

importScripts(
  "../shared/constants.js",
  "../storage/extension_storage.js",
  "../services/api_service.js"
);

console.log("[COMPAREX ServiceWorker] Initialized v1.0.0");

let currentDetectedProduct = null;
let lastComparisonResult = null;
let isBackendOnline = false;

// ── Service Worker Lifecycle ──────────────────────────────────────────────────
chrome.runtime.onInstalled.addListener((details) => {
  console.log("[COMPAREX ServiceWorker] Installed event:", details.reason);
  COMPAREX_STORAGE.setSettings(COMPAREX_CONSTANTS.DEFAULT_SETTINGS);
});

// Health check interval
async function checkBackendHealth() {
  const status = await COMPAREX_API.getStatus();
  isBackendOnline = status && status.status === "online";
  console.log("[COMPAREX ServiceWorker] Backend status:", isBackendOnline ? "ONLINE" : "OFFLINE");
}

checkBackendHealth();

// ── Message Router ────────────────────────────────────────────────────────────
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const { type, payload } = message || {};

  if (type === COMPAREX_CONSTANTS.MESSAGE_TYPES.PRODUCT_DETECTED) {
    currentDetectedProduct = payload;
    console.log("[COMPAREX ServiceWorker] Product detected:", payload.title);

    // Call backend ingest API
    COMPAREX_API.ingestProduct(payload).then((compareRes) => {
      lastComparisonResult = compareRes;
      sendResponse({ success: true, compare: compareRes });

      // Notify active tab to display overlay if enabled
      if (sender.tab && sender.tab.id) {
        chrome.tabs.sendMessage(sender.tab.id, {
          type: "RENDER_OVERLAY",
          payload: compareRes,
        });
      }
    });
    return true; // Keep channel open for async response
  }

  if (type === COMPAREX_CONSTANTS.MESSAGE_TYPES.GET_STATUS) {
    sendResponse({
      isOnline: isBackendOnline,
      currentProduct: currentDetectedProduct,
      lastCompare: lastComparisonResult,
      version: COMPAREX_CONSTANTS.VERSION,
    });
    return false;
  }

  if (type === COMPAREX_CONSTANTS.MESSAGE_TYPES.QUERY_COMPARE) {
    COMPAREX_API.quickCompare(payload.query, payload.category).then((res) => {
      sendResponse({ success: true, data: res });
    });
    return true;
  }

  return false;
});
