"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  ShoppingBag,
  Bell,
  Settings,
  LogOut,
  Search,
  User,
  ChevronRight,
  Package,
  Heart,
  GitCompare,
  ArrowUpRight,
  Clock,
  SlidersHorizontal,
  TrendingDown,
  Trash2,
  Edit,
  Plus,
  Tag,
  RefreshCw,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useWishlist } from "@/context/WishlistContext";
import { AuthGuard } from "@/components/shared/AuthGuard";
import apiClient, { alertsService } from "@/services/api";
import type { Product, PriceAlertItem } from "@/types";
import { getUserDisplayName, getUserFirstName, getUserInitials } from "@/utils/user";
import { PriceAlertModal } from "@/components/alerts/PriceAlertModal";

const sidebarItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/dashboard", active: true },
  { icon: Heart, label: "Wishlist & Favorites", href: "/dashboard/wishlist", active: false },
  { icon: Bell, label: "Price Alerts", href: "/dashboard/alerts", active: false },
  { icon: ShoppingBag, label: "Catalog Products", href: "/products", active: false },
  { icon: Settings, label: "Settings", href: "/dashboard/settings", active: false },
];

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { wishlistItems, wishlistCount, refetchWishlist } = useWishlist();
  const [productCount, setProductCount] = useState<number | null>(null);
  const [recentProducts, setRecentProducts] = useState<Product[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  // Dynamic DB Dashboard States
  const [dashboardStats, setDashboardStats] = useState<{
    total_money_saved: number;
    coupon_savings: number;
    active_alerts_count: number;
    wishlist_count: number;
    tracked_products_count: number;
  }>({
    total_money_saved: 0,
    coupon_savings: 0,
    active_alerts_count: 0,
    wishlist_count: 0,
    tracked_products_count: 0,
  });

  const [priceAlerts, setPriceAlerts] = useState<PriceAlertItem[]>([]);
  const [activeAlertProduct, setActiveAlertProduct] = useState<Product | null>(null);

  const fetchDashboardData = async () => {
    setIsLoadingStats(true);
    try {
      // 1. Fetch dynamic summary stats from DB
      const sumRes = await apiClient.get("/dashboard/summary");
      if (sumRes.data?.data?.stats) {
        setDashboardStats(sumRes.data.data.stats);
      }

      // 2. Refresh wishlist context
      await refetchWishlist();

      // 3. Fetch user price alerts
      const alRes = await alertsService.getAlerts();
      if (alRes.data?.data) {
        setPriceAlerts(alRes.data.data);
      } else {
        setPriceAlerts([]);
      }

      // 4. Fetch catalog sample
      const prodRes = await apiClient.get("/products?skip=0&limit=4");
      setRecentProducts(prodRes.data?.data || []);
      const countRes = await apiClient.get("/products?skip=0&limit=100");
      setProductCount(countRes.data?.data?.length || 0);

    } catch (err) {
      console.error("Dashboard dynamic load error:", err);
    } finally {
      setIsLoadingStats(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();

    const handleUpdate = () => {
      fetchDashboardData();
    };
    window.addEventListener("wishlist:updated", handleUpdate);
    return () => window.removeEventListener("wishlist:updated", handleUpdate);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/products?q=${encodeURIComponent(searchQuery)}`;
    }
  };

  const toggleAlert = async (id: string, currentActive: boolean) => {
    try {
      await alertsService.updateAlert(id, { is_active: !currentActive });
      fetchDashboardData();
    } catch (err) {
      console.error("Toggle alert error:", err);
    }
  };

  const deleteAlert = async (id: string) => {
    try {
      await alertsService.deleteAlert(id);
      fetchDashboardData();
    } catch (err) {
      console.error("Delete alert error:", err);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "morning";
    if (hour < 18) return "afternoon";
    return "evening";
  };

  const initials = getUserInitials(user);
  const displayName = getUserDisplayName(user);
  const firstName = getUserFirstName(user);

  return (
    <AuthGuard>
      <div
        className="min-h-screen flex"
        style={{ background: "var(--background)", paddingTop: "64px" }}
      >
        {activeAlertProduct && (
          <PriceAlertModal
            isOpen={Boolean(activeAlertProduct)}
            onClose={() => {
              setActiveAlertProduct(null);
              fetchDashboardData();
            }}
            productId={activeAlertProduct.id}
            productName={activeAlertProduct.name}
            currentPrice={Number(activeAlertProduct.base_price) || 19999}
          />
        )}

        {/* Sidebar */}
        <aside
          className="hidden lg:flex flex-col w-64 border-r h-[calc(100vh-64px)] sticky top-16"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="p-4 border-b" style={{ borderColor: "var(--border)" }}>
            <div className="flex items-center gap-3">
              {user?.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={displayName}
                  className="h-10 w-10 rounded-xl object-cover flex-shrink-0"
                />
              ) : (
                <div className="h-10 w-10 rounded-xl gradient-bg flex items-center justify-center flex-shrink-0 text-white font-bold text-sm">
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
                  item.active ? "gradient-bg text-white shadow-md" : "hover:text-indigo-400"
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

        {/* Main Dashboard Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-8">
            {/* Header Banner */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <motion.h1
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-3xl font-bold"
                  style={{ color: "var(--foreground)" }}
                >
                  Good {getGreeting()},{" "}
                  <span className="gradient-text">
                    {firstName}!
                  </span>
                </motion.h1>
                <p className="mt-1 text-sm" style={{ color: "var(--foreground-muted)" }}>
                  Dynamic real-time overview calculated directly from backend database.
                </p>
              </div>

              <button
                onClick={fetchDashboardData}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold border hover:border-indigo-500 transition-colors w-fit"
                style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isLoadingStats ? "animate-spin text-indigo-400" : ""}`} /> Sync Dashboard
              </button>
            </div>

            {/* Quick Search */}
            <motion.form
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              onSubmit={handleSearch}
              className="relative"
            >
              <Search
                className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5"
                style={{ color: "var(--foreground-muted)" }}
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for any product to compare live prices across top stores…"
                className="w-full pl-12 pr-28 py-4 rounded-2xl text-sm"
                style={{
                  background: "var(--card)",
                  border: "1px solid var(--border)",
                  color: "var(--foreground)",
                }}
              />
              <button
                type="submit"
                className="absolute right-3 top-1/2 -translate-y-1/2 px-4 py-2 rounded-xl gradient-bg text-white text-sm font-medium"
              >
                Search
              </button>
            </motion.form>

            {/* Dynamic Overview Stats (Zero Hardcoding) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {/* Money Saved */}
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl p-5 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold" style={{ color: "var(--foreground-muted)" }}>
                    Total Money Saved
                  </span>
                  <Package className="h-4 w-4 text-emerald-400" />
                </div>
                <p className="text-2xl font-black text-emerald-400">
                  ₹{Number(dashboardStats.total_money_saved || 0).toLocaleString("en-IN")}
                </p>
                <span className="text-[10px] text-slate-400">
                  Calculated from target price drops
                </span>
              </motion.div>

              {/* Active Alerts */}
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className="rounded-2xl p-5 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold" style={{ color: "var(--foreground-muted)" }}>
                    Active Price Alerts
                  </span>
                  <Bell className="h-4 w-4 text-amber-400" />
                </div>
                <p className="text-2xl font-black text-amber-400">
                  {priceAlerts.filter((a) => a.is_active).length}
                </p>
                <span className="text-[10px] text-slate-400">
                  {priceAlerts.length} total alert rules
                </span>
              </motion.div>

              {/* Coupon Savings */}
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="rounded-2xl p-5 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold" style={{ color: "var(--foreground-muted)" }}>
                    Coupon Savings
                  </span>
                  <Tag className="h-4 w-4 text-indigo-400" />
                </div>
                <p className="text-2xl font-black text-indigo-400">
                  ₹{Number(dashboardStats.coupon_savings || 0).toLocaleString("en-IN")}
                </p>
                <span className="text-[10px] text-slate-400">Auto-applied promos</span>
              </motion.div>

              {/* Wishlist Count */}
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="rounded-2xl p-5 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold" style={{ color: "var(--foreground-muted)" }}>
                    Wishlist Items
                  </span>
                  <Heart className="h-4 w-4 text-rose-400" />
                </div>
                <p className="text-2xl font-black text-rose-400">
                  {wishlistItems.length}
                </p>
                <span className="text-[10px] text-slate-400">
                  {dashboardStats.tracked_products_count || wishlistItems.length} tracked products
                </span>
              </motion.div>
            </div>

            {/* Main Grid — Dynamic Widgets */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column */}
              <div className="lg:col-span-2 space-y-6">
                {/* Recent Searches */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-2xl border p-6"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-indigo-400" />
                      <h2 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                        Popular Catalog Searches
                      </h2>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {[
                      "iPhone 15 Pro Max",
                      "Poco X5 Pro",
                      "Samsung Galaxy S25 Ultra",
                      "MacBook Air M4",
                      "Sony WH-1000XM5",
                    ].map((q) => (
                      <Link
                        key={q}
                        href={`/products?q=${encodeURIComponent(q)}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors hover:border-indigo-500 hover:text-indigo-400"
                        style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                      >
                        <Search className="h-3 w-3" />
                        {q}
                      </Link>
                    ))}
                  </div>
                </motion.div>

                {/* Wishlist Widget */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="rounded-2xl border p-6 space-y-4"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Heart className="h-4 w-4 text-rose-400" />
                      <h2 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                        Wishlist & Saved Items
                      </h2>
                    </div>
                    <Link href="/dashboard/wishlist" className="text-xs font-bold text-indigo-400 hover:underline">
                      Manage Wishlist ({wishlistItems.length})
                    </Link>
                  </div>

                  {wishlistItems.length === 0 ? (
                    <div className="text-center py-8 border rounded-xl" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                      <Heart className="h-8 w-8 text-rose-400/40 mx-auto mb-2" />
                      <p className="text-xs font-bold" style={{ color: "var(--foreground)" }}>
                        Your wishlist is currently empty
                      </p>
                      <p className="text-[11px] mt-0.5" style={{ color: "var(--foreground-muted)" }}>
                        Click the ❤️ on any product card to bookmark it here!
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {wishlistItems.slice(0, 4).map((item) => {
                        const prod = item.product;
                        return (
                          <div
                            key={item.id}
                            className="flex items-center justify-between p-3.5 rounded-xl border hover:border-indigo-500/50 transition-colors"
                            style={{ background: "var(--background)", borderColor: "var(--border)" }}
                          >
                            <div className="flex items-center gap-3 min-w-0 flex-1">
                              <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center shrink-0">
                                {prod?.image_url ? (
                                  <img src={prod.image_url} alt={prod.name} className="h-8 w-8 object-contain" />
                                ) : (
                                  <ShoppingBag className="h-5 w-5 text-indigo-400" />
                                )}
                              </div>
                              <div className="min-w-0 flex-1">
                                <Link href={`/products/${prod?.id || item.product_id}`} className="text-xs font-bold hover:text-indigo-400 transition-colors line-clamp-1" style={{ color: "var(--foreground)" }}>
                                  {prod?.name || "Wishlist Item"}
                                </Link>
                                <p className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>
                                  Target: ₹{Number(item.target_price || prod?.base_price || 0).toLocaleString("en-IN")}
                                </p>
                              </div>
                            </div>

                            <div className="text-right ml-3 shrink-0">
                              <p className="text-xs font-black text-emerald-400">
                                ₹{Number(item.current_price || prod?.base_price || 0).toLocaleString("en-IN")}
                              </p>
                              <Link
                                href={`/products/${prod?.id || item.product_id}`}
                                className="text-[10px] font-bold text-indigo-400 hover:underline"
                              >
                                Compare
                              </Link>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </motion.div>
              </div>

              {/* Right Column — Price Alerts & Quick Actions */}
              <div className="space-y-6">
                {/* Price Alerts Widget */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15 }}
                  className="rounded-2xl border p-6 space-y-4"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Bell className="h-4 w-4 text-amber-400" />
                      <h2 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                        Price Alerts ({priceAlerts.length})
                      </h2>
                    </div>
                    <Link href="/dashboard/alerts" className="text-xs font-bold text-indigo-400 hover:underline">
                      Manage All
                    </Link>
                  </div>

                  {priceAlerts.length === 0 ? (
                    <div className="text-center py-8 border rounded-xl" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
                      <Bell className="h-8 w-8 text-amber-400/40 mx-auto mb-2" />
                      <p className="text-xs font-bold" style={{ color: "var(--foreground)" }}>
                        No price alerts set
                      </p>
                      <p className="text-[11px] mt-0.5" style={{ color: "var(--foreground-muted)" }}>
                        Click 🔔 on any product card to create a price alert!
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {priceAlerts.slice(0, 4).map((alert) => (
                        <div
                          key={alert.id}
                          className="p-3.5 rounded-xl border space-y-2"
                          style={{ background: "var(--background)", borderColor: "var(--border)" }}
                        >
                          <div className="flex items-start justify-between">
                            <p className="text-xs font-bold line-clamp-1" style={{ color: "var(--foreground)" }}>
                              {alert.product_name}
                            </p>
                            <button
                              onClick={() => toggleAlert(alert.id, alert.is_active)}
                              className={`px-2 py-0.5 text-[10px] font-bold rounded-full transition-colors ${
                                alert.is_active
                                  ? "bg-emerald-500/20 text-emerald-400"
                                  : "bg-gray-500/20 text-gray-400"
                              }`}
                            >
                              {alert.is_active ? "ACTIVE" : "PAUSED"}
                            </button>
                          </div>

                          <div className="flex items-center justify-between text-xs">
                            <span style={{ color: "var(--foreground-muted)" }}>
                              Current: ₹{Number(alert.current_price || 0).toLocaleString("en-IN")}
                            </span>
                            <span className="font-bold text-amber-400">
                              Target: ₹{Number(alert.target_price).toLocaleString("en-IN")}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>

                {/* Quick Navigation Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.25 }}
                  className="rounded-2xl border p-6 space-y-3"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
                    Quick Navigation
                  </h3>
                  <div className="space-y-2">
                    <Link
                      href="/products"
                      className="flex items-center justify-between p-3 rounded-xl border hover:border-indigo-500 transition-colors text-xs font-bold"
                      style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                    >
                      <span className="flex items-center gap-2">
                        <ShoppingBag className="h-4 w-4 text-indigo-400" />
                        Browse Catalog
                      </span>
                      <ChevronRight className="h-4 w-4" />
                    </Link>

                    <Link
                      href="/dashboard/wishlist"
                      className="flex items-center justify-between p-3 rounded-xl border hover:border-rose-500 transition-colors text-xs font-bold"
                      style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                    >
                      <span className="flex items-center gap-2">
                        <Heart className="h-4 w-4 text-rose-400" />
                        Wishlist Page
                      </span>
                      <ChevronRight className="h-4 w-4" />
                    </Link>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
