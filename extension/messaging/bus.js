// COMPAREX Extension Messaging Bus Abstraction

const COMPAREX_BUS = {
  sendToBackground(type, payload, callback) {
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
      chrome.runtime.sendMessage({ type, payload }, (response) => {
        if (chrome.runtime.lastError) {
          console.warn("[COMPAREX Bus] Send error:", chrome.runtime.lastError.message);
          if (callback) callback({ success: false, error: chrome.runtime.lastError.message });
        } else if (callback) {
          callback(response);
        }
      });
    }
  },

  onMessage(handler) {
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        handler(message, sender, sendResponse);
        return true; // Keep channel open for async response
      });
    }
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = COMPAREX_BUS;
}
