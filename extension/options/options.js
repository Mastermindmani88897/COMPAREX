// COMPAREX Extension Options Controller

document.addEventListener("DOMContentLoaded", async () => {
  const themeSelect = document.getElementById("theme-select");
  const overlayPos = document.getElementById("overlay-position");
  const enableOverlay = document.getElementById("enable-overlay");
  const debugMode = document.getElementById("debug-mode");
  const mpGrid = document.getElementById("marketplace-grid");
  const saveBtn = document.getElementById("save-btn");
  const clearCacheBtn = document.getElementById("clear-cache-btn");
  const saveMsg = document.getElementById("save-msg");

  const settings = await COMPAREX_STORAGE.getSettings();

  themeSelect.value = settings.theme || "dark";
  overlayPos.value = settings.overlayPosition || "bottom-right";
  enableOverlay.checked = settings.enableOverlay !== false;
  debugMode.checked = !!settings.debugMode;

  const ALL_MARKETPLACES = [
    { slug: "amazon", name: "Amazon India" },
    { slug: "flipkart", name: "Flipkart" },
    { slug: "croma", name: "Croma" },
    { slug: "reliance_digital", name: "Reliance Digital" },
    { slug: "vijay_sales", name: "Vijay Sales" },
    { slug: "myntra", name: "Myntra" },
    { slug: "ajio", name: "Ajio" },
    { slug: "meesho", name: "Meesho" },
    { slug: "nykaa", name: "Nykaa" }
  ];

  mpGrid.innerHTML = ALL_MARKETPLACES.map((mp) => {
    const isChecked = settings.enabledMarketplaces?.includes(mp.slug) !== false;
    return `
      <label class="mp-toggle">
        <input type="checkbox" value="${mp.slug}" ${isChecked ? "checked" : ""}>
        ${mp.name}
      </label>
    `;
  }).join("");

  saveBtn.addEventListener("click", async () => {
    const selectedMps = Array.from(mpGrid.querySelectorAll("input:checked")).map((cb) => cb.value);

    const updatedSettings = {
      theme: themeSelect.value,
      language: "en",
      overlayPosition: overlayPos.value,
      enableOverlay: enableOverlay.checked,
      enabledMarketplaces: selectedMps,
      debugMode: debugMode.checked,
    };

    await COMPAREX_STORAGE.setSettings(updatedSettings);
    saveMsg.textContent = "Settings saved successfully!";
    setTimeout(() => {
      saveMsg.textContent = "";
    }, 3000);
  });

  clearCacheBtn.addEventListener("click", async () => {
    await COMPAREX_STORAGE.clearCache();
    alert("Extension cache cleared!");
  });
});
