// COMPAREX Extension Content Script

(function () {
  console.log("[COMPAREX ContentScript] Initialized on:", window.location.hostname);

  function runProductDetection() {
    const productInfo = COMPAREX_EXTRACTOR.extractProductInfo();
    if (!productInfo) {
      console.log("[COMPAREX ContentScript] No product detected on page");
      return;
    }

    console.log("[COMPAREX ContentScript] Detected product:", productInfo.title);

    COMPAREX_BUS.sendToBackground(
      COMPAREX_CONSTANTS.MESSAGE_TYPES.PRODUCT_DETECTED,
      productInfo,
      (response) => {
        if (response && response.compare) {
          COMPAREX_OVERLAY.injectOverlay(response.compare);
        }
      }
    );
  }

  // Execute after DOM renders
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setTimeout(runProductDetection, 1500));
  } else {
    setTimeout(runProductDetection, 1500);
  }

  // Listen for render events from background
  COMPAREX_BUS.onMessage((message) => {
    if (message.type === "RENDER_OVERLAY" && message.payload) {
      COMPAREX_OVERLAY.injectOverlay(message.payload);
    }
  });
})();
