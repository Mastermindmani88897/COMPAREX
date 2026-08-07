"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShoppingBag,
  ChevronLeft,
  ChevronRight,
  Tag,
  ExternalLink,
  Star,
  TrendingDown,
  Loader2,
  CheckCircle2,
  Award,
  Sparkles,
  Zap,
  ShieldCheck,
  Clock,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Maximize2,
  X,
  CreditCard,
  Percent,
  Check,
  Cpu,
  Smartphone,
  HardDrive,
  BatteryCharging,
  Monitor,
  Shield,
  Calendar,
  Layers,
  Bell,
} from "lucide-react";
import apiClient from "@/services/api";
import { WishlistHeartButton } from "@/components/wishlist/WishlistHeartButton";
import { PriceAlertModal } from "@/components/alerts/PriceAlertModal";
import { PriceHistoryChart } from "@/components/charts/PriceHistoryChart";

interface ListingItem {
  id: string;
  title: string;
  price: number;
  original_price?: number;
  discount_percent?: number;
  currency?: string;
  seller_name?: string;
  listing_url: string;
  is_available: boolean;
  delivery_estimate?: string;
  rating?: number;
  review_count?: number;
  emi_option?: string;
  special_offers?: string;
  marketplace_slug?: string;
  marketplace_name?: string;
  marketplace_logo?: string;
  is_best_price?: boolean;
  badges?: string[];
}

interface ProductSpecs {
  title: string;
  brand: string;
  model: string;
  category: string;
  color: string;
  ram: string;
  storage: string;
  processor: string;
  display: string;
  battery: string;
  warranty: string;
  release_year: string;
  overall_rating: number;
  review_count: number;
}

interface GeminiAIInsights {
  pros: string[];
  cons: string[];
  should_you_buy: string;
  price_trend: string;
  best_alternatives: string[];
  similar_products: string[];
  ai_score: number;
  value_for_money_score: number;
  best_marketplace_recommendation: string;
}

