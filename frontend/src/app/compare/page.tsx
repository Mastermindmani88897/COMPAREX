"use client";

import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  Search,
  SlidersHorizontal,
  ArrowUpDown,
  ShoppingBag,
  Zap,
  Star,
  ExternalLink,
  Award,
  CheckCircle2,
  XCircle,
  TrendingDown,
  Tag,
  Loader2,
  Database,
  Cpu,
} from "lucide-react";
import apiClient from "@/services/api";
import type { AggregatedSearchResponse, ConnectorMetadata } from "@/types";

const CATEGORIES = [
  { id: "all", label: "All Categories" },
  { id: "electronics", label: "Electronics (Amazon, Flipkart, Croma, Reliance, Vijay)" },
  { id: "fashion", label: "Fashion (Amazon, Flipkart, Myntra, Ajio, Meesho)" },
  { id: "beauty", label: "Beauty & Personal Care (Amazon, Flipkart, Nykaa)" },
];

export default function AggregatedComparePage() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "iPhone 15";
  const initialCategory = searchParams.get("category") || "all";

  const [query, setQuery] = useState(initialQuery);
  const [activeCategory, setActiveCategory] = useState(initialCategory);

  const [connectors, setConnectors] = useState<ConnectorMetadata[]>([]);
  const [aggregatorData, setAggregatorData] = useState<AggregatedSearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Sorting & Filtering
  const [sortBy, setSortBy] = useState<"price" | "price_desc" | "rating" | "discount" | "deal_score">("price");
  const [inStockOnly, setInStockOnly] = useState(false);
  const [primeOnly, setPrimeOnly] = useState(false);

  // Fetch Connectors
  useEffect(() => {
    let isCancelled = false;
    async function fetchConnectors() {
      try {
        const res = await apiClient.get("/marketplaces/connectors");
        if (!isCancelled) {
          setConnectors(res.data.data || []);
        }
      } catch {
        // Fallback connectors list
      }
    }
    fetchConnectors();
    return () => {
      isCancelled = true;
    };
  }, []);

  // Fetch Aggregated Prices
  const runAggregation = useCallback(async (searchQuery: string, categoryFilter: string, sort: string, stockFilter: boolean) => {
    setIsLoading(true);
    setError(null);
    try {
      const catParam = categoryFilter === "all" ? "" : categoryFilter;
      const res = await apiClient.get(
        `/comparison/aggregate?q=${encodeURIComponent(searchQuery)}&category=${encodeURIComponent(catParam)}&sort_by=${sort}&in_stock_only=${stockFilter}`
      );
      setAggregatorData(res.data.data);
    } catch {
      setError("Failed to aggregate live connector pricing. Please check your backend connection.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;
    async function loadResults() {
      setIsLoading(true);
      setError(null);
      try {
        let searchQueryToRun = query;
        const idsParam = searchParams.get("ids");
        if (idsParam && /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(idsParam)) {
          try {
            const pRes = await apiClient.get(`/products/${idsParam}`);
            if (pRes.data?.data?.name) {
              searchQueryToRun = pRes.data.data.name;
              setQuery(searchQueryToRun);
            }
          } catch {
            // fallback to current query
          }
        }

        if (!searchQueryToRun.trim()) return;

        const catParam = activeCategory === "all" ? "" : activeCategory;
        const res = await apiClient.get(
          `/comparison/aggregate?q=${encodeURIComponent(searchQueryToRun)}&category=${encodeURIComponent(catParam)}&sort_by=${sortBy}&in_stock_only=${inStockOnly}`
        );
        if (!isCancelled) {
          setAggregatorData(res.data.data);
        }
      } catch {
        if (!isCancelled) {
          setError("Failed to aggregate live connector pricing. Please check backend connection.");
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }
    loadResults();
    return () => {
      isCancelled = true;
    };
  }, [query, activeCategory, sortBy, inStockOnly, searchParams]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      runAggregation(query, activeCategory, sortBy, inStockOnly);
    }
  };

  const listings = (aggregatorData?.listings || []).filter((item) => (primeOnly ? item.is_prime : true));

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-extrabold border gradient-text" style={{ borderColor: "var(--border)" }}>
            <Cpu className="h-3.5 w-3.5 text-indigo-400" /> Phase 4 Multi-Marketplace Connector Framework
          </span>
          <h1 className="text-3xl sm:text-4xl font-extrabold" style={{ color: "var(--foreground)" }}>
            Live Price <span className="gradient-text">Aggregator</span> Engine
          </h1>
          <p className="text-sm max-w-2xl mx-auto" style={{ color: "var(--foreground-muted)" }}>
            Querying Amazon, Flipkart, Croma, Reliance Digital, Vijay Sales, Myntra, Ajio, Meesho, and Nykaa concurrently.
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative max-w-3xl mx-auto">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5" style={{ color: "var(--foreground-muted)" }} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for iPhone 15, MacBook Pro, Sony Headphones, Lipsticks, Sneakers..."
            className="w-full pl-12 pr-32 py-4 rounded-2xl text-sm font-medium focus:outline-none"
            style={{
              background: "var(--card)",
              border: "1px solid var(--border)",
              color: "var(--foreground)",
            }}
          />
          <button
            type="submit"
            className="absolute right-3 top-1/2 -translate-y-1/2 px-5 py-2.5 rounded-xl gradient-bg text-white text-xs font-bold shadow-md"
          >
            Compare Prices
          </button>
        </form>

        {/* Category Pills */}
        <div className="flex flex-wrap items-center justify-center gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                activeCategory === cat.id ? "gradient-bg text-white shadow-md" : "hover:text-indigo-400"
              }`}
              style={activeCategory === cat.id ? {} : { background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground-muted)" }}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Connector Registry Status Badges */}
        {connectors.length > 0 && (
          <div className="rounded-2xl p-4 border" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5" style={{ color: "var(--foreground-muted)" }}>
                <Zap className="h-3.5 w-3.5 text-amber-400" /> Active Registered Connectors ({connectors.length})
              </span>
              <span className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>
                Category Capability Filtering Enabled
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {connectors.map((c) => {
                const isQueried = aggregatorData?.marketplaces_queried?.includes(c.slug);
                return (
                  <div
                    key={c.slug}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-opacity ${
                      isQueried ? "border-indigo-500/50 bg-indigo-500/10 text-indigo-400" : "opacity-50"
                    }`}
                    style={isQueried ? {} : { borderColor: "var(--border)", color: "var(--foreground-muted)" }}
                  >
                    <span className="h-2 w-2 rounded-full bg-emerald-400" />
                    {c.name}
                    {c.priority === 1 && <span className="text-[9px] bg-amber-400/20 text-amber-400 px-1 rounded">P1</span>}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Summary Stats & Redis Cache Indicator */}
        {aggregatorData && !isLoading && (
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div className="p-4 rounded-2xl border" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Lowest Price</span>
              <p className="text-xl font-extrabold text-emerald-400">
                {aggregatorData.lowest_price ? `₹${aggregatorData.lowest_price.toLocaleString("en-IN")}` : "N/A"}
              </p>
            </div>

            <div className="p-4 rounded-2xl border" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Highest Price</span>
              <p className="text-xl font-extrabold text-amber-400">
                {aggregatorData.highest_price ? `₹${aggregatorData.highest_price.toLocaleString("en-IN")}` : "N/A"}
              </p>
            </div>

            <div className="p-4 rounded-2xl border" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Average Price</span>
              <p className="text-xl font-extrabold gradient-text">
                {aggregatorData.average_price ? `₹${aggregatorData.average_price.toLocaleString("en-IN")}` : "N/A"}
              </p>
            </div>

            <div className="p-4 rounded-2xl border" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <span className="text-xs flex items-center gap-1 text-indigo-400 font-semibold">
                <TrendingDown className="h-3.5 w-3.5" /> Max Savings
              </span>
              <p className="text-xl font-extrabold text-indigo-400">
                {aggregatorData.max_savings ? `₹${aggregatorData.max_savings.toLocaleString("en-IN")}` : "₹0"}
              </p>
            </div>

            <div className="p-4 rounded-2xl border col-span-2 sm:col-span-1" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Cache Status</span>
              <p className="text-xs font-bold mt-1 flex items-center gap-1 text-cyan-400">
                <Database className="h-3.5 w-3.5" />
                {aggregatorData.from_cache ? "Redis Cache HIT" : "Live Connector Query"}
              </p>
            </div>
          </div>
        )}

        {/* Toolbar Controls */}
        <div className="rounded-2xl p-4 border flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
              <span className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>Filters:</span>
            </div>
            <label className="flex items-center gap-2 text-xs font-medium cursor-pointer" style={{ color: "var(--foreground)" }}>
              <input
                type="checkbox"
                checked={inStockOnly}
                onChange={(e) => setInStockOnly(e.target.checked)}
                className="rounded text-indigo-500 focus:ring-indigo-400"
              />
              In-Stock Only
            </label>
            <label className="flex items-center gap-2 text-xs font-medium cursor-pointer" style={{ color: "var(--foreground)" }}>
              <input
                type="checkbox"
                checked={primeOnly}
                onChange={(e) => setPrimeOnly(e.target.checked)}
                className="rounded text-indigo-500 focus:ring-indigo-400"
              />
              Express/Prime Only
            </label>
          </div>

          <div className="flex items-center gap-3">
            <ArrowUpDown className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "price" | "price_desc" | "rating" | "discount" | "deal_score")}
              className="py-2 px-3 rounded-xl text-xs font-medium border"
              style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              <option value="price">Sort by Price: Low to High</option>
              <option value="price_desc">Sort by Price: High to Low</option>
              <option value="deal_score">Sort by Best Deal Score</option>
              <option value="rating">Sort by Highest Rating</option>
              <option value="discount">Sort by Biggest Discount</option>
            </select>
          </div>
        </div>

        {/* Comparison Offer Cards Grid */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="text-center py-20 space-y-3">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-400 mx-auto" />
              <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
                Aggregating live price connectors across marketplaces…
              </p>
            </div>
          ) : error ? (
            <div className="text-center py-16 p-6 rounded-2xl border space-y-3" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <XCircle className="h-10 w-10 text-red-400 mx-auto" />
              <p className="text-sm font-medium text-red-400">{error}</p>
            </div>
          ) : listings.length === 0 ? (
            <div className="text-center py-16 p-6 rounded-2xl border space-y-3" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <ShoppingBag className="h-12 w-12 text-gray-500 mx-auto" />
              <h3 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>No listings found</h3>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>Try searching for another product query or change category filter.</p>
            </div>
          ) : (
            listings.map((item, idx) => {
              const isBestDeal = aggregatorData?.best_deal_listing_id === item.id || idx === 0;
              return (
                <motion.div
                  key={item.id || idx}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.04 }}
                  className={`p-6 rounded-2xl border flex flex-col md:flex-row md:items-center md:justify-between gap-6 transition-all ${
                    isBestDeal ? "border-emerald-500/50 shadow-md" : ""
                  }`}
                  style={{
                    background: isBestDeal ? "rgba(16,185,129,0.04)" : "var(--card)",
                    borderColor: isBestDeal ? "rgba(16,185,129,0.4)" : "var(--border)",
                  }}
                >
                  {/* Left Column: Store info & product title */}
                  <div className="flex items-start gap-4 flex-1">
                    <div className="h-12 w-12 rounded-xl gradient-bg flex items-center justify-center text-white font-bold text-base flex-shrink-0 shadow-sm">
                      {item.marketplace_name[0]}
                    </div>

                    <div className="space-y-1.5 min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full border" style={{ borderColor: "var(--border)", color: "var(--foreground)" }}>
                          {item.marketplace_name}
                        </span>

                        {isBestDeal && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500 text-white shadow-sm">
                            <Award className="h-3 w-3" /> BEST DEAL
                          </span>
                        )}

                        {item.badges?.map((b) => (
                          <span key={b} className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400">
                            {b}
                          </span>
                        ))}
                      </div>

                      <h3 className="text-base font-bold truncate" style={{ color: "var(--foreground)" }}>
                        {item.title}
                      </h3>

                      <div className="flex flex-wrap items-center gap-3 text-xs" style={{ color: "var(--foreground-muted)" }}>
                        {item.seller_name && (
                          <span className="flex items-center gap-1">
                            <Tag className="h-3 w-3 text-indigo-400" /> Seller: <strong>{item.seller_name}</strong>
                          </span>
                        )}
                        {item.rating && (
                          <span className="flex items-center gap-1 text-amber-400 font-semibold">
                            <Star className="h-3 w-3 fill-amber-400" /> {item.rating} ({item.review_count || 840})
                          </span>
                        )}
                        {item.delivery_estimate && (
                          <span className="flex items-center gap-1 text-indigo-400 font-medium">
                            <Zap className="h-3 w-3" /> {item.delivery_estimate}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          {item.is_available ? (
                            <span className="text-emerald-400 flex items-center gap-1 font-medium"><CheckCircle2 className="h-3 w-3" /> In Stock</span>
                          ) : (
                            <span className="text-red-400 flex items-center gap-1 font-medium"><XCircle className="h-3 w-3" /> Out of Stock</span>
                          )}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Price & Action */}
                  <div className="flex items-center justify-between md:justify-end gap-6 pt-4 md:pt-0 border-t md:border-t-0" style={{ borderColor: "var(--border)" }}>
                    <div className="text-left md:text-right">
                      <p className="text-2xl sm:text-3xl font-extrabold gradient-text">
                        ₹{item.price.toLocaleString("en-IN")}
                      </p>
                      {item.original_price && item.original_price > item.price && (
                        <div className="flex items-center gap-2 text-xs" style={{ color: "var(--foreground-muted)" }}>
                          <span className="line-through">₹{item.original_price.toLocaleString("en-IN")}</span>
                          {item.discount_percent && (
                            <span className="text-emerald-400 font-bold">({item.discount_percent}% OFF)</span>
                          )}
                        </div>
                      )}
                      {item.deal_score && (
                        <span className="text-[10px] font-bold text-indigo-400 block mt-0.5">
                          Deal Score: {item.deal_score} / 1.0
                        </span>
                      )}
                    </div>

                    <a
                      href={item.listing_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-xs font-bold gradient-bg text-white shadow-md hover:opacity-90 transition-opacity flex-shrink-0"
                    >
                      Go to Store <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
