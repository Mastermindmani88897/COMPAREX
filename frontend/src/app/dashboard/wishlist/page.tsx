"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Heart,
  LayoutDashboard,
  ShoppingBag,
  Bell,
  Settings,
  LogOut,
  Search,
  SlidersHorizontal,
  ArrowUpDown,
  TrendingDown,
  ExternalLink,
  GitCompare,
  Sparkles,
  Loader2,
  Trash2,
  Plus,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useWishlist } from "@/context/WishlistContext";
import { AuthGuard } from "@/components/shared/AuthGuard";
import apiClient from "@/services/api";
import { getUserDisplayName, getUserInitials } from "@/utils/user";
import { ProductActionButtons } from "@/components/products/ProductActionButtons";

interface WishlistItem {
  id: string;
  user_id: string;
  product_id: string;
  preferred_marketplace?: string;
  target_price?: number;
  current_price?: number;
  savings?: number;
  price_drop_alert: boolean;
  notes?: string;
  created_at: string;
  product?: {
    id: string;
    name: string;
    brand?: string;
    category?: string;
    image_url?: string;
    base_price?: number;
    listings?: Array<{ listing_url?: string }>;
  };
}

interface AIRecommendationItem {
  id?: string;
  product_id?: string;
  title: string;
  name?: string;
  brand?: string;
  category?: string;
  price: number;
  image_url?: string;
  rating?: number;
  marketplace?: string;
  listing_url?: string | null;
  savings?: string;
  reason?: string;
}

const sidebarItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/dashboard", active: false },
  { icon: Heart, label: "Wishlist & Favorites", href: "/dashboard/wishlist", active: true },
  { icon: ShoppingBag, label: "My Products", href: "/products", active: false },
  { icon: Bell, label: "Price Alerts", href: "/dashboard#alerts", active: false },
  { icon: Settings, label: "Settings", href: "/dashboard/settings", active: false },
];