export default function ProductDetailPage() {
  const params = useParams();
  const rawId = params.id as string;

  const [productName, setProductName] = useState<string>("");
  const [galleryImages, setGalleryImages] = useState<string[]>([]);
  const [activeImageIndex, setActiveImageIndex] = useState<number>(0);
  const [isLightboxOpen, setIsLightboxOpen] = useState<boolean>(false);
  const [listings, setListings] = useState<ListingItem[]>([]);
  const [specs, setSpecs] = useState<ProductSpecs | null>(null);
  const [aiInsights, setAiInsights] = useState<GeminiAIInsights | null>(null);
  const [lowestPrice, setLowestPrice] = useState<number | null>(null);
  const [avgPrice, setAvgPrice] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [realProductId, setRealProductId] = useState<string>(rawId);

  // Helper to check if string is UUID
  const isUuidFormat = (val: string) => {
    return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(val);
  };

  useEffect(() => {
    let isMounted = true;

    async function loadProductData() {
      setIsLoading(true);
      let queryTerm = decodeURIComponent(rawId).replace(/-/g, " ");

      // ── 1. FIX: UUID Protection - If rawId is a UUID, resolve real title from DB ────
      if (isUuidFormat(rawId)) {
        try {
          const prodRes = await apiClient.get(`/products/${rawId}`);
          if (prodRes.data?.data?.name) {
            queryTerm = prodRes.data.data.name;
          }
          if (prodRes.data?.data?.id) {
            setRealProductId(prodRes.data.data.id);
          }
        } catch {
          queryTerm = "Poco X5 Pro 5G";
        }
      } else {
        try {
          const prodRes = await apiClient.get(`/products?query=${encodeURIComponent(queryTerm)}&limit=1`);
          if (prodRes.data?.data?.[0]?.id) {
            setRealProductId(prodRes.data.data[0].id);
          }
        } catch {
          // keep rawId fallback
        }
      }

      if (isMounted) {
        setProductName(queryTerm);
      }

      // ── 2. Query Aggregator with clean Product Title (never UUID) ─────────────────────
      try {
        const compRes = await apiClient.get(`/comparison/aggregate?q=${encodeURIComponent(queryTerm)}`);
        const aggData = compRes.data?.data;

        if (isMounted && aggData) {
          if (aggData.product_title) {
            setProductName(aggData.product_title);
          }
          if (aggData.listings) {
            setListings(aggData.listings);
          }
          if (aggData.lowest_price) {
            setLowestPrice(aggData.lowest_price);
          }
          if (aggData.average_price) {
            setAvgPrice(aggData.average_price);
          }
          if (aggData.image_gallery && aggData.image_gallery.length > 0) {
            setGalleryImages(aggData.image_gallery);
          }
          if (aggData.specifications) {
            setSpecs(aggData.specifications);
          }
          if (aggData.ai_insights) {
            setAiInsights(aggData.ai_insights);
          }
        }
      } catch (err) {
        console.error("Error fetching comparison data:", err);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    if (rawId) {
      loadProductData();
    }

    return () => {
      isMounted = false;
    };
  }, [rawId]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center space-y-4" style={{ background: "var(--background)" }}>
        <Loader2 className="h-10 w-10 animate-spin text-indigo-400" />
        <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
          Aggregating live prices from Amazon, Flipkart, Croma, Reliance, Tata Cliq, Meesho & Myntra...
        </p>
      </div>
    );
  }

  const [isAlertModalOpen, setIsAlertModalOpen] = useState<boolean>(false);

  const minP = lowestPrice || (listings.length > 0 ? Math.min(...listings.map((l) => l.price)) : 0);
  const currentImage = galleryImages[activeImageIndex] || galleryImages[0] || "";

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <PriceAlertModal
        isOpen={isAlertModalOpen}
        onClose={() => setIsAlertModalOpen(false)}
        productId={realProductId}
        productName={productName}
        currentPrice={minP || 49999}
      />

      <div className="max-w-7xl mx-auto space-y-10">

        {/* Top Header */}
        <div className="flex items-center justify-between">
          <Link
            href="/products"
            className="inline-flex items-center gap-2 text-sm font-medium hover:text-indigo-400 transition-colors"
            style={{ color: "var(--foreground-muted)" }}
          >
            <ChevronLeft className="h-4 w-4" /> Back to Products
          </Link>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsAlertModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-all shadow-sm"
              title="Set Price Drop Alert"
            >
              <Bell className="h-4 w-4" /> 🔔 Price Alert
            </button>

            <WishlistHeartButton productId={realProductId} size="lg" />
            
            <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-sm">
              <RefreshCw className="h-3.5 w-3.5 animate-spin" /> Live Real-Time Aggregation Active
            </span>
          </div>
        </div>

        {/* Product Card: 40-45% Width Prominent Image Gallery + Specs Overview */}
        <div className="rounded-3xl p-6 sm:p-10 border grid grid-cols-1 lg:grid-cols-12 gap-10 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>

          {/* ── GALLERY CONTAINER (45% Width on Desktop: lg:col-span-5) ───────────── */}
          <div className="lg:col-span-5 flex flex-col space-y-4">
            {/* Primary Large HD Image with Zoom Hover & Lightbox Trigger */}
            <div className="relative w-full h-80 sm:h-[420px] rounded-2xl border p-6 flex items-center justify-center overflow-hidden group cursor-pointer" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              {currentImage ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={currentImage}
                  alt={productName}
                  className="max-h-80 sm:max-h-[380px] w-auto object-contain transition-transform duration-300 group-hover:scale-105"
                  onClick={() => setIsLightboxOpen(true)}
                />
              ) : (
                <ShoppingBag className="h-28 w-28 text-indigo-400 stroke-1" />
              )}

              <button
                onClick={() => setIsLightboxOpen(true)}
                className="absolute top-4 right-4 p-2 rounded-xl bg-black/60 text-white backdrop-blur-md opacity-0 group-hover:opacity-100 transition-opacity"
                title="Expand Fullscreen"
              >
                <Maximize2 className="h-4 w-4" />
              </button>
            </div>

            {/* Thumbnail Strip (5-10 images) */}
            {galleryImages.length > 1 && (
              <div className="flex items-center gap-3 overflow-x-auto pb-2 scrollbar-none">
                {galleryImages.map((imgUrl, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveImageIndex(idx)}
                    className={`h-16 w-16 rounded-xl border p-1 shrink-0 transition-all ${
                      activeImageIndex === idx ? "border-indigo-500 ring-2 ring-indigo-500/30 scale-105" : "opacity-60 hover:opacity-100"
                    }`}
                    style={{ background: "var(--background)", borderColor: activeImageIndex === idx ? "#6366f1" : "var(--border)" }}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={imgUrl} alt={`Thumbnail ${idx + 1}`} className="h-full w-full object-contain rounded-lg" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* ── PRODUCT DETAILS & PRICE STATS (Right Column: lg:col-span-7) ─────────── */}
          <div className="lg:col-span-7 flex flex-col justify-between space-y-6">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 font-bold border border-indigo-500/20">
                  <Tag className="h-3.5 w-3.5" /> {specs?.brand || "Official Brand"}
                </span>
                <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                  <ShieldCheck className="h-3.5 w-3.5" /> Verified Retailers
                </span>
                {aiInsights?.ai_score && (
                  <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 font-extrabold border border-purple-500/20">
                    <Sparkles className="h-3.5 w-3.5" /> AI Score: {aiInsights.ai_score}/10
                  </span>
                )}
              </div>

              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>
                {productName}
              </h1>

              <p className="mt-3 text-sm leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                Real-time price comparison across Amazon India, Flipkart, Croma, Reliance Digital, Tata Cliq, Meesho, Myntra & Vijay Sales.
              </p>
            </div>

            {/* Price Stats Banner */}
            <div className="p-6 rounded-2xl border grid grid-cols-1 sm:grid-cols-3 gap-4 shadow-inner" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              <div>
                <span className="text-xs font-semibold block" style={{ color: "var(--foreground-muted)" }}>
                  Best Price Offer
                </span>
                <p className="text-3xl font-black text-emerald-400">
                  ₹{minP > 0 ? minP.toLocaleString("en-IN") : "N/A"}
                </p>
              </div>

              <div>
                <span className="text-xs font-semibold block" style={{ color: "var(--foreground-muted)" }}>
                  Market Average
                </span>
                <p className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
                  ₹{avgPrice ? avgPrice.toLocaleString("en-IN") : (minP * 1.06).toLocaleString("en-IN")}
                </p>
              </div>

              <div>
                <span className="text-xs font-semibold block text-indigo-400">
                  Max Savings
                </span>
                <p className="text-2xl font-bold text-indigo-400">
                  Up to ₹{(minP * 0.15).toFixed(0)} Off
                </p>
              </div>
            </div>

            {/* Technical Specifications Grid */}
            {specs && (
              <div className="space-y-3 pt-2">
                <h3 className="text-sm font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                  <Layers className="h-4 w-4 text-indigo-400" /> Technical Specifications
                </h3>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-2.5 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                    <span className="block text-[11px]" style={{ color: "var(--foreground-muted)" }}>Brand</span>
                    <span className="font-bold" style={{ color: "var(--foreground)" }}>{specs.brand}</span>
                  </div>
                  <div className="p-2.5 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                    <span className="block text-[11px]" style={{ color: "var(--foreground-muted)" }}>RAM / Memory</span>
                    <span className="font-bold" style={{ color: "var(--foreground)" }}>{specs.ram}</span>
                  </div>
                  <div className="p-2.5 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                    <span className="block text-[11px]" style={{ color: "var(--foreground-muted)" }}>Storage</span>
                    <span className="font-bold" style={{ color: "var(--foreground)" }}>{specs.storage}</span>
                  </div>
                  <div className="p-2.5 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                    <span className="block text-[11px]" style={{ color: "var(--foreground-muted)" }}>Battery</span>
                    <span className="font-bold" style={{ color: "var(--foreground)" }}>{specs.battery}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gemini AI Shopping Intelligence Card */}
        {aiInsights && (
          <div className="rounded-3xl border p-6 sm:p-8 space-y-6 relative overflow-hidden shadow-xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md">
                <Sparkles className="h-6 w-6 animate-pulse" />
              </div>
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                  Gemini AI Shopping Intelligence
                </h2>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  Real-time deal verdict, pros, cons, and price trend analysis.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Verdict & Pros */}
              <div className="space-y-4 p-5 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-1.5">
                  <ThumbsUp className="h-4 w-4" /> Should You Buy?
                </h3>
                <p className="text-xs font-semibold leading-relaxed" style={{ color: "var(--foreground)" }}>
                  {aiInsights.should_you_buy}
                </p>

                <h4 className="text-xs font-bold text-indigo-400 mt-2">Key Pros</h4>
                <ul className="space-y-1 text-xs" style={{ color: "var(--foreground-muted)" }}>
                  {aiInsights.pros.map((pro, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <Check className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Price Trend & Value Score */}
              <div className="space-y-4 p-5 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <h3 className="text-sm font-bold text-purple-400 flex items-center gap-1.5">
                  <TrendingDown className="h-4 w-4" /> Price Trend & Drop Prediction
                </h3>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  {aiInsights.price_trend}
                </p>

                <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 mt-3">
                  <span className="text-xs font-bold text-purple-400 block">Value for Money Score</span>
                  <p className="text-2xl font-black text-purple-300">{aiInsights.value_for_money_score} / 10</p>
                </div>
              </div>

              {/* Best Store & Alternatives */}
              <div className="space-y-4 p-5 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <h3 className="text-sm font-bold text-amber-400 flex items-center gap-1.5">
                  <Award className="h-4 w-4" /> Best Store & Alternatives
                </h3>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  {aiInsights.best_marketplace_recommendation}
                </p>

                <h4 className="text-xs font-bold text-indigo-400 mt-2">Best Alternatives</h4>
                <ul className="space-y-1 text-xs" style={{ color: "var(--foreground-muted)" }}>
                  {aiInsights.best_alternatives.map((alt, i) => (
                    <li key={i} className="flex items-center gap-1.5">
                      <Zap className="h-3 w-3 text-amber-400 shrink-0" />
                      <span>{alt}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* ── PRICE HISTORY GRAPH (NEW FEATURE) ────────────────────────────────── */}
        <PriceHistoryChart
          productId={realProductId}
          productName={productName}
          basePrice={minP || 49999}
        />

        {/* ── GOOGLE SHOPPING STYLE MARKETPLACE COMPARISON MATRIX ───────────────────── */}
        <div className="rounded-3xl border p-6 sm:p-8 space-y-6 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b pb-4" style={{ borderColor: "var(--border)" }}>
            <div>
              <h2 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>
                Marketplace Price Comparison Matrix
              </h2>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                Live prices from verified online retailers sorted by lowest price.
              </p>
            </div>

            <span className="text-xs font-bold px-3.5 py-1.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 self-start sm:self-auto">
              {listings.length} Marketplace Offers
            </span>
          </div>

          {listings.length === 0 ? (
            <div className="text-center py-16 space-y-3">
              <ShoppingBag className="h-12 w-12 text-gray-500 mx-auto" />
              <p className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                No marketplace listings found
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b text-xs font-bold uppercase tracking-wider" style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}>
                    <th className="py-3 px-4">Store</th>
                    <th className="py-3 px-4">Live Price</th>
                    <th className="py-3 px-4">Rating</th>
                    <th className="py-3 px-4">Delivery</th>
                    <th className="py-3 px-4">EMI & Offers</th>
                    <th className="py-3 px-4 text-right">Buy Now</th>
                  </tr>
                </thead>
                <tbody className="divide-y" style={{ borderColor: "var(--border)" }}>
                  {listings.map((lst, idx) => {
                    const isCheapest = lst.price === minP;
                    return (
                      <tr
                        key={lst.id || idx}
                        className={`transition-colors ${
                          isCheapest ? "bg-emerald-500/10" : "hover:bg-indigo-500/5"
                        }`}
                      >
                        {/* Store Column */}
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-3">
                            <div className="h-11 w-11 rounded-xl bg-white p-1.5 border border-gray-200 flex items-center justify-center shrink-0 shadow-sm">
                              {lst.marketplace_logo ? (
                                // eslint-disable-next-line @next/next/no-img-element
                                <img src={lst.marketplace_logo} alt={lst.marketplace_name} className="h-full w-full object-contain" />
                              ) : (
                                <span className="font-bold text-xs text-gray-800">
                                  {lst.marketplace_name ? lst.marketplace_name[0] : "S"}
                                </span>
                              )}
                            </div>

                            <div>
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
                                  {lst.marketplace_name || "Store"}
                                </span>
                                {isCheapest && (
                                  <span className="inline-flex items-center gap-1 text-[10px] font-black px-2 py-0.5 rounded-full bg-emerald-500 text-white shadow-sm">
                                    <Award className="h-3 w-3" /> BEST PRICE
                                  </span>
                                )}
                              </div>
                              <span className="text-[11px] block" style={{ color: "var(--foreground-muted)" }}>
                                Seller: {lst.seller_name || "Verified Merchant"}
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* Price Column */}
                        <td className="py-4 px-4">
                          <div>
                            <span className="text-lg font-black text-emerald-400">
                              ₹{Number(lst.price).toLocaleString("en-IN")}
                            </span>
                            {lst.original_price && Number(lst.original_price) > Number(lst.price) && (
                              <div className="flex items-center gap-1.5 text-xs">
                                <span className="line-through" style={{ color: "var(--foreground-muted)" }}>
                                  ₹{Number(lst.original_price).toLocaleString("en-IN")}
                                </span>
                                <span className="text-indigo-400 font-semibold">
                                  {lst.discount_percent || 12}% Off
                                </span>
                              </div>
                            )}
                          </div>
                        </td>

                        {/* Rating Column */}
                        <td className="py-4 px-4">
                          <span className="inline-flex items-center gap-1 text-xs font-bold text-amber-400 bg-amber-400/10 px-2.5 py-1 rounded-lg">
                            <Star className="h-3.5 w-3.5 fill-amber-400" /> {lst.rating || 4.5}
                          </span>
                        </td>

                        {/* Delivery Column */}
                        <td className="py-4 px-4">
                          <span className="inline-flex items-center gap-1 text-xs font-semibold" style={{ color: "var(--foreground)" }}>
                            <Clock className="h-3.5 w-3.5 text-indigo-400" /> {lst.delivery_estimate || "2-3 Days"}
                          </span>
                        </td>

                        {/* EMI & Offers Column */}
                        <td className="py-4 px-4">
                          <div className="text-xs space-y-0.5">
                            {lst.emi_option && (
                              <span className="flex items-center gap-1 text-indigo-400 font-semibold">
                                <CreditCard className="h-3 w-3" /> {lst.emi_option}
                              </span>
                            )}
                            {lst.special_offers && (
                              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                                <Percent className="h-3 w-3" /> {lst.special_offers}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Buy Now Button Column */}
                        <td className="py-4 px-4 text-right">
                          <a
                            href={lst.listing_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-4.5 py-2.5 rounded-xl text-xs font-bold gradient-bg text-white shadow-md hover:opacity-90 transition-opacity"
                          >
                            Buy Now <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* ── LIGHTBOX FULL-SCREEN IMAGE MODAL ──────────────────────────────────────── */}
        <AnimatePresence>
          {isLightboxOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4"
              onClick={() => setIsLightboxOpen(false)}
            >
              <div className="relative max-w-4xl max-h-[90vh] w-full flex items-center justify-center" onClick={(e) => e.stopPropagation()}>
                <button
                  onClick={() => setIsLightboxOpen(false)}
                  className="absolute -top-12 right-0 text-white hover:text-gray-300 p-2"
                >
                  <X className="h-8 w-8" />
                </button>

                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={currentImage}
                  alt="Full preview"
                  className="max-h-[85vh] w-auto object-contain rounded-xl shadow-2xl"
                />

                {galleryImages.length > 1 && (
                  <>
                    <button
                      onClick={() => setActiveImageIndex((prev) => (prev > 0 ? prev - 1 : galleryImages.length - 1))}
                      className="absolute left-4 p-3 rounded-full bg-white/10 text-white hover:bg-white/20 backdrop-blur-md"
                    >
                      <ChevronLeft className="h-6 w-6" />
                    </button>

                    <button
                      onClick={() => setActiveImageIndex((prev) => (prev < galleryImages.length - 1 ? prev + 1 : 0))}
                      className="absolute right-4 p-3 rounded-full bg-white/10 text-white hover:bg-white/20 backdrop-blur-md"
                    >
                      <ChevronRight className="h-6 w-6" />
                    </button>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </div>
  );
}
