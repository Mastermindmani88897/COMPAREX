"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  ShoppingBag,
  Bell,
  Settings,
  LogOut,
  Search,
  Plus,
  X,
  ChevronRight,
  Package,
  Loader2,
  AlertTriangle,
  Tag,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { AuthGuard } from "@/components/shared/AuthGuard";
import apiClient from "@/services/api";
import type { Product } from "@/types";

const sidebarItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/dashboard", active: false },
  { icon: ShoppingBag, label: "My Products", href: "/dashboard/products", active: true },
  { icon: Bell, label: "Price Alerts", href: "/dashboard/alerts", active: false },
  { icon: Settings, label: "Settings", href: "/dashboard/settings", active: false },
];

interface AddProductForm {
  name: string;
  brand: string;
  category: string;
  description: string;
  base_price: string;
  ean: string;
  image_url: string;
}

const EMPTY_FORM: AddProductForm = {
  name: "",
  brand: "",
  category: "",
  description: "",
  base_price: "",
  ean: "",
  image_url: "",
};

export default function ProductsPage() {
  const { user, logout } = useAuth();
  const searchParams = useSearchParams();
  const initQuery = searchParams.get("q") || "";

  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(initQuery);
  const [isSearching, setIsSearching] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<AddProductForm>(EMPTY_FORM);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  const loadProducts = useCallback(async (query?: string) => {
    try {
      setIsSearching(true);
      const url = query
        ? `/products?query=${encodeURIComponent(query)}&limit=100`
        : "/products?limit=100";
      const res = await apiClient.get(url);
      setProducts(res.data.data || []);
    } catch {
      setProducts([]);
    } finally {
      setIsSearching(false);
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;

    async function fetchProductsAsync() {
      try {
        const url = initQuery
          ? `/products?query=${encodeURIComponent(initQuery)}&limit=100`
          : "/products?limit=100";
        const res = await apiClient.get(url);
        if (!isCancelled) {
          setProducts(res.data.data || []);
        }
      } catch {
        if (!isCancelled) {
          setProducts([]);
        }
      } finally {
        if (!isCancelled) {
          setIsSearching(false);
          setIsLoading(false);
        }
      }
    }

    fetchProductsAsync();

    return () => {
      isCancelled = true;
    };
  }, [initQuery]);

  const handleSearchChange = (val: string) => {
    setSearchQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      loadProducts(val || undefined);
    }, 400);
  };

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setIsSubmitting(true);
    try {
      const payload = {
        name: form.name,
        brand: form.brand || undefined,
        category: form.category || undefined,
        description: form.description || undefined,
        base_price: form.base_price ? parseFloat(form.base_price) : undefined,
        ean: form.ean || undefined,
        image_url: form.image_url || undefined,
      };
      await apiClient.post("/products", payload);
      setShowModal(false);
      setForm(EMPTY_FORM);
      loadProducts(searchQuery || undefined);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      setSubmitError(e?.response?.data?.detail || "Failed to create product.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "??";

  return (
    <AuthGuard>
      <div
        className="min-h-screen flex"
        style={{ background: "var(--background)", paddingTop: "64px" }}
      >
        {/* Sidebar */}
        <aside
          className="hidden lg:flex flex-col w-64 border-r h-[calc(100vh-64px)] sticky top-16"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="p-4 border-b" style={{ borderColor: "var(--border)" }}>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl gradient-bg flex items-center justify-center flex-shrink-0 text-white font-bold text-sm">
                {initials}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold truncate" style={{ color: "var(--foreground)" }}>
                  {user?.name || "User"}
                </p>
                <p className="text-xs truncate" style={{ color: "var(--foreground-muted)" }}>
                  {user?.email || ""}
                </p>
              </div>
            </div>
          </div>

          <div className="flex-1 p-4 space-y-1 mt-2">
            {sidebarItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  item.active ? "gradient-bg text-white" : "hover:text-indigo-400"
                }`}
                style={item.active ? {} : { color: "var(--foreground-muted)" }}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </div>

          <div className="p-4 border-t" style={{ borderColor: "var(--border)" }}>
            <button
              onClick={logout}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium w-full transition-colors hover:text-red-400"
              style={{ color: "var(--foreground-muted)" }}
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
                  Products
                </h1>
                <p className="text-sm mt-0.5" style={{ color: "var(--foreground-muted)" }}>
                  {products.length} product{products.length !== 1 ? "s" : ""} in your index
                </p>
              </div>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowModal(true)}
                id="add-product-btn"
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl gradient-bg text-white text-sm font-semibold"
                style={{ boxShadow: "0 4px 15px rgba(99,102,241,0.3)" }}
              >
                <Plus className="h-4 w-4" />
                Add Product
              </motion.button>
            </div>

            {/* Search */}
            <div className="relative mb-6">
              <Search
                className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4"
                style={{ color: "var(--foreground-muted)" }}
              />
              <input
                type="text"
                id="products-search"
                value={searchQuery}
                onChange={(e) => handleSearchChange(e.target.value)}
                placeholder="Search products by name…"
                className="w-full pl-11 pr-4 py-3 rounded-xl text-sm"
                style={{
                  background: "var(--card)",
                  border: "1px solid var(--border)",
                  color: "var(--foreground)",
                }}
              />
              {isSearching && (
                <Loader2
                  className="absolute right-4 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin"
                  style={{ color: "var(--foreground-muted)" }}
                />
              )}
            </div>

            {/* Product Grid */}
            {isLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {[...Array(6)].map((_, i) => (
                  <div
                    key={i}
                    className="rounded-2xl p-5 border animate-pulse"
                    style={{ background: "var(--card)", borderColor: "var(--border)", height: "160px" }}
                  />
                ))}
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-20">
                <div
                  className="inline-flex h-16 w-16 rounded-2xl items-center justify-center mb-4"
                  style={{ background: "rgba(99,102,241,0.1)" }}
                >
                  <Package className="h-8 w-8" style={{ color: "var(--brand-primary)" }} />
                </div>
                <p className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                  {searchQuery ? "No products found" : "No products yet"}
                </p>
                <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
                  {searchQuery
                    ? `No results for "${searchQuery}"`
                    : "Click 'Add Product' to start building your index."}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {products.map((product, i) => (
                  <motion.div
                    key={product.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04 }}
                  >
                    <Link
                      href={`/products/${product.id}`}
                      className="block rounded-2xl p-5 border transition-all duration-200 hover:border-indigo-500 hover:shadow-lg group"
                      style={{ background: "var(--card)", borderColor: "var(--border)" }}
                    >
                      <div
                        className="h-12 w-12 rounded-xl flex items-center justify-center mb-4"
                        style={{ background: "rgba(99,102,241,0.1)" }}
                      >
                        {product.image_url ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="h-10 w-10 object-contain rounded-lg"
                          />
                        ) : (
                          <ShoppingBag className="h-5 w-5" style={{ color: "var(--brand-primary)" }} />
                        )}
                      </div>

                      <p
                        className="text-sm font-semibold leading-snug line-clamp-2 mb-2"
                        style={{ color: "var(--foreground)" }}
                      >
                        {product.name}
                      </p>

                      <div className="flex items-center justify-between">
                        <div className="flex flex-wrap gap-1">
                          {product.brand && (
                            <span
                              className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full"
                              style={{ background: "rgba(99,102,241,0.1)", color: "var(--brand-primary)" }}
                            >
                              <Tag className="h-2.5 w-2.5" />
                              {product.brand}
                            </span>
                          )}
                          {product.category && (
                            <span
                              className="text-xs px-2 py-0.5 rounded-full"
                              style={{ background: "var(--background)", color: "var(--foreground-muted)" }}
                            >
                              {product.category}
                            </span>
                          )}
                        </div>
                        {product.base_price && (
                          <span className="text-sm font-bold gradient-text ml-2 flex-shrink-0">
                            ₹{Number(product.base_price).toLocaleString("en-IN")}
                          </span>
                        )}
                      </div>

                      <div
                        className="flex items-center gap-1 text-xs mt-3 group-hover:text-indigo-400 transition-colors"
                        style={{ color: "var(--foreground-muted)" }}
                      >
                        <span>Compare prices</span>
                        <ChevronRight className="h-3 w-3" />
                      </div>
                    </Link>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Add Product Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center px-4"
            style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
            onClick={(e) => { if (e.target === e.currentTarget) setShowModal(false); }}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-lg rounded-2xl border p-6"
              style={{ background: "var(--card)", borderColor: "var(--border)" }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold" style={{ color: "var(--foreground)" }}>
                  Add Product
                </h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-1.5 rounded-lg hover:opacity-70"
                  style={{ color: "var(--foreground-muted)" }}
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {submitError && (
                <div
                  className="flex items-start gap-2 rounded-xl px-4 py-3 mb-4 text-sm"
                  style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#f87171" }}
                >
                  <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  {submitError}
                </div>
              )}

              <form onSubmit={handleAddProduct} className="space-y-4" id="add-product-form">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: "var(--foreground)" }}>
                    Product name <span className="text-red-400">*</span>
                  </label>
                  <input
                    required
                    value={form.name}
                    onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                    placeholder="e.g. Samsung Galaxy S24 Ultra"
                    className="w-full px-4 py-2.5 text-sm rounded-xl"
                    style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                    disabled={isSubmitting}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1.5" style={{ color: "var(--foreground)" }}>
                      Brand
                    </label>
                    <input
                      value={form.brand}
                      onChange={(e) => setForm((f) => ({ ...f, brand: e.target.value }))}
                      placeholder="e.g. Samsung"
                      className="w-full px-4 py-2.5 text-sm rounded-xl"
                      style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                      disabled={isSubmitting}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1.5" style={{ color: "var(--foreground)" }}>
                      Category
                    </label>
                    <input
                      value={form.category}
                      onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                      placeholder="e.g. Smartphones"
                      className="w-full px-4 py-2.5 text-sm rounded-xl"
                      style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                      disabled={isSubmitting}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1.5" style={{ color: "var(--foreground)" }}>
                      Base Price (₹)
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={form.base_price}
                      onChange={(e) => setForm((f) => ({ ...f, base_price: e.target.value }))}
                      placeholder="0.00"
                      className="w-full px-4 py-2.5 text-sm rounded-xl"
                      style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                      disabled={isSubmitting}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1.5" style={{ color: "var(--foreground)" }}>
                      EAN / Barcode
                    </label>
                    <input
                      value={form.ean}
                      onChange={(e) => setForm((f) => ({ ...f, ean: e.target.value }))}
                      placeholder="Optional"
                      className="w-full px-4 py-2.5 text-sm rounded-xl"
                      style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                      disabled={isSubmitting}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: "var(--foreground)" }}>
                    Description
                  </label>
                  <textarea
                    rows={2}
                    value={form.description}
                    onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                    placeholder="Brief product description (optional)"
                    className="w-full px-4 py-2.5 text-sm rounded-xl resize-none"
                    style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                    disabled={isSubmitting}
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 py-2.5 rounded-xl text-sm font-medium border transition-colors hover:opacity-80"
                    style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
                    disabled={isSubmitting}
                  >
                    Cancel
                  </button>
                  <motion.button
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    type="submit"
                    id="submit-product"
                    disabled={isSubmitting}
                    className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold gradient-bg text-white disabled:opacity-70"
                  >
                    {isSubmitting ? (
                      <><Loader2 className="h-4 w-4 animate-spin" /> Adding…</>
                    ) : (
                      <><Plus className="h-4 w-4" /> Add Product</>
                    )}
                  </motion.button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AuthGuard>
  );
}
