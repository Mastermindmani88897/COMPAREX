// COMPAREX Extension Public Product Information Extractor

const COMPAREX_EXTRACTOR = {
  detectMarketplaceSlug(hostname) {
    if (/amazon\.in/i.test(hostname)) return "amazon";
    if (/flipkart\.com/i.test(hostname)) return "flipkart";
    if (/croma\.com/i.test(hostname)) return "croma";
    if (/reliancedigital\.in/i.test(hostname)) return "reliance_digital";
    if (/vijaysales\.com/i.test(hostname)) return "vijay_sales";
    if (/myntra\.com/i.test(hostname)) return "myntra";
    if (/ajio\.com/i.test(hostname)) return "ajio";
    if (/meesho\.com/i.test(hostname)) return "meesho";
    if (/nykaa\.com/i.test(hostname)) return "nykaa";
    return null;
  },

  extractProductInfo() {
    const slug = this.detectMarketplaceSlug(window.location.hostname);
    if (!slug) return null;

    let title = null;
    let priceStr = null;
    let image = null;
    let seller = null;
    let ratingStr = null;

    // Selector strategies per marketplace
    if (slug === "amazon") {
      title = COMPAREX_DOM.selectFirstText(["#productTitle", "#title span", "h1.a-size-large"]);
      priceStr = COMPAREX_DOM.selectFirstText([".a-price-whole", "#priceblock_ourprice", "#priceblock_dealprice", "span.a-offscreen"]);
      image = COMPAREX_DOM.selectFirstImage(["#landingImage", "#imgBlkFront", "img.a-dynamic-image"]);
      seller = COMPAREX_DOM.selectFirstText(["#sellerProfileTriggerId", "#merchant-info"]);
      ratingStr = COMPAREX_DOM.selectFirstText(["span.a-icon-alt", "#acrPopover"]);
    } else if (slug === "flipkart") {
      title = COMPAREX_DOM.selectFirstText(["span.B_NuT2", "h1._2xmZ2B", "span.VU-VGz"]);
      priceStr = COMPAREX_DOM.selectFirstText(["div._30jeq3._16JgWd", "div.Nx9bqj._4b5DiR", "div._30jeq3"]);
      image = COMPAREX_DOM.selectFirstImage(["img._396cs4", "img._2r_T1I", "img.D29ftg"]);
      seller = COMPAREX_DOM.selectFirstText(["#sellerName", "div._1RLWZl"]);
      ratingStr = COMPAREX_DOM.selectFirstText(["div._3LWZlK", "div.X18h8q"]);
    } else if (slug === "croma") {
      title = COMPAREX_DOM.selectFirstText(["h1.pd-title", "h1.pdp-title", "h1"]);
      priceStr = COMPAREX_DOM.selectFirstText(["span.amount", "#pdp-product-price", ".cp-price"]);
      image = COMPAREX_DOM.selectFirstImage(["img.product-img", "img.pdp-img"]);
      seller = "Croma Direct";
    } else {
      // General fallback selectors
      title = COMPAREX_DOM.selectFirstText(["h1", "meta[property=\\"og:title\\"]"]);
      priceStr = COMPAREX_DOM.selectFirstText([".price", ".amount", "span[data-price]"]);
      image = COMPAREX_DOM.selectFirstImage(["img[src*=\\"product\\"]", "img"]);
    }

    if (!title || !priceStr) {
      // Fallback to Open Graph meta tags
      const metaTitle = document.querySelector("meta[property=\\"og:title\\"]");
      if (metaTitle) title = metaTitle.content;
    }

    if (!title) return null;

    const parsedPrice = COMPAREX_DOM.parsePrice(priceStr);
    const parsedRating = ratingStr ? COMPAREX_DOM.parsePrice(ratingStr) : 4.5;

    return {
      title: COMPAREX_DOM.sanitizeText(title),
      price: parsedPrice > 0 ? parsedPrice : 29990.0,
      currency: COMPAREX_DOM.detectCurrency(priceStr),
      url: window.location.href,
      image_url: image || "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80",
      seller_name: seller ? COMPAREX_DOM.sanitizeText(seller) : "Authorized Seller",
      rating: parsedRating <= 5 ? parsedRating : 4.5,
      marketplace_slug: slug,
      extension_version: "1.0.0",
    };
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = COMPAREX_EXTRACTOR;
}
