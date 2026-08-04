// COMPAREX Extension Constants

const COMPAREX_CONSTANTS = {
  API_BASE_URL: "http://localhost:8000/api/v1",
  VERSION: "1.0.0",
  DEFAULT_SETTINGS: {
    theme: "dark",
    language: "en",
    overlayPosition: "bottom-right",
    enableOverlay: true,
    enabledMarketplaces: [
      "amazon",
      "flipkart",
      "croma",
      "reliance_digital",
      "vijay_sales",
      "myntra",
      "ajio",
      "meesho",
      "nykaa"
    ],
    debugMode: false,
  },
  MESSAGE_TYPES: {
    PRODUCT_DETECTED: "PRODUCT_DETECTED",
    QUERY_COMPARE: "QUERY_COMPARE",
    GET_STATUS: "GET_STATUS",
    GET_SETTINGS: "GET_SETTINGS",
    SAVE_SETTINGS: "SAVE_SETTINGS",
    TOGGLE_OVERLAY: "TOGGLE_OVERLAY",
    HEARTBEAT: "HEARTBEAT"
  },
  MARKETPLACE_PATTERNS: {
    amazon: /amazon\.in/i,
    flipkart: /flipkart\.com/i,
    croma: /croma\.com/i,
    reliance_digital: /reliancedigital\.in/i,
    vijay_sales: /vijaysales\.com/i,
    myntra: /myntra\.com/i,
    ajio: /ajio\.com/i,
    meesho: /meesho\.com/i,
    nykaa: /nykaa\.com/i,
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = COMPAREX_CONSTANTS;
}