export default function WishlistDashboardPage() {
  const { user, logout } = useAuth();
  const { removeFromWishlist } = useWishlist();
  const [items, setItems] = useState<WishlistItem[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [totalSavings, setTotalSavings] = useState<number>(0);
  const [aiRecs, setAiRecs] = useState<{
    you_may_also_like: AIRecommendationItem[];
    cheaper_alternative: AIRecommendationItem[];
    best_value: AIRecommendationItem[];
  }>({
    you_may_also_like: [],
    cheaper_alternative: [],
    best_value: [],
  });

  const [categories, setCategories] = useState<{ id: string; name: string }[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("date_added");

  useEffect(() => {
    let isCancelled = false;
    apiClient
      .get("/categories")
      .then((res) => {
        if (!isCancelled && res.data?.data) {
          setCategories(res.data.data);
        }
      })
      .catch(() => {});
    return () => {
      isCancelled = true;
    };
  }, []);

  const loadWishlist = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchQuery.trim()) params.append("search", searchQuery.trim());
      if (selectedCategory !== "all") params.append("category", selectedCategory);
      if (sortBy) params.append("sort_by", sortBy);

      const res = await apiClient.get(`/wishlist?${params.toString()}`);
      const data = res.data?.data;
      if (data) {
        setItems(data.items || []);
        setTotalItems(data.total_items || 0);
        setTotalSavings(Number(data.total_savings || 0));
        if (data.ai_recommendations) {
          setAiRecs(data.ai_recommendations);
        }
      }
    } catch (err) {
      console.error("Failed to load wishlist:", err);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, selectedCategory, sortBy]);

  useEffect(() => {
    loadWishlist();

    const handleUpdate = () => {
      loadWishlist();
    };
    window.addEventListener("wishlist:updated", handleUpdate);
    return () => window.removeEventListener("wishlist:updated", handleUpdate);
  }, [loadWishlist]);

  const handleRemoveItem = async (itemId: string, productId?: string) => {
    try {
      setItems((prev) => prev.filter((i) => i.id !== itemId && i.product_id !== productId));
      setTotalItems((prev) => Math.max(0, prev - 1));
      await removeFromWishlist(itemId);
    } catch (err) {
      console.error("Failed to remove item:", err);
    }
  };

  const displayName = getUserDisplayName(user);
  const initials = getUserInitials(user);

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
              {user?.avatar_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={user.avatar_url}
                  alt={displayName}
                  className="h-10 w-10 rounded-xl object-cover shrink-0"
                />
              ) : (
                <div className="h-10 w-10 rounded-xl gradient-bg flex items-center justify-center shrink-0 text-white font-bold text-sm">
                  {initials}
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold truncate" style={{ color: "var(--foreground)" }}>
                  {displayName}
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

        {/* Main Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-8">
            {/* Header Banner */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <motion.h1
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-3xl font-bold flex items-center gap-3"
                  style={{ color: "var(--foreground)" }}
                >
                  <Heart className="h-8 w-8 text-rose-500 fill-rose-500" /> My Wishlist & Favorites
                </motion.h1>
                <p className="mt-1 text-sm" style={{ color: "var(--foreground-muted)" }}>
                  Track your saved products, target price alerts, and live market savings.
                </p>
              </div>

              <Link
                href="/products"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold gradient-bg text-white shadow-md hover:opacity-90 transition-opacity w-fit"
              >
                <Plus className="h-4 w-4" /> Add Products
              </Link>
            </div>

            {/* Overview Stats Bar */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              <div className="rounded-2xl p-5 border" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                <span className="text-xs font-semibold block" style={{ color: "var(--foreground-muted)" }}>
                  Saved Items
                </span>
                <p className="text-3xl font-black text-rose-500">{totalItems}</p>
              </div>

              <div className="rounded-2xl p-5 border" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                <span className="text-xs font-semibold block" style={{ color: "var(--foreground-muted)" }}>
                  Live Price Drop Savings
                </span>
                <p className="text-3xl font-black text-emerald-400">₹{totalSavings.toLocaleString("en-IN")}</p>
              </div>

              <div className="rounded-2xl p-5 border" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                <span className="text-xs font-semibold block" style={{ color: "var(--foreground-muted)" }}>
                  Active Price Alerts Sync
                </span>
                <p className="text-3xl font-black text-indigo-400">{items.filter((i) => i.price_drop_alert).length} Alerts Triggered</p>
              </div>
            </div>

            {/* Search & Filter Toolbar */}
            <div className="rounded-2xl p-4 border space-y-4 md:space-y-0 md:flex md:items-center md:gap-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <div className="relative flex-1">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search wishlist items..."
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm"
                  style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                />
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-2">
                  <SlidersHorizontal className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="py-2.5 px-3 rounded-xl text-sm font-medium border"
                    style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                  >
                    <option value="all">All Categories</option>
                    {categories.length > 0
                      ? categories.map((cat) => (
                          <option key={cat.id} value={cat.name.toLowerCase()}>
                            {cat.name}
                          </option>
                        ))
                      : (
                        <>
                          <option value="mobiles">Mobiles</option>
                          <option value="laptops">Laptops</option>
                          <option value="headphones">Headphones</option>
                          <option value="electronics">Electronics</option>
                        </>
                      )}
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <ArrowUpDown className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="py-2.5 px-3 rounded-xl text-sm font-medium border"
                    style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                  >
                    <option value="date_added">Date Added</option>
                    <option value="price_low">Price: Low to High</option>
                    <option value="price_high">Price: High to Low</option>
                    <option value="price_drop">Max Price Savings</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Wishlist Items List */}
            {isLoading ? (
              <div className="text-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-400 mx-auto" />
              </div>
            ) : items.length === 0 ? (
              <div className="text-center py-20 rounded-3xl border p-8 space-y-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                <Heart className="h-14 w-14 text-rose-500/50 mx-auto" />
                <h3 className="text-xl font-bold" style={{ color: "var(--foreground)" }}>
                  Your Wishlist is Empty
                </h3>
                <p className="text-sm max-w-md mx-auto" style={{ color: "var(--foreground-muted)" }}>
                  Browse our catalog and click the heart icon on any product to start tracking prices.
                </p>
                <Link href="/products" className="inline-block px-5 py-2.5 rounded-xl gradient-bg text-white text-sm font-semibold">
                  Browse Catalog
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {items.map((item) => {
                  const prod = item.product;
                  if (!prod) return null;
                  const currentP = Number(item.current_price || prod.base_price || 0);
                  const targetP = Number(item.target_price || currentP);

                  return (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-5 rounded-2xl border flex flex-col md:flex-row md:items-center md:justify-between gap-6 shadow-sm hover:border-indigo-500/50 transition-colors"
                      style={{ background: "var(--card)", borderColor: "var(--border)" }}
                    >
                      <div className="flex items-center gap-4">
                        <div className="h-20 w-20 rounded-2xl bg-white p-2 border flex items-center justify-center shrink-0">
                          {prod.image_url ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img src={prod.image_url} alt={prod.name} className="h-full w-full object-contain" />
                          ) : (
                            <ShoppingBag className="h-8 w-8 text-indigo-400" />
                          )}
                        </div>

                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 font-semibold">
                              {prod.brand || "Brand"}
                            </span>
                            {item.price_drop_alert && (
                              <span className="inline-flex items-center gap-1 text-[11px] font-black px-2.5 py-0.5 rounded-full bg-emerald-500 text-white">
                                <TrendingDown className="h-3 w-3" /> PRICE DROP ALERT!
                              </span>
                            )}
                          </div>

                          <h3 className="text-base font-bold line-clamp-1" style={{ color: "var(--foreground)" }}>
                            {prod.name}
                          </h3>

                          <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                            Preferred Marketplace: <span className="font-semibold text-indigo-400">{item.preferred_marketplace || "Amazon"}</span>
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between md:justify-end gap-6 border-t md:border-t-0 pt-4 md:pt-0" style={{ borderColor: "var(--border)" }}>
                        <div className="text-left md:text-right">
                          <span className="text-xs block" style={{ color: "var(--foreground-muted)" }}>Current Price</span>
                          <p className="text-xl font-extrabold text-emerald-400">
                            ₹{currentP.toLocaleString("en-IN")}
                          </p>
                          <span className="text-[11px] text-amber-400">
                            Target: ₹{targetP.toLocaleString("en-IN")}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <Link
                            href={`/products/${prod.id}`}
                            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border hover:border-indigo-500 transition-colors"
                            style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
                          >
                            <GitCompare className="h-3.5 w-3.5" /> Compare
                          </Link>

                          <a
                            href={prod.listings?.[0]?.listing_url || `/products/${prod.id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold gradient-bg text-white"
                          >
                            Buy Now <ExternalLink className="h-3.5 w-3.5" />
                          </a>

                          <button
                            onClick={() => handleRemoveItem(item.id, item.product_id)}
                            className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                            title="Remove from Wishlist"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}

            {/* AI Recommendations Section */}
            {aiRecs && (
              <div className="rounded-3xl border p-6 sm:p-8 space-y-6 shadow-xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                <div className="flex items-center gap-3 border-b pb-4" style={{ borderColor: "var(--border)" }}>
                  <Sparkles className="h-6 w-6 text-purple-400 animate-pulse" />
                  <div>
                    <h2 className="text-xl font-bold" style={{ color: "var(--foreground)" }}>
                      AI Wishlist Recommendations
                    </h2>
                    <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                      Personalized deals, cheaper alternatives, and best value picks.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* You May Also Like */}
                  <div className="space-y-3 p-4 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                    <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">You May Also Like</h3>
                    {aiRecs.you_may_also_like && aiRecs.you_may_also_like.length > 0 ? (
                      aiRecs.you_may_also_like.map((rec, i) => (
                        <div key={rec.id || i} className="p-3.5 rounded-xl border space-y-2" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                          <p className="text-xs font-bold line-clamp-1" style={{ color: "var(--foreground)" }}>{rec.title || rec.name}</p>
                          <p className="text-xs text-emerald-400 font-extrabold">₹{Number(rec.price).toLocaleString("en-IN")}</p>
                          {rec.reason && <p className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>{rec.reason}</p>}
                          <ProductActionButtons product={{ id: rec.id || rec.product_id || "", name: rec.title || rec.name, price: rec.price, listing_url: rec.listing_url }} compact />
                        </div>
                      ))
                    ) : (
                      <p className="text-xs italic" style={{ color: "var(--foreground-muted)" }}>No recommendations available yet.</p>
                    )}
                  </div>

                  {/* Cheaper Alternative */}
                  <div className="space-y-3 p-4 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                    <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Cheaper Alternative</h3>
                    {aiRecs.cheaper_alternative && aiRecs.cheaper_alternative.length > 0 ? (
                      aiRecs.cheaper_alternative.map((rec, i) => (
                        <div key={rec.id || i} className="p-3.5 rounded-xl border space-y-2" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                          <p className="text-xs font-bold line-clamp-1" style={{ color: "var(--foreground)" }}>{rec.title || rec.name}</p>
                          <p className="text-xs text-emerald-400 font-extrabold">₹{Number(rec.price).toLocaleString("en-IN")}</p>
                          {rec.reason && <p className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>{rec.reason}</p>}
                          <ProductActionButtons product={{ id: rec.id || rec.product_id || "", name: rec.title || rec.name, price: rec.price, listing_url: rec.listing_url }} compact />
                        </div>
                      ))
                    ) : (
                      <p className="text-xs italic" style={{ color: "var(--foreground-muted)" }}>No cheaper alternatives found.</p>
                    )}
                  </div>

                  {/* Best Value */}
                  <div className="space-y-3 p-4 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                    <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Best Value</h3>
                    {aiRecs.best_value && aiRecs.best_value.length > 0 ? (
                      aiRecs.best_value.map((rec, i) => (
                        <div key={rec.id || i} className="p-3.5 rounded-xl border space-y-2" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                          <p className="text-xs font-bold line-clamp-1" style={{ color: "var(--foreground)" }}>{rec.title || rec.name}</p>
                          <p className="text-xs text-emerald-400 font-extrabold">₹{Number(rec.price).toLocaleString("en-IN")}</p>
                          {rec.reason && <p className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>{rec.reason}</p>}
                          <ProductActionButtons product={{ id: rec.id || rec.product_id || "", name: rec.title || rec.name, price: rec.price, listing_url: rec.listing_url }} compact />
                        </div>
                      ))
                    ) : (
                      <p className="text-xs italic" style={{ color: "var(--foreground-muted)" }}>No best value picks available yet.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
