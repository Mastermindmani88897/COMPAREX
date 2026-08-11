"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  Search,
  ShoppingBag,
  ChevronRight,
  Package,
  SlidersHorizontal,
  Tag,
  AlertCircle,
  ChevronLeft,
  ArrowUpDown,
  Bell,
} from "lucide-react";
import apiClient from "@/services/api";
import type { Product, Category } from "@/types";
import { WishlistHeartButton } from "@/components/wishlist/WishlistHeartButton";
import { PriceAlertModal } from "@/components/alerts/PriceAlertModal";

export default function ProductsCatalogPage() {
  const searchParams = useSearchParams();
  const initQuery = searchParams.get("q") || "";

  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Search & Filter state
  const [query, setQuery] = useState(initQuery);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"price-asc" | "price-desc" | "name">("name");

  // Pagination state
  const [page, setPage] = useState(1);
  const limit = 12;

  const retryFetch = async () => {
    setIsLoading(true);
    setError(null);
    try {
      try {
        const catRes = await apiClient.get("/categories");
        setCategories(catRes.data.data || []);
      } catch {
        // Non-fatal if categories fail
      }

      const endpoint = query.trim()
        ? `/products?query=${encodeURIComponent(query)}&page=${page}&limit=24`
        : `/products?page=${page}&limit=24`;

      const prodRes = await apiClient.get(endpoint);
      setProducts(prodRes.data.data || []);
    } catch (err: any) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        "Failed to load products. Please check your connection and try again.";
      setError(msg);
      setProducts([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let isCancelled = false;

    async function loadCatalog() {
      setError(null);
      setIsLoading(true);

      // Load categories safely
      try {
        const catRes = await apiClient.get("/categories");
        if (!isCancelled) {
          setCategories(catRes.data.data || []);
        }
      } catch {
        // Non-fatal
      }

      // Load products catalog
      try {
        const endpoint = query.trim()
          ? `/products?query=${encodeURIComponent(query)}&page=${page}&limit=24`
          : `/products?page=${page}&limit=24`;

        const prodRes = await apiClient.get(endpoint);
        if (!isCancelled) {
          setProducts(prodRes.data.data || []);
        }
      } catch (err: any) {
        if (!isCancelled) {
          const msg =
            err?.response?.data?.message ||
            err?.message ||
            "Failed to load products. Please check your connection and try again.";
          setError(msg);
          setProducts([]);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    loadCatalog();

    return () => {
      isCancelled = true;
    };
  }, [query, page]);

  // Client-side filtering & sorting
  const filteredProducts = products
    .filter((p) => {
      if (selectedCategory !== "all") {
        return p.category?.toLowerCase() === selectedCategory.toLowerCase();
      }
      return true;
    })
    .sort((a, b) => {
      if (sortBy === "price-asc") {
        return (Number(a.base_price) || 0) - (Number(b.base_price) || 0);
      }
      if (sortBy === "price-desc") {
        return (Number(b.base_price) || 0) - (Number(a.base_price) || 0);
      }
      return a.name.localeCompare(b.name);
    });

  // Pagination slicing
  const totalPages = Math.ceil(filteredProducts.length / limit) || 1;
  const paginatedProducts = filteredProducts.slice((page - 1) * limit, page * limit);

  // Price Alert Modal state
  const [activeAlertProduct, setActiveAlertProduct] = useState<Product | null>(null);
  
  return (
    <div
      className="min-h-screen py-12 px-4 sm:px-6 lg:px-8"
      style={{ background: "var(--background)", paddingTop: "88px" }}
    >
      {activeAlertProduct && (
        <PriceAlertModal
          isOpen={Boolean(activeAlertProduct)}
          onClose={() => setActiveAlertProduct(null)}
          productId={activeAlertProduct.id}
          productName={activeAlertProduct.name}
          currentPrice={Number(activeAlertProduct.base_price) || 0}
        />
      )}
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Page Title Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: "var(--foreground)" }}>
              Product Catalog
            </h1>
            <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
              Compare prices across top Indian marketplaces for thousands of products.
            </p>
          </div>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border hover:border-indigo-500 transition-colors w-fit"
            style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            Dashboard <ChevronRight className="h-4 w-4" />
          </Link>
        </div>

        {/* Search & Filter Toolbar */}
        <div
          className="rounded-2xl p-4 border space-y-4 md:space-y-0 md:flex md:items-center md:gap-4"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          {/* Search Input */}
          <div className="relative flex-1">
            <Search
              className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4"
              style={{ color: "var(--foreground-muted)" }}
            />
            <input
              type="text"
              id="catalog-search"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setPage(1);
              }}
              placeholder="Search products by name or brand…"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm"
              style={{
                background: "var(--background)",
                border: "1px solid var(--border)",
                color: "var(--foreground)",
              }}
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Category Filter */}
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
              <select
                id="catalog-category-filter"
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setPage(1);
                }}
                className="py-2.5 px-3 rounded-xl text-sm font-medium border"
                style={{
                  background: "var(--background)",
                  borderColor: "var(--border)",
                  color: "var(--foreground)",
                }}
              >
                <option value="all">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.name}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort Dropdown */}
            <div className="flex items-center gap-2">
              <ArrowUpDown className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
              <select
                id="catalog-sort"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as "price-asc" | "price-desc" | "name")}
                className="py-2.5 px-3 rounded-xl text-sm font-medium border"
                style={{
                  background: "var(--background)",
                  borderColor: "var(--border)",
                  color: "var(--foreground)",
                }}
              >
                <option value="name">Sort by Name</option>
                <option value="price-asc">Price: Low to High</option>
                <option value="price-desc">Price: High to Low</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div
            className="flex items-center justify-between p-4 rounded-xl text-sm border"
            style={{
              background: "rgba(239,68,68,0.1)",
              borderColor: "rgba(239,68,68,0.3)",
              color: "#f87171",
            }}
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
            <button
              onClick={retryFetch}
              className="px-3 py-1 bg-red-500/20 text-red-300 font-semibold rounded-lg hover:bg-red-500/30"
            >
              Retry
            </button>
          </div>
        )}

        {/* Product Grid / Loading / Empty State */}
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="h-64 rounded-2xl border animate-pulse p-5 space-y-4"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="h-12 w-12 rounded-xl bg-gray-700/20" />
                <div className="h-4 w-3/4 bg-gray-700/20 rounded" />
                <div className="h-4 w-1/2 bg-gray-700/20 rounded" />
              </div>
            ))}
          </div>
        ) : paginatedProducts.length === 0 ? (
          <div className="text-center py-20 rounded-2xl border p-8" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
            <div className="inline-flex h-16 w-16 rounded-2xl items-center justify-center mb-4" style={{ background: "rgba(99,102,241,0.1)" }}>
              <Package className="h-8 w-8 text-indigo-400" />
            </div>
            <h3 className="text-lg font-bold" style={{ color: "var(--foreground)" }}>
              No products found
            </h3>
            <p className="text-sm mt-1 max-w-md mx-auto" style={{ color: "var(--foreground-muted)" }}>
              {query || selectedCategory !== "all"
                ? "Try adjusting your search query or category filters to find products."
                : "No products currently available in the index."}
            </p>
            {(query || selectedCategory !== "all") && (
              <button
                onClick={() => {
                  setQuery("");
                  setSelectedCategory("all");
                }}
                className="mt-4 px-4 py-2 rounded-xl gradient-bg text-white text-sm font-semibold"
              >
                Reset Filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {paginatedProducts.map((product, i) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <div className="relative group flex flex-col justify-between h-full">
                  <div className="absolute top-3 right-3 z-10 flex items-center gap-1.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        e.preventDefault();
                        setActiveAlertProduct(product);
                      }}
                      className="p-2 rounded-xl border bg-black/40 text-amber-400 backdrop-blur-md hover:bg-black/60 transition-all shadow-sm"
                      style={{ borderColor: "var(--border)" }}
                      title="Set Price Alert"
                    >
                      <Bell className="h-4 w-4" />
                    </button>
                    <WishlistHeartButton productId={product.id} size="sm" />
                  </div>
                  <Link
                    href={`/products/${product.id}`}
                    className="flex flex-col justify-between h-full rounded-2xl p-5 border transition-all duration-200 hover:border-indigo-500 hover:shadow-xl"
                    style={{ background: "var(--card)", borderColor: "var(--border)" }}
                  >
                  <div>
                    <div className="h-12 w-12 rounded-xl flex items-center justify-center mb-4" style={{ background: "rgba(99,102,241,0.1)" }}>
                      {product.image_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={product.image_url} alt={product.name} className="h-10 w-10 object-contain rounded-lg" />
                      ) : (
                        <ShoppingBag className="h-5 w-5 text-indigo-400" />
                      )}
                    </div>

                    <h3 className="text-sm font-semibold leading-snug line-clamp-2 mb-2" style={{ color: "var(--foreground)" }}>
                      {product.name}
                    </h3>

                    {product.description && (
                      <p className="text-xs line-clamp-2 mb-4" style={{ color: "var(--foreground-muted)" }}>
                        {product.description}
                      </p>
                    )}
                  </div>

                  <div>
                    <div className="flex items-center justify-between pt-3 border-t" style={{ borderColor: "var(--border)" }}>
                      <div className="flex flex-wrap gap-1">
                        {product.brand && (
                          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 font-medium">
                            <Tag className="h-2.5 w-2.5" />
                            {product.brand}
                          </span>
                        )}
                      </div>

                      {product.base_price && (
                        <span className="text-base font-bold gradient-text">
                          ₹{Number(product.base_price).toLocaleString("en-IN")}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-1 text-xs mt-3 group-hover:text-indigo-400 transition-colors font-medium" style={{ color: "var(--foreground-muted)" }}>
                      <span>View Price Comparison</span>
                      <ChevronRight className="h-3.5 w-3.5" />
                    </div>
                  </div>
                </Link>
              </div>
            </motion.div>
            ))}
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 pt-6">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 rounded-xl border disabled:opacity-40"
              style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="text-xs font-semibold px-4" style={{ color: "var(--foreground)" }}>
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-2 rounded-xl border disabled:opacity-40"
              style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
