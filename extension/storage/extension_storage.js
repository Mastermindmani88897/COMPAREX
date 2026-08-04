// COMPAREX Extension Storage Service

const COMPAREX_STORAGE = {
  async getSettings() {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        chrome.storage.local.get(["settings"], (result) => {
          resolve(result.settings || COMPAREX_CONSTANTS.DEFAULT_SETTINGS);
        });
      } else {
        const local = localStorage.getItem("comparex_settings");
        resolve(local ? JSON.parse(local) : COMPAREX_CONSTANTS.DEFAULT_SETTINGS);
      }
    });
  },

  async setSettings(settings) {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        chrome.storage.local.set({ settings }, () => resolve(true));
      } else {
        localStorage.setItem("comparex_settings", JSON.stringify(settings));
        resolve(true);
      }
    });
  },

  async clearCache() {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        chrome.storage.local.remove(["lastProduct", "cachedCompare"], () => resolve(true));
      } else {
        localStorage.removeItem("comparex_last_product");
        resolve(true);
      }
    });
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = COMPAREX_STORAGE;
}
