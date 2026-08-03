export const siteConfig = {
  name: "COMPAREX",
  tagline: "AI Shopping Intelligence Platform",
  description:
    "COMPAREX uses AI to compare products across multiple marketplaces, find the best deals, and give you personalized shopping insights — all in one place.",
  url: "https://comparex.io",
  ogImage: "https://comparex.io/og.png",
  links: {
    github: "https://github.com/Mastermindmani88897/COMPAREX",
    twitter: "https://twitter.com/comparex_io",
    linkedin: "https://linkedin.com/company/comparex",
  },
  nav: [
    { label: "Home", href: "/" },
    { label: "About", href: "/about" },
    { label: "Contact", href: "/contact" },
  ],
  features: [
    {
      id: "smart-comparison",
      title: "Smart Product Comparison",
      description:
        "Compare products side-by-side across Amazon, Flipkart, and 10+ marketplaces with real-time data.",
      icon: "BarChart3",
      color: "from-violet-500 to-purple-600",
    },
    {
      id: "ai-assistant",
      title: "AI Shopping Assistant",
      description:
        "Chat with our AI to get personalized product recommendations based on your needs and budget.",
      icon: "Bot",
      color: "from-blue-500 to-cyan-600",
    },
    {
      id: "image-search",
      title: "Image Search",
      description:
        "Upload a photo of any product and instantly find it across all supported marketplaces.",
      icon: "Camera",
      color: "from-emerald-500 to-teal-600",
    },
    {
      id: "price-alerts",
      title: "Price Alerts",
      description:
        "Set your target price and get instant notifications when products drop to your desired amount.",
      icon: "Bell",
      color: "from-orange-500 to-amber-600",
    },
    {
      id: "personalized-shopping",
      title: "Personalized Shopping",
      description:
        "AI-powered recommendations that learn from your preferences to surface products you'll love.",
      icon: "Sparkles",
      color: "from-pink-500 to-rose-600",
    },
    {
      id: "browser-extension",
      title: "Browser Extension",
      description:
        "Shop anywhere on the web and get instant price comparisons and deal alerts from your browser.",
      icon: "Globe2",
      color: "from-indigo-500 to-violet-600",
    },
  ],
};

export type SiteConfig = typeof siteConfig;
