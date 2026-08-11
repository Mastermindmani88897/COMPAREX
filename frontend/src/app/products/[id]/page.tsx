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
  Award,
  Sparkles,
  Zap,
  ShieldCheck,
  Clock,
  ThumbsUp,
  RefreshCw,
  Maximize2,
  X,
  CreditCard,
  Percent,
  Check,
  Layers,
  Bell,
  AlertCircle,
  PackageX,
  CheckCircle2,
  Search,
} from "lucide-react";
import apiClient from "@/services/api";
import { WishlistHeartButton } from "@/components/wishlist/WishlistHeartButton";
import { PriceAlertModal } from "@/components/alerts/PriceAlertModal";
import { PriceHistoryChart } from "@/components/charts/PriceHistoryChart";

interface ListingItem {
  id?: string;
  title?: string;
  price: number;
  original_price?: number;
  discount_percent?: number;
  currency?: string;
  seller_name?: string;
  listing_url: string;
  is_available?: boolean;
  delivery_estimate?: string;
  rating?: number;
  review_count?: number;
  emi_option?: string;
  special_offers?: string;
  marketplace_slug?: string;
  marketplace_name?: string;
  marketplace_logo?: string;
  is_best_price?: boolean;
  verification_status?: string;
  match_score?: number;
  is_exact_url?: boolean;
  retrieved_at?: string;
  is_outlier?: boolean;
  outlier_reason?: string;
}

interface MajorMarketplaceStatusItem {
  slug: string;
  name: string;
  logo_url?: string;
  priority: number;
  status: "verified" | "unavailable" | "not_checked";
  title?: string | null;
  price: number | null;
  original_price?: number | null;
  discount_percent?: number | null;
  currency?: string;
  listing_url: string;
  search_url: string;
  image_url?: string | null;
  is_exact_url?: boolean;
  seller_name?: string | null;
  delivery_estimate?: string | null;
  rating?: number | null;
  review_count?: number | null;
  is_available?: boolean | null;
  match_score?: number | null;
  last_checked?: string;
  has_verified_price: boolean;
  unavailable_reason?: string;
}


interface ProductSpecs {
  brand?: string;
  model?: string;
  category?: string;
  color?: string;
  ram?: string;
  storage?: string;
  processor?: string;
  display?: string;
  battery?: string;
  warranty?: string;
  release_year?: string;
  overall_rating?: number;
  review_count?: number;
}

interface GeminiAIInsights {
  pros?: string[];
  cons?: string[];
  should_you_buy?: string;
  price_trend?: string;
  best_alternatives?: string[];
  similar_products?: string[];
  ai_score?: number;
  value_for_money_score?: number;
  best_marketplace_recommendation?: string;
}

interface ProductData {
  id: string;
  name: string;
  description?: string;
  category?: string;
  brand?: string;
  base_price?: number;
  rating?: number;
  review_count?: number;
  image_url?: string;
  ean?: string;
  stock_status?: string;
  discount_percentage?: number;
  is_quarantined?: boolean;
  images?: Array<{ url: string; is_primary?: boolean }>;
  listings?: ListingItem[];
}

