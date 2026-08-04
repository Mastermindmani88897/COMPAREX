// COMPAREX Extension Floating Overlay Controller

const COMPAREX_OVERLAY = {
  isMinimized: false,
  rootElement: null,

  injectOverlay(compareData) {
    if (document.getElementById("comparex-overlay-root")) {
      this.updateData(compareData);
      return;
    }

    const root = document.createElement("div");
    root.id = "comparex-overlay-root";

    const card = document.createElement("div");
    card.id = "comparex-overlay-card";

    const savingsPotential = compareData ? compareData.savings_potential : 0;
    const isBestPrice = compareData ? compareData.is_best_price_here : true;
    const matrix = compareData ? compareData.comparison_matrix : null;
    const topOffers = matrix && matrix.listings ? matrix.listings.slice(0, 2) : [];

    card.innerHTML = `
      <div id="comparex-overlay-header">
        <div class="cx-title">
          <span>⚡ COMPAREX Assistant</span>
        </div>
        <div class="cx-controls">
          <button class="cx-btn-icon" id="cx-min-btn">−</button>
          <button class="cx-btn-icon" id="cx-close-btn">×</button>
        </div>
      </div>
      <div id="comparex-overlay-body">
        ${
          savingsPotential > 0
            ? `<div class="cx-savings-banner">
                <span>💰 Potential Savings</span>
                <span>Save ₹${savingsPotential.toLocaleString("en-IN")}</span>
               </div>`
            : isBestPrice
            ? `<div class="cx-savings-banner" style="background:rgba(59,130,246,0.15); border-color:rgba(59,130,246,0.4); color:#60a5fa;">
                <span>✨ Best Price Guaranteed</span>
                <span>Lowest here!</span>
               </div>`
            : ""
        }

        ${
          topOffers.length > 0
            ? topOffers
                .map(
                  (off) => `
              <div class="cx-offer-item">
                <div>
                  <span class="cx-offer-store">${off.marketplace_name}</span>
                  <div style="font-size:10px; color:#9ca3af;">${off.delivery_estimate || "In Stock"}</div>
                </div>
                <div class="cx-offer-price">₹${off.price.toLocaleString("en-IN")}</div>
              </div>
            `
                )
                .join("")
            : `<div style="font-size:12px; color:#9ca3af;">Analyzing live price matrix across 9 stores...</div>`
        }

        <a href="http://localhost:3000/compare" target="_blank" class="cx-action-btn">
          View Full Price Matrix
        </a>
      </div>
    `;

    root.appendChild(card);
    document.body.appendChild(root);
    this.rootElement = root;

    // Attach control event listeners
    const minBtn = card.querySelector("#cx-min-btn");
    const closeBtn = card.querySelector("#cx-close-btn");
    const body = card.querySelector("#comparex-overlay-body");

    if (minBtn) {
      minBtn.addEventListener("click", () => {
        this.isMinimized = !this.isMinimized;
        card.classList.toggle("minimized", this.isMinimized);
        body.style.display = this.isMinimized ? "none" : "flex";
        minBtn.textContent = this.isMinimized ? "+" : "−";
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        root.remove();
      });
    }
  },

  updateData(compareData) {
    if (this.rootElement) {
      this.rootElement.remove();
      this.injectOverlay(compareData);
    }
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = COMPAREX_OVERLAY;
}
