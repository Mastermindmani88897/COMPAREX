// COMPAREX Extension Popup Controller

document.addEventListener("DOMContentLoaded", () => {
  const statusBadge = document.getElementById("status-badge");
  const statusText = document.getElementById("status-text");
  const productTitle = document.getElementById("product-title");
  const productPrice = document.getElementById("product-price");
  const marketplaceName = document.getElementById("marketplace-name");
  const priceRow = document.getElementById("price-row");
  const savingsCard = document.getElementById("savings-card");
  const savingsAmount = document.getElementById("savings-amount");
  const quickCompareBtn = document.getElementById("quick-compare-btn");
  const openOptionsBtn = document.getElementById("open-options");

  // Query background status
  COMPAREX_BUS.sendToBackground(COMPAREX_CONSTANTS.MESSAGE_TYPES.GET_STATUS, {}, (response) => {
    if (response) {
      if (response.isOnline) {
        statusText.textContent = "Online";
        statusBadge.classList.remove("offline");
      } else {
        statusText.textContent = "Offline";
        statusBadge.classList.add("offline");
      }

      if (response.currentProduct) {
        const prod = response.currentProduct;
        productTitle.textContent = prod.title;
        productPrice.textContent = `₹${prod.price.toLocaleString("en-IN")}`;
        marketplaceName.textContent = prod.marketplace_slug.toUpperCase();
        priceRow.style.display = "flex";
      }

      if (response.lastCompare && response.lastCompare.savings_potential > 0) {
        savingsAmount.textContent = `Save ₹${response.lastCompare.savings_potential.toLocaleString("en-IN")}`;
        savingsCard.style.display = "flex";
      }
    }
  });

  if (quickCompareBtn) {
    quickCompareBtn.addEventListener("click", () => {
      window.open("http://localhost:3000/compare", "_blank");
    });
  }

  if (openOptionsBtn) {
    openOptionsBtn.addEventListener("click", (e) => {
      e.preventDefault();
      if (chrome.runtime.openOptionsPage) {
        chrome.runtime.openOptionsPage();
      } else {
        window.open("../options/options.html");
      }
    });
  }
});
