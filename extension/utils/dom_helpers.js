// COMPAREX Extension DOM Helper Utilities

const COMPAREX_DOM = {
  sanitizeText(str) {
    if (!str) return "";
    return str.replace(/\s+/g, " ").trim();
  },

  parsePrice(priceStr) {
    if (!priceStr) return 0;
    const clean = priceStr.replace(/[^\d.]/g, "");
    return parseFloat(clean) || 0;
  },

  detectCurrency(priceStr) {
    if (!priceStr) return "INR";
    if (priceStr.includes("$")) return "USD";
    if (priceStr.includes("€")) return "EUR";
    if (priceStr.includes("£")) return "GBP";
    return "INR";
  },

  selectFirstText(selectors) {
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.textContent) {
        const text = this.sanitizeText(el.textContent);
        if (text.length > 0) return text;
      }
    }
    return null;
  },

  selectFirstImage(selectors) {
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) {
        const src = el.getAttribute("src") || el.getAttribute("data-src");
        if (src && src.startsWith("http")) return src;
      }
    }
    return null;
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = COMPAREX_DOM;
}
