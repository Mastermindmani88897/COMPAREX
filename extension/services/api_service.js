// COMPAREX Extension API Client Service

const COMPAREX_API = {
  async getStatus() {
    try {
      const res = await fetch(`${COMPAREX_CONSTANTS.API_BASE_URL}/extension/status`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (err) {
      console.warn("[COMPAREX API] Status error:", err.message);
      return { status: "offline", error: err.message };
    }
  },

  async checkVersion(clientVersion = "1.0.0") {
    try {
      const res = await fetch(`${COMPAREX_CONSTANTS.API_BASE_URL}/extension/version?v=${clientVersion}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (err) {
      return { is_compatible: true, error: err.message };
    }
  },

  async ingestProduct(productPayload) {
    try {
      const res = await fetch(`${COMPAREX_CONSTANTS.API_BASE_URL}/extension/product`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(productPayload),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (err) {
      console.warn("[COMPAREX API] Ingest product error:", err.message);
      return null;
    }
  },

  async quickCompare(productTitle, category = null) {
    try {
      const res = await fetch(`${COMPAREX_CONSTANTS.API_BASE_URL}/extension/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_title: productTitle, category }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (err) {
      console.warn("[COMPAREX API] Quick compare error:", err.message);
      return null;
    }
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = COMPAREX_API;
}