export default function ProductDetailPage() {
  const params = useParams();
  const rawId = typeof params?.id === "string" ? params.id : Array.isArray(params?.id) ? params.id[0] : "";

  const [product, setProduct] = useState<ProductData | null>(null);
  const [galleryImages, setGalleryImages] = useState<string[]>([]);
  const [activeImageIndex, setActiveImageIndex] = useState<number>(0);
  const [isLightboxOpen, setIsLightboxOpen] = useState<boolean>(false);
  const [listings, setListings] = useState<ListingItem[]>([]);
  const [specs, setSpecs] = useState<ProductSpecs | null>(null);
  const [aiInsights, setAiInsights] = useState<GeminiAIInsights | null>(null);
  const [lowestPrice, setLowestPrice] = useState<number | null>(null);
  const [avgPrice, setAvgPrice] = useState<number | null>(null);

  // Major marketplace always-visible status layer
  const [majorMarketplaceStatus, setMajorMarketplaceStatus] = useState<MajorMarketplaceStatusItem[]>([]);
  const [verifiedMarketplaceCount, setVerifiedMarketplaceCount] = useState<number>(0);
  const [dataQuality, setDataQuality] = useState<string>("unavailable");
  const [marketplaceCoverage, setMarketplaceCoverage] = useState<string>("0/7 verified");
  const [lastChecked, setLastChecked] = useState<string | null>(null);

  // Refresh state
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [refreshCooldown, setRefreshCooldown] = useState<boolean>(false);
  const [refreshCooldownSeconds, setRefreshCooldownSeconds] = useState<number>(0);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [notFound, setNotFound] = useState<boolean>(false);
  const [hasError, setHasError] = useState<boolean>(false);
  const [isAlertModalOpen, setIsAlertModalOpen] = useState<boolean>(false);


  useEffect(() => {
    let isMounted = true;

    async function loadProductData() {
      if (!rawId) {
        setIsLoading(false);
        setNotFound(true);
        return;
      }

      setIsLoading(true);
      setNotFound(false);
      setHasError(false);

      try {
        // ── 1. PRIMARY FETCH: Canonical Product from backend API ─────────────────
        const prodRes = await apiClient.get(`/products/${rawId}`);
        const pData: ProductData = prodRes.data?.data;

        if (!pData || pData.is_quarantined) {
          if (isMounted) {
            setNotFound(true);
            setIsLoading(false);
          }
          return;
        }

        if (isMounted) {
          setProduct(pData);

          // Build gallery images array
          const imgs: string[] = [];
          if (pData.images && pData.images.length > 0) {
            pData.images.forEach((img) => {
              if (img.url && !imgs.includes(img.url)) imgs.push(img.url);
            });
          }
          if (pData.image_url && !imgs.includes(pData.image_url)) {
            imgs.unshift(pData.image_url);
          }
          if (imgs.length === 0) {
            imgs.push("https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80");
          }
          setGalleryImages(imgs);

          // Build initial listings from DB (filter only verified entries)
          const dbListings = pData.listings || [];
          const verifiedDbListings = dbListings.filter(
            (lst) => lst.verification_status !== "unverified" && lst.is_exact_url !== false
          );
          setListings(verifiedDbListings);

          if (verifiedDbListings.length > 0) {
            const prices = verifiedDbListings.map((l) => Number(l.price)).filter((p) => p > 0);
            if (prices.length > 0) {
              const minVal = Math.min(...prices);
              const avgVal = Math.round(prices.reduce((a, b) => a + b, 0) / prices.length);
              setLowestPrice(minVal);
              setAvgPrice(avgVal);
            } else {
              setLowestPrice(null);
              setAvgPrice(null);
            }
          } else {
            setLowestPrice(null);
            setAvgPrice(null);
          }

          setSpecs({
            brand: pData.brand || "Official Brand",
            category: pData.category || "Electronics",
            overall_rating: pData.rating || 4.5,
            review_count: pData.review_count || 0,
          });
        }

        // ── 2. BACKGROUND ENRICHMENT: Async live marketplace aggregation ─────────
        try {
          // Pass both product name AND product_id for accurate resolution
          const aggUrl = `/comparison/aggregate?q=${encodeURIComponent(pData.name)}&product_id=${encodeURIComponent(pData.id)}`;
          const compRes = await apiClient.get(aggUrl);
          const aggData = compRes.data?.data;

          if (isMounted && aggData) {
            // Always update the major marketplace status layer (always visible)
            if (aggData.major_marketplace_status && aggData.major_marketplace_status.length > 0) {
              setMajorMarketplaceStatus(aggData.major_marketplace_status);
            }
            if (typeof aggData.verified_marketplace_count === "number") {
              setVerifiedMarketplaceCount(aggData.verified_marketplace_count);
            }
            if (aggData.data_quality) setDataQuality(aggData.data_quality);
            if (aggData.marketplace_coverage) setMarketplaceCoverage(aggData.marketplace_coverage);
            if (aggData.last_checked) setLastChecked(aggData.last_checked);

            // Only update listings if verified ones were returned
            if (aggData.listings && aggData.listings.length > 0) {
              setListings(aggData.listings);
              // Price stats: only from non-outlier verified prices
              const nonOutlierPrices = aggData.listings
                .filter((l: ListingItem) => !l.is_outlier && l.price && Number(l.price) > 0)
                .map((l: ListingItem) => Number(l.price));
              if (nonOutlierPrices.length > 0) {
                setLowestPrice(aggData.lowest_price || Math.min(...nonOutlierPrices));
                setAvgPrice(aggData.average_price || Math.round(nonOutlierPrices.reduce((a: number, b: number) => a + b, 0) / nonOutlierPrices.length));
              } else {
                setLowestPrice(aggData.lowest_price || null);
                setAvgPrice(aggData.average_price || null);
              }
            }
            // Do NOT reset listings to [] if no live providers returned — keep DB listings

            if (aggData.image_gallery && aggData.image_gallery.length > 0) {
              setGalleryImages((prev) => Array.from(new Set([...aggData.image_gallery, ...prev])));
            }
            if (aggData.specifications) {
              setSpecs((prev) => ({ ...prev, ...aggData.specifications }));
            }
            if (aggData.ai_insights) {
              setAiInsights(aggData.ai_insights);
            }
          }
        } catch {
          // Live provider call failed — do NOT wipe price summary or listings.
          // The major marketplace section will show "Unavailable" status entries.
          // Previously loaded DB listings (if any) remain visible.
          if (isMounted) {
            // Mark all major marketplaces as temporarily unavailable
            setMajorMarketplaceStatus((prev) =>
              prev.length > 0
                ? prev.map((mp) => ({ ...mp, status: "unavailable" as const }))
                : []
            );
          }
        }


        apiClient.post(`/products/${pData.id}/view`).catch(() => {});

      } catch (err: unknown) {
        if (isMounted) {
          if (typeof err === "object" && err !== null && "response" in err) {
            const status = (err as { response?: { status?: number } }).response?.status;
            if (status === 404) {
              setNotFound(true);
            } else {
              setHasError(true);
            }
          } else {
            setHasError(true);
          }
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadProductData();

    return () => {
      isMounted = false;
    };
  }, [rawId]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center space-y-4" style={{ background: "var(--background)" }}>
        <Loader2 className="h-10 w-10 animate-spin text-indigo-400" />
        <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
          Loading canonical product details...
        </p>
      </div>
    );
  }

  if (notFound || !product) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center" style={{ background: "var(--background)", paddingTop: "88px" }}>
        <div className="rounded-3xl border p-8 max-w-md w-full space-y-5 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="p-4 rounded-2xl bg-rose-500/10 text-rose-400 w-16 h-16 mx-auto flex items-center justify-center border border-rose-500/20">
            <PackageX className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
            Product Unavailable
          </h1>
          <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            The requested product could not be found or has been removed from our public catalog index.
          </p>
          <Link
            href="/products"
            className="inline-flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold gradient-bg text-white shadow-lg transition-all hover:opacity-90"
          >
            <ChevronLeft className="h-4 w-4" /> Back to Products Catalog
          </Link>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center" style={{ background: "var(--background)", paddingTop: "88px" }}>
        <div className="rounded-3xl border p-8 max-w-md w-full space-y-5 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="p-4 rounded-2xl bg-amber-500/10 text-amber-400 w-16 h-16 mx-auto flex items-center justify-center border border-amber-500/20">
            <AlertCircle className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
            Unable to Load Product
          </h1>
          <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            A temporary network error occurred. Please reload to try again.
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => window.location.reload()}
              className="flex-1 py-3 rounded-xl text-sm font-semibold border hover:border-indigo-500 transition-colors"
              style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              Reload Page
            </button>
            <Link
              href="/products"
              className="flex-1 inline-flex items-center justify-center py-3 rounded-xl text-sm font-semibold gradient-bg text-white shadow-lg"
            >
              Products Catalog
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const productName = product.name;

  // Filter listings to separate verified exact listings vs unverified
  const verifiedListings = listings.filter((l) => l.verification_status !== "unverified" && l.is_exact_url !== false);
  const minP = lowestPrice && lowestPrice > 0 ? lowestPrice : (verifiedListings.length > 0 ? Math.min(...verifiedListings.map((l) => l.price).filter((p) => p > 0)) : null);
  const currentImage = galleryImages[activeImageIndex] || galleryImages[0] || product.image_url || "";

  const formatLastChecked = (isoStr: string | null): string => {
    if (!isoStr) return "Not yet checked";
    try {
      const date = new Date(isoStr);
      const diffMs = Date.now() - date.getTime();
      const diffSecs = Math.floor(diffMs / 1000);
      const diffMins = Math.floor(diffSecs / 60);
      if (diffSecs < 60) return "Just now";
      if (diffMins < 60) return `${diffMins}m ago`;
      return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "Recently";
    }
  };

  const handleRefresh = async () => {
    if (!product || isRefreshing || refreshCooldown) return;
    setIsRefreshing(true);
    try {
      const res = await apiClient.post(`/products/${product.id}/refresh`);
      const data = res.data?.data;
      if (data) {
        if (data.listings && data.listings.length > 0) setListings(data.listings);
        if (data.major_marketplace_status) setMajorMarketplaceStatus(data.major_marketplace_status);
        if (typeof data.verified_marketplace_count === "number") setVerifiedMarketplaceCount(data.verified_marketplace_count);
        if (data.data_quality) setDataQuality(data.data_quality);
        if (data.marketplace_coverage) setMarketplaceCoverage(data.marketplace_coverage);
        if (data.last_checked) setLastChecked(data.last_checked);
        if (data.lowest_price) setLowestPrice(data.lowest_price);
        if (data.average_price) setAvgPrice(data.average_price);
        setRefreshCooldown(true);
        setRefreshCooldownSeconds(data.cooldown_seconds || 60);
        const interval = setInterval(() => {
          setRefreshCooldownSeconds((prev) => {
            if (prev <= 1) {
              clearInterval(interval);
              setRefreshCooldown(false);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      }
    } catch (err: unknown) {
      // 429 = cooldown still active from a previous refresh
      const errObj = err as { response?: { status?: number; data?: { detail?: { retry_after_seconds?: number } } } };
      if (errObj?.response?.status === 429) {
        const retryAfter = errObj?.response?.data?.detail?.retry_after_seconds || 60;
        setRefreshCooldown(true);
        setRefreshCooldownSeconds(retryAfter);
      }
    } finally {
      setIsRefreshing(false);
    }
  };

  return (

    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <PriceAlertModal
        isOpen={isAlertModalOpen}
        onClose={() => setIsAlertModalOpen(false)}
        productId={product.id}
        productName={productName}
        currentPrice={minP || Number(product.base_price) || 0}
      />


      <div className="max-w-7xl mx-auto space-y-10">

        {/* Top Navigation & Action Header */}
        <div className="flex items-center justify-between">
          <Link
            href="/products"
            className="inline-flex items-center gap-2 text-sm font-medium hover:text-indigo-400 transition-colors"
            style={{ color: "var(--foreground-muted)" }}
          >
            <ChevronLeft className="h-4 w-4" /> Back to Products Catalog
          </Link>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsAlertModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-all shadow-sm"
              title="Set Price Drop Alert"
            >
              <Bell className="h-4 w-4" /> Price Drop Alert
            </button>

            <WishlistHeartButton productId={product.id} size="lg" />

            <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-sm">
              <ShieldCheck className="h-3.5 w-3.5" /> Verified Data Engine
            </span>
          </div>
        </div>

        {/* Product Card: Gallery + Overview */}
        <div className="rounded-3xl p-6 sm:p-10 border grid grid-cols-1 lg:grid-cols-12 gap-10 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>

          {/* ── GALLERY CONTAINER (lg:col-span-5) ─────────────────────────────────── */}
          <div className="lg:col-span-5 flex flex-col space-y-4">
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

            {/* Thumbnail Strip */}
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

          {/* ── PRODUCT DETAILS & PRICE STATS (lg:col-span-7) ────────────────────── */}
          <div className="lg:col-span-7 flex flex-col justify-between space-y-6">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 font-bold border border-indigo-500/20">
                  <Tag className="h-3.5 w-3.5" /> {product.brand || specs?.brand || "Brand"}
                </span>
                <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                  <ShieldCheck className="h-3.5 w-3.5" /> {product.category || "Verified Category"}
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
                {product.description || `Verified marketplace product catalog entry with strict exact attribute matching.`}
              </p>
            </div>

            {/* Price Stats Banner */}
            <div className="p-6 rounded-2xl border grid grid-cols-1 sm:grid-cols-3 gap-4 shadow-inner" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              <div>
                <span className="text-xs font-semibold block" style={{ color: "var(--foreground-muted)" }}>
                  Verified Best Price
                </span>
                {lowestPrice && lowestPrice > 0 && listings.length > 0 ? (
                  <p className="text-3xl font-black text-emerald-400">
                    ₹{Number(lowestPrice).toLocaleString("en-IN")}
                  </p>
                ) : (
                  <p className="text-sm font-bold text-amber-400">
                    Unavailable
                  </p>
                )}
              </div>

              <div>
                <span className="text-xs font-semibold block" style={{ color: "var(--foreground-muted)" }}>
                  Market Average
                </span>
                <p className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
                  {avgPrice && avgPrice > 0 && listings.length > 0
                    ? `₹${Number(avgPrice).toLocaleString("en-IN")}`
                    : "Unavailable"}
                </p>
              </div>

              <div>
                <span className="text-xs font-semibold block text-indigo-400">
                  Stock Availability
                </span>
                <p className="text-xl font-bold text-indigo-400 uppercase tracking-wide">
                  {product.stock_status || "In Stock"}
                </p>
              </div>
            </div>

            {/* Key Specs */}
            {specs && (
              <div className="space-y-3 pt-2">
                <h3 className="text-sm font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                  <Layers className="h-4 w-4 text-indigo-400" /> Key Specifications
                </h3>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  {specs.brand && (
                    <div className="p-2.5 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                      <span className="block text-[11px]" style={{ color: "var(--foreground-muted)" }}>Brand</span>
                      <span className="font-bold" style={{ color: "var(--foreground)" }}>{specs.brand}</span>
                    </div>
                  )}
                  {specs.category && (
                    <div className="p-2.5 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                      <span className="block text-[11px]" style={{ color: "var(--foreground-muted)" }}>Category</span>
                      <span className="font-bold" style={{ color: "var(--foreground)" }}>{specs.category}</span>
                    </div>
                  )}
                  {specs.release_year && (
                    <div className="p-2.5 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                      <span className="block text-[11px]" style={{ color: "var(--foreground-muted)" }}>Year</span>
                      <span className="font-bold" style={{ color: "var(--foreground)" }}>{specs.release_year}</span>
                    </div>
                  )}
                  {specs.overall_rating && (
                    <div className="p-2.5 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                      <span className="block text-[11px]" style={{ color: "var(--foreground-muted)" }}>Rating</span>
                      <span className="font-bold" style={{ color: "var(--foreground)" }}>{specs.overall_rating} / 5</span>
                    </div>
                  )}
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

                {aiInsights.pros && aiInsights.pros.length > 0 && (
                  <>
                    <h4 className="text-xs font-bold text-indigo-400 mt-2">Key Pros</h4>
                    <ul className="space-y-1 text-xs" style={{ color: "var(--foreground-muted)" }}>
                      {aiInsights.pros.map((pro, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <Check className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{pro}</span>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>

              {/* Price Trend & Value Score */}
              <div className="space-y-4 p-5 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <h3 className="text-sm font-bold text-purple-400 flex items-center gap-1.5">
                  <TrendingDown className="h-4 w-4" /> Price Trend & Drop Prediction
                </h3>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  {aiInsights.price_trend || "Historical price trend is stable. Verified catalog item."}
                </p>

                {aiInsights.value_for_money_score && (
                  <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 mt-3">
                    <span className="text-xs font-bold text-purple-400 block">Value for Money Score</span>
                    <p className="text-2xl font-black text-purple-300">{aiInsights.value_for_money_score} / 10</p>
                  </div>
                )}
              </div>

              {/* Best Store & Alternatives */}
              <div className="space-y-4 p-5 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <h3 className="text-sm font-bold text-amber-400 flex items-center gap-1.5">
                  <Award className="h-4 w-4" /> Best Store & Alternatives
                </h3>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  {aiInsights.best_marketplace_recommendation || "Purchase directly from authorized stores with verified pricing."}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ── PRICE HISTORY CHART ─────────────────────────────────────────────── */}
        <PriceHistoryChart
          productId={product.id}
          productName={productName}
          basePrice={minP || undefined}
        />

        {/* ── MAJOR MARKETPLACES — ALWAYS VISIBLE ────────────────────────────── */}
        <div className="rounded-3xl border p-6 sm:p-8 space-y-5 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b pb-4" style={{ borderColor: "var(--border)" }}>
            <div>
              <h2 className="text-xl font-bold tracking-tight flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                <ShieldCheck className="h-5 w-5 text-indigo-400" /> Major Marketplace Coverage
              </h2>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                Always-visible status for all 7 major Indian marketplaces.
                Green = verified live price. Amber = no listing found. Use Search links to check manually.
              </p>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              {/* Coverage badge */}
              <span className={`text-xs font-bold px-3 py-1.5 rounded-full border ${
                dataQuality === "high" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
                dataQuality === "medium" ? "bg-amber-500/10 text-amber-400 border-amber-500/20" :
                "bg-gray-500/10 text-gray-400 border-gray-500/20"
              }`}>
                {marketplaceCoverage}
              </span>
              {/* Refresh button with cooldown */}
              <button
                onClick={handleRefresh}
                disabled={isRefreshing || refreshCooldown}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold border transition-all ${
                  isRefreshing || refreshCooldown
                    ? "opacity-50 cursor-not-allowed"
                    : "hover:border-indigo-500 hover:text-indigo-400"
                }`}
                style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
                title={refreshCooldown ? `Cooldown: ${refreshCooldownSeconds}s` : "Refresh live prices"}
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin text-indigo-400" : ""}`} />
                {isRefreshing ? "Refreshing..." : refreshCooldown ? `Wait ${refreshCooldownSeconds}s` : "Refresh Prices"}
              </button>
            </div>
          </div>

          {lastChecked && (
            <p className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>
              Last checked: {formatLastChecked(lastChecked)}
            </p>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {majorMarketplaceStatus.length === 0 ? (
              // Not yet fetched — show placeholder cards
              Array.from({ length: 7 }).map((_, i) => (
                <div key={i} className="rounded-2xl border p-4 animate-pulse" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="h-8 w-8 rounded-xl bg-gray-500/20" />
                    <div className="h-3 w-20 rounded bg-gray-500/20" />
                  </div>
                  <div className="h-5 w-24 rounded bg-gray-500/20" />
                </div>
              ))
            ) : (
              majorMarketplaceStatus.map((mp) => (
                <div
                  key={mp.slug}
                  className={`rounded-2xl border p-4 transition-all ${
                    mp.has_verified_price
                      ? "border-emerald-500/30 bg-emerald-500/5 hover:bg-emerald-500/10"
                      : "hover:border-gray-500/40"
                  }`}
                  style={mp.has_verified_price ? {} : { background: "var(--background)", borderColor: "var(--border)" }}
                >
                  {/* Store header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2.5">
                      {mp.logo_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={mp.logo_url} alt={mp.name} className="h-6 w-auto max-w-[60px] object-contain" />
                      ) : (
                        <div className="h-6 w-6 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                          <span className="text-[10px] font-bold text-indigo-400">{mp.name[0]}</span>
                        </div>
                      )}
                      <span className="text-xs font-bold" style={{ color: "var(--foreground)" }}>{mp.name}</span>
                    </div>

                    {mp.has_verified_price && (
                      <span className="inline-flex items-center gap-1 text-[9px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        <CheckCircle2 className="h-2.5 w-2.5" /> Verified
                      </span>
                    )}
                  </div>

                  {/* Price or status */}
                  {mp.has_verified_price && mp.price ? (
                    <>
                      <div className="flex items-baseline gap-2">
                        <p className="text-xl font-black text-emerald-400">
                          ₹{Number(mp.price).toLocaleString("en-IN")}
                        </p>
                        {mp.original_price && mp.original_price > mp.price && (
                          <span className="text-xs line-through" style={{ color: "var(--foreground-muted)" }}>
                            ₹{Number(mp.original_price).toLocaleString("en-IN")}
                          </span>
                        )}
                        {mp.discount_percent && mp.discount_percent > 0 && (
                          <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                            {Math.round(mp.discount_percent)}% OFF
                          </span>
                        )}
                      </div>
                      {mp.seller_name && (
                        <p className="text-[10px] mt-0.5 truncate" style={{ color: "var(--foreground-muted)" }}>
                          Seller: {mp.seller_name}
                        </p>
                      )}
                      {mp.delivery_estimate && (
                        <p className="text-[10px] flex items-center gap-1 mt-1 text-indigo-400">
                          <Clock className="h-3 w-3" /> {mp.delivery_estimate}
                        </p>
                      )}
                    </>
                  ) : (
                    <>
                      <p className="text-xs font-bold text-amber-400 mb-1">
                        {mp.status === "not_checked" ? "Not checked yet" : "No verified listing"}
                      </p>
                      {mp.unavailable_reason && (
                        <p className="text-[10px]" style={{ color: "var(--foreground-muted)" }}>
                          {mp.unavailable_reason}
                        </p>
                      )}
                    </>
                  )}

                  {/* Action Button: "Buy Now" for verified direct listing vs "Search [Marketplace]" for fallback */}
                  <a
                    href={mp.has_verified_price ? mp.listing_url : mp.search_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`mt-3 w-full inline-flex items-center justify-center gap-1.5 text-[11px] font-bold px-3 py-2 rounded-xl transition-all shadow-sm ${
                      mp.has_verified_price
                        ? "gradient-bg text-white hover:opacity-95 hover:shadow-indigo-500/25"
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20"
                    }`}
                  >
                    {mp.has_verified_price ? (
                      <><ShoppingBag className="h-3.5 w-3.5" /> Buy Now on {mp.name}</>
                    ) : (
                      <><Search className="h-3.5 w-3.5" /> Search {mp.name}</>
                    )}
                  </a>
                </div>
              ))
            )}
          </div>
        </div>

        {/* ── MARKETPLACE PRICE COMPARISON MATRIX ───────────────────────────────── */}
        <div className="rounded-3xl border p-6 sm:p-8 space-y-6 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b pb-4" style={{ borderColor: "var(--border)" }}>
            <div>
              <h2 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>
                Marketplace Price Comparison Matrix
              </h2>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                Verified prices from online retailers with exact attribute matching.
              </p>
            </div>

            <span className="text-xs font-bold px-3.5 py-1.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 self-start sm:self-auto">
              {listings.length} Marketplace Offers
            </span>
          </div>

          {listings.length === 0 ? (
            <div className="text-center py-12 space-y-4">
              <ShoppingBag className="h-10 w-10 text-amber-400 mx-auto" />
              <div className="space-y-1">
                <p className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                  Live marketplace prices are temporarily unavailable.
                </p>
                <p className="text-xs text-amber-400 font-semibold max-w-md mx-auto leading-relaxed">
                  Marketplace providers could not verify current listings for this exact product model.
                </p>
              </div>
              <span className="inline-block text-[11px] font-mono px-3 py-1 rounded-lg bg-gray-500/10 text-gray-400 border border-gray-500/20">
                Last checked: {new Date().toLocaleTimeString()} (UTC)
              </span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b text-xs font-bold uppercase tracking-wider" style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}>
                    <th className="py-3 px-4">Store</th>
                    <th className="py-3 px-4">Live Price</th>
                    <th className="py-3 px-4">Verification</th>
                    <th className="py-3 px-4">Delivery</th>
                    <th className="py-3 px-4">Offers</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y" style={{ borderColor: "var(--border)" }}>
                  {listings.map((lst, idx) => {
                    const isCheapest = lst.price === minP && minP > 0;
                    const isVerified = lst.verification_status !== "unverified" && lst.is_exact_url !== false;

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
                                <img src={lst.marketplace_logo} alt={lst.marketplace_name || "Store"} className="h-full w-full object-contain" />
                              ) : (
                                <span className="font-bold text-xs text-gray-800">
                                  {lst.marketplace_name ? lst.marketplace_name[0] : "S"}
                                </span>
                              )}
                            </div>

                            <div>
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
                                  {lst.marketplace_name || lst.seller_name || "Store"}
                                </span>
                                {isCheapest && (
                                  <span className="inline-flex items-center gap-1 text-[10px] font-black px-2 py-0.5 rounded-full bg-emerald-500 text-white shadow-sm">
                                    <Award className="h-3 w-3" /> BEST PRICE
                                  </span>
                                )}
                              </div>
                              <span className="text-[11px] block" style={{ color: "var(--foreground-muted)" }}>
                                Seller: {lst.seller_name || "Merchant"}
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* Price Column */}
                        <td className="py-4 px-4">
                          <div>
                            {lst.price && Number(lst.price) > 0 ? (
                              <span className="text-lg font-black text-emerald-400">
                                ₹{Number(lst.price).toLocaleString("en-IN")}
                              </span>
                            ) : (
                              <span className="text-xs font-bold text-amber-400">
                                Price Unavailable
                              </span>
                            )}
                            {lst.original_price && Number(lst.original_price) > Number(lst.price) && (
                              <div className="flex items-center gap-1.5 text-xs">
                                <span className="line-through" style={{ color: "var(--foreground-muted)" }}>
                                  ₹{Number(lst.original_price).toLocaleString("en-IN")}
                                </span>
                                <span className="text-indigo-400 font-semibold">
                                  {lst.discount_percent || 10}% Off
                                </span>
                              </div>
                            )}
                          </div>
                        </td>

                        {/* Verification Column */}
                        <td className="py-4 px-4">
                          {isVerified ? (
                            <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" /> Verified Item
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-xs font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
                              <Search className="h-3.5 w-3.5 text-amber-400" /> Search Link
                            </span>
                          )}
                        </td>

                        {/* Delivery Column */}
                        <td className="py-4 px-4">
                          <span className="inline-flex items-center gap-1 text-xs font-semibold" style={{ color: "var(--foreground)" }}>
                            <Clock className="h-3.5 w-3.5 text-indigo-400" /> {lst.delivery_estimate || "2-3 Days"}
                          </span>
                        </td>

                        {/* Offers Column */}
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
                            {!lst.emi_option && !lst.special_offers && (
                              <span className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>
                                Standard Return & Warranty
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Buy Now / Search Button Column */}
                        <td className="py-4 px-4 text-right">
                          {isVerified ? (
                            <a
                              href={lst.listing_url || "#"}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold gradient-bg text-white shadow-md hover:opacity-90 transition-opacity"
                            >
                              Buy on {lst.marketplace_name || "Store"} <ExternalLink className="h-3.5 w-3.5" />
                            </a>
                          ) : (
                            <a
                              href={lst.listing_url || "#"}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-all shadow-sm"
                            >
                              Search {lst.marketplace_name || "Store"} <ExternalLink className="h-3.5 w-3.5" />
                            </a>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Fullscreen Lightbox Modal */}
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
