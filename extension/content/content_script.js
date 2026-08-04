// COMPAREX Extension 2.0 Content Script with SPA Route Mutation Detection

(function () {
  console.log("[COMPAREX ContentScript 2.0] Active on:", window.location.hostname);
  let lastUrl = location.href;

  function runProductDetection() {
    if (typeof COMPAREX_EXTRACTOR === "undefined") return;
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

  // Observe SPA route changes
  const observer = new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      console.log("[COMPAREX ContentScript] SPA Route Change Detected:", lastUrl);
      setTimeout(runProductDetection, 1200);
    }
  });

  observer.observe(document.body, { childList: true, subtree: true });

  // Initial execution
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setTimeout(runProductDetection, 1200));
  } else {
    setTimeout(runProductDetection, 1200);
  }

  COMPAREX_BUS.onMessage((message) => {
    if (message.type === "RENDER_OVERLAY" && message.payload) {
      COMPAREX_OVERLAY.injectOverlay(message.payload);
    }
  });
})();
