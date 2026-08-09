"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  ShoppingBag,
  ChevronLeft,
  Tag,
  ExternalLink,
  Star,
  TrendingDown,
  AlertCircle,
  Loader2,
  CheckCircle2,
  XCircle,
  Award,
  ArrowUpDown,
  SlidersHorizontal,
  Clock,
  Zap,
} from "lucide-react";
import apiClient from "@/services/api";
import { MarketplaceBadge } from "@/components/shared/MarketplaceBadge";
import type { Product, PriceCompareResult, ProductListing } from "@/types";

export default function CompareProductPage() {
  const params = useParams();
  const productId = typeof params?.id === "string" ? params.id : Array.isArray(params?.id) ? params.id[0] : "";

  const [product, setProduct] = useState<Product | null>(null);
  const [compareData, setCompareData] = useState<PriceCompareResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Sorting & Filtering state
  const [sortBy, setSortBy] = useState<"price-asc" | "price-desc" | "rating" | "discount">("price-asc");
  const [filterStockOnly, setFilterStockOnly] = useState(false);

  const fetchComparison = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const prodRes = await apiClient.get(`/products/${productId}`);
      setProduct(prodRes.data.data);

      try {
        const compRes = await apiClient.get(`/products/${productId}/compare`);
        setCompareData(compRes.data);
      } catch {
        // Handle missing listings
      }
    } catch {
      setError("Failed to load product comparison details.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let isCancelled = false;

    async function loadData() {
      setError(null);
      try {
        const prodRes = await apiClient.get(`/products/${productId}`);
        if (!isCancelled) {
          setProduct(prodRes.data.data);
        }

        try {
          const compRes = await apiClient.get(`/products/${productId}/compare`);
          if (!isCancelled) {
            setCompareData(compRes.data);
          }
        } catch {
          // Listings comparison fallback
        }
      } catch {
        if (!isCancelled) {
          setError("Failed to load product comparison details.");
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    if (productId) {
      loadData();
    }

    return () => {
      isCancelled = true;
    };
  }, [productId]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--background)" }}>
        <div className="text-center space-y-3">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-400 mx-auto" />
          <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
            Building Marketplace Comparison Matrix…
          </p>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen py-24 px-4 text-center" style={{ background: "var(--background)" }}>
        <div className="max-w-md mx-auto space-y-4">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto" />
          <h1 className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
            Comparison Unavailable
          </h1>
          <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
            {error || "The requested product does not exist."}
          </p>
          <div className="pt-2">
            <button
              onClick={fetchComparison}
              className="px-4 py-2 rounded-xl gradient-bg text-white text-sm font-semibold mr-3"
            >
              Retry
            </button>
            <Link
              href="/products"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border text-sm font-medium"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              <ChevronLeft className="h-4 w-4" /> Catalog
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const rawListings = compareData?.listings || [];

  // Filter & Sort listings
  const processedListings = rawListings
    .filter((lst) => (filterStockOnly ? lst.is_available : true))
    .sort((a, b) => {
      if (sortBy === "price-asc") return Number(a.price) - Number(b.price);
      if (sortBy === "price-desc") return Number(b.price) - Number(a.price);
      if (sortBy === "rating") return (Number(b.rating) || 0) - (Number(a.rating) || 0);
      if (sortBy === "discount") return (Number(b.discount_percent) || 0) - (Number(a.discount_percent) || 0);
      return 0;
    });

  return (
    <div
      className="min-h-screen py-12 px-4 sm:px-6 lg:px-8"
      style={{ background: "var(--background)", paddingTop: "88px" }}
    >
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link
            href={`/products/${product.id}`}
            className="inline-flex items-center gap-2 text-sm font-medium hover:text-indigo-400 transition-colors"
            style={{ color: "var(--foreground-muted)" }}
          >
            <ChevronLeft className="h-4 w-4" /> Back to Product Details
          </Link>
          <span className="text-xs px-3 py-1 rounded-full border gradient-text font-bold" style={{ borderColor: "var(--border)" }}>
            Marketplace Intelligence Engine v1.0
          </span>
        </div>

        {/* Product Overview Header Card */}
        <div
          className="rounded-2xl p-6 sm:p-8 border grid grid-cols-1 lg:grid-cols-4 gap-6 items-center"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="flex justify-center p-4 rounded-xl border bg-black/5 dark:bg-white/5" style={{ borderColor: "var(--border)" }}>
            {product.image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={product.image_url} alt={product.name} className="max-h-44 object-contain" />
            ) : (
              <ShoppingBag className="h-20 w-20 text-indigo-400" />
            )}
          </div>

          <div className="lg:col-span-3 space-y-4">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                {product.brand && (
                  <span className="inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 font-semibold">
                    <Tag className="h-3 w-3" /> {product.brand}
                  </span>
                )}
                {product.category && (
                  <span className="text-xs px-2.5 py-0.5 rounded-full border" style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}>
                    {product.category}
                  </span>
                )}
              </div>

              <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: "var(--foreground)" }}>
                {product.name}
              </h1>
            </div>

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
              <div className="p-3 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Lowest Price</span>
                <p className="text-lg font-bold text-emerald-400">
                  {compareData?.lowest_price ? `₹${Number(compareData.lowest_price).toLocaleString("en-IN")}` : "N/A"}
                </p>
              </div>

              <div className="p-3 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Highest Price</span>
                <p className="text-lg font-bold text-amber-400">
                  {compareData?.highest_price ? `₹${Number(compareData.highest_price).toLocaleString("en-IN")}` : "N/A"}
                </p>
              </div>

              <div className="p-3 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Average Price</span>
                <p className="text-lg font-bold gradient-text">
                  {compareData?.average_price ? `₹${Number(compareData.average_price).toLocaleString("en-IN")}` : "N/A"}
                </p>
              </div>

              <div className="p-3 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                <span className="text-xs text-indigo-400 font-semibold flex items-center gap-1">
                  <TrendingDown className="h-3.5 w-3.5" /> Max Savings
                </span>
                <p className="text-lg font-bold text-indigo-400">
                  {compareData?.max_savings ? `₹${Number(compareData.max_savings).toLocaleString("en-IN")}` : "₹0"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Toolbar: Filters & Sort */}
        <div
          className="rounded-2xl p-4 border flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="flex items-center gap-3">
            <SlidersHorizontal className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
            <label className="flex items-center gap-2 text-xs font-medium cursor-pointer" style={{ color: "var(--foreground)" }}>
              <input
                type="checkbox"
                checked={filterStockOnly}
                onChange={(e) => setFilterStockOnly(e.target.checked)}
                className="rounded text-indigo-500 focus:ring-indigo-400"
              />
              In-Stock Only ({rawListings.filter((l) => l.is_available).length})
            </label>
          </div>

          <div className="flex items-center gap-3">
            <ArrowUpDown className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "price-asc" | "price-desc" | "rating" | "discount")}
              className="py-2 px-3 rounded-xl text-xs font-medium border"
              style={{
                background: "var(--background)",
                borderColor: "var(--border)",
                color: "var(--foreground)",
              }}
            >
              <option value="price-asc">Price: Low to High</option>
              <option value="price-desc">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
              <option value="discount">Biggest Discount</option>
            </select>
          </div>
        </div>

        {/* Marketplace Comparison Cards / Matrix Table */}
        <div
          className="rounded-2xl border p-6 space-y-6"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="flex items-center justify-between border-b pb-4" style={{ borderColor: "var(--border)" }}>
            <h2 className="text-xl font-bold" style={{ color: "var(--foreground)" }}>
              Marketplace Offer Comparison
            </h2>
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400">
              Showing {processedListings.length} of {rawListings.length} Offers
            </span>
          </div>

          {processedListings.length === 0 ? (
            <div className="text-center py-16 space-y-3">
              <ShoppingBag className="h-12 w-12 text-gray-500 mx-auto" />
              <h3 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                No active marketplace listings found
              </h3>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Try disabling filters or search for another product.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {processedListings.map((lst: ProductListing, i: number) => {
                const isBestDeal = compareData?.best_listing_id === lst.id;
                return (
                  <motion.div
                    key={lst.id}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04 }}
                    className={`p-5 rounded-2xl border flex flex-col md:flex-row md:items-center md:justify-between gap-6 transition-all ${
                      isBestDeal ? "border-emerald-500/50" : ""
                    }`}
                    style={{
                      background: isBestDeal ? "rgba(16,185,129,0.04)" : "var(--background)",
                      borderColor: isBestDeal ? "rgba(16,185,129,0.4)" : "var(--border)",
                    }}
                  >
                    {/* Marketplace Logo & Title */}
                    <div className="flex items-start gap-4">
                      <div className="h-12 w-12 rounded-xl gradient-bg flex items-center justify-center text-white font-bold text-base flex-shrink-0 shadow-sm">
                        {lst.marketplace?.name ? lst.marketplace.name[0] : "M"}
                      </div>

                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                            {lst.marketplace?.name || "Marketplace Partner"}
                          </h3>

                          {isBestDeal && (
                            <span className="inline-flex items-center gap-1 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500 text-white shadow-sm">
                              <Award className="h-3 w-3" /> BEST DEAL
                            </span>
                          )}

                          {lst.badges?.map((badge) => (
                            <MarketplaceBadge key={badge} type={badge} />
                          ))}
                        </div>

                        <div className="flex flex-wrap items-center gap-3 text-xs" style={{ color: "var(--foreground-muted)" }}>
                          {lst.seller_name && <span>Seller: <strong>{lst.seller_name}</strong></span>}
                          {lst.rating && (
                            <span className="flex items-center gap-1 text-amber-400 font-semibold">
                              <Star className="h-3 w-3 fill-amber-400" /> {lst.rating} ({lst.review_count || 0})
                            </span>
                          )}
                          {lst.delivery_estimate && (
                            <span className="flex items-center gap-1 text-indigo-400 font-medium">
                              <Zap className="h-3 w-3" /> {lst.delivery_estimate}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            {lst.is_available ? (
                              <span className="text-emerald-400 flex items-center gap-1 font-medium"><CheckCircle2 className="h-3 w-3" /> In Stock</span>
                            ) : (
                              <span className="text-red-400 flex items-center gap-1 font-medium"><XCircle className="h-3 w-3" /> Out of Stock</span>
                            )}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Price & Action Button */}
                    <div className="flex items-center justify-between md:justify-end gap-6 pt-4 md:pt-0 border-t md:border-t-0" style={{ borderColor: "var(--border)" }}>
                      <div className="text-left md:text-right">
                        <p className="text-2xl font-bold gradient-text">
                          ₹{Number(lst.price).toLocaleString("en-IN")}
                        </p>
                        {lst.original_price && Number(lst.original_price) > Number(lst.price) && (
                          <div className="flex items-center gap-2 text-xs" style={{ color: "var(--foreground-muted)" }}>
                            <span className="line-through">₹{Number(lst.original_price).toLocaleString("en-IN")}</span>
                            {lst.discount_percent && (
                              <span className="text-emerald-400 font-bold">({Number(lst.discount_percent).toFixed(0)}% OFF)</span>
                            )}
                          </div>
                        )}
                      </div>

                      <a
                        href={lst.listing_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold gradient-bg text-white shadow-md hover:opacity-90 transition-opacity"
                      >
                        Go to Store <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>

        {/* Feature Highlights Footer */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="p-5 rounded-2xl border space-y-2" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
            <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
              <Clock className="h-4 w-4" /> Live Price Intelligence
            </div>
            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
              Prices are normalized and verified across all participating stores.
            </p>
          </div>

          <div className="p-5 rounded-2xl border space-y-2" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm">
              <Award className="h-4 w-4" /> Best Deal Ranking
            </div>
            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
              Our ranking engine balances price, shipping speed, seller rating, and stock availability.
            </p>
          </div>

          <div className="p-5 rounded-2xl border space-y-2" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
            <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
              <TrendingDown className="h-4 w-4" /> Price Drop Tracking
            </div>
            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
              Historical price trends log price movements over time.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
