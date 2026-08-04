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
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { AuthGuard } from "@/components/shared/AuthGuard";
import apiClient from "@/services/api";
import type { Product } from "@/types";

const sidebarItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/dashboard", active: true },
  { icon: ShoppingBag, label: "My Products", href: "/products", active: false },
  { icon: Bell, label: "Price Alerts", href: "/dashboard#alerts", active: false },
  { icon: Settings, label: "Settings", href: "/dashboard/settings", active: false },
];

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [productCount, setProductCount] = useState<number | null>(null);
  const [recentProducts, setRecentProducts] = useState<Product[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  // Widget States (Phase 2 Dashboard Widgets)
  const [recentSearches] = useState<string[]>([
    "iPhone 15 Pro Max",
    "MacBook Pro M3",
    "Sony WH-1000XM5",
    "Samsung Galaxy S24 Ultra",
  ]);

  const [wishlist] = useState([
    {
      id: "w1",
      name: "Apple iPad Air (M2)",
      brand: "Apple",
      targetPrice: 54900,
      currentPrice: 57900,
    },
    {
      id: "w2",
      name: "Dell XPS 15 Laptop",
      brand: "Dell",
      targetPrice: 145000,
      currentPrice: 139900,
    },
  ]);

  const [savedComparisons] = useState([
    {
      id: "c1",
      title: "Flagship Smartphones 2026",
      items: ["iPhone 15 Pro", "Galaxy S24 Ultra", "Pixel 8 Pro"],
      updatedAt: "2 hours ago",
      bestPrice: "₹1,29,990",
    },
    {
      id: "c2",
      title: "Wireless ANC Headphones",
      items: ["Sony WH-1000XM5", "Bose QC Ultra", "AirPods Max"],
      updatedAt: "Yesterday",
      bestPrice: "₹24,990",
    },
  ]);

  const [priceAlerts, setPriceAlerts] = useState([
    {
      id: "a1",
      productName: "Sony PlayStation 5 Console",
      targetPrice: 44990,
      currentPrice: 49990,
      active: true,
      store: "Amazon India",
    },
    {
      id: "a2",
      productName: "Apple Watch Series 9",
      targetPrice: 38000,
      currentPrice: 37490,
      active: true,
      store: "Flipkart",
    },
  ]);

  useEffect(() => {
    let isCancelled = false;
    async function fetchStats() {
      try {
        const res = await apiClient.get("/products?skip=0&limit=5");
        const products: Product[] = res.data.data || [];
        if (!isCancelled) {
          setRecentProducts(products.slice(0, 4));
        }
        const allRes = await apiClient.get("/products?skip=0&limit=100");
        if (!isCancelled) {
          setProductCount((allRes.data.data || []).length);
        }
      } catch {
        if (!isCancelled) {
          setProductCount(0);
          setRecentProducts([]);
        }
      } finally {
        if (!isCancelled) {
          setIsLoadingStats(false);
        }
      }
    }
    fetchStats();
    return () => {
      isCancelled = true;
    };
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/products?q=${encodeURIComponent(searchQuery)}`;
    }
  };

  const toggleAlert = (id: string) => {
    setPriceAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, active: !a.active } : a))
    );
  };

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
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
                <p
                  className="text-sm font-semibold truncate"
                  style={{ color: "var(--foreground)" }}
                >
                  {user?.name || "User"}
                </p>
                <p
                  className="text-xs truncate"
                  style={{ color: "var(--foreground-muted)" }}
                >
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
                id={`sidebar-${item.label.toLowerCase().replace(/\s+/g, "-")}`}
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
              id="dashboard-logout"
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
            <div>
              <motion.h1
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-3xl font-bold"
                style={{ color: "var(--foreground)" }}
              >
                Good {getGreeting()},{" "}
                <span className="gradient-text">
                  {user?.name?.split(" ")[0] || "there"}!
                </span>
              </motion.h1>
              <p
                className="mt-1 text-sm"
                style={{ color: "var(--foreground-muted)" }}
              >
                Welcome to your COMPAREX Intelligence Dashboard.
              </p>
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
                id="dashboard-search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for any product to compare prices across stores…"
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

            {/* Overview Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl p-5 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                    Total Money Saved
                  </span>
                  <Package className="h-4 w-4 text-emerald-400" />
                </div>
                <p className="text-2xl font-bold text-emerald-400">
                  ₹4,250
                </p>
                <span className="text-[10px] text-slate-400">
                  {isLoadingStats ? "Loading catalog..." : `${productCount ?? 0} catalog products indexed`}
                </span>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className="rounded-2xl p-5 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                    Active Price Alerts
                  </span>
                  <Bell className="h-4 w-4 text-amber-400" />
                </div>
                <p className="text-2xl font-bold text-amber-400">
                  {priceAlerts.filter((a) => a.active).length}
                </p>
                <span className="text-[10px] text-slate-400">Target drops monitored</span>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="rounded-2xl p-5 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                    Coupon Savings
                  </span>
                  <GitCompare className="h-4 w-4 text-indigo-400" />
                </div>
                <p className="text-2xl font-bold text-indigo-400">
                  ₹1,500
                </p>
                <span className="text-[10px] text-slate-400">3 coupons auto-applied</span>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="rounded-2xl p-5 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                    Wishlist & Saved
                  </span>
                  <Heart className="h-4 w-4 text-rose-400" />
                </div>
                <p className="text-2xl font-bold text-rose-400">
                  {wishlist.length}
                </p>
                <span className="text-[10px] text-slate-400">Tracked products</span>
              </motion.div>
            </div>

            {/* Main Grid — Widgets */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column */}
              <div className="lg:col-span-2 space-y-6">
                {/* Recent Searches Widget */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-2xl border p-6"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-indigo-400" />
                      <h2 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                        Recent Searches
                      </h2>
                    </div>
                    <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                      Quick re-search
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {recentSearches.map((q) => (
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

                {/* Saved Products Preview */}
                {recentProducts.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.05 }}
                    className="rounded-2xl border p-6"
                    style={{ background: "var(--card)", borderColor: "var(--border)" }}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <ShoppingBag className="h-4 w-4 text-indigo-400" />
                        <h2 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                          Recent Products in Index
                        </h2>
                      </div>
                      <Link href="/products" className="text-xs font-medium text-indigo-400 hover:underline">
                        View All
                      </Link>
                    </div>

                    <div className="divide-y" style={{ borderColor: "var(--border)" }}>
                      {recentProducts.map((prod) => (
                        <Link
                          key={prod.id}
                          href={`/products/${prod.id}`}
                          className="flex items-center justify-between py-3 hover:opacity-80 transition-opacity"
                        >
                          <span className="text-sm font-medium" style={{ color: "var(--foreground)" }}>
                            {prod.name}
                          </span>
                          {prod.base_price && (
                            <span className="text-sm font-bold gradient-text">
                              ₹{Number(prod.base_price).toLocaleString("en-IN")}
                            </span>
                          )}
                        </Link>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* Wishlist & Saved Products Widget */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="rounded-2xl border p-6"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Heart className="h-4 w-4 text-rose-400" />
                      <h2 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                        Wishlist & Saved Items
                      </h2>
                    </div>
                    <Link href="/products" className="text-xs font-medium text-indigo-400 hover:underline">
                      Explore All
                    </Link>
                  </div>

                  <div className="space-y-3">
                    {wishlist.map((item) => {
                      const isPriceDropped = item.currentPrice <= item.targetPrice;
                      return (
                        <div
                          key={item.id}
                          className="flex items-center justify-between p-3.5 rounded-xl border"
                          style={{ background: "var(--background)", borderColor: "var(--border)" }}
                        >
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-lg gradient-bg flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                              {item.brand[0]}
                            </div>
                            <div>
                              <p className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
                                {item.name}
                              </p>
                              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                Target: ₹{item.targetPrice.toLocaleString("en-IN")}
                              </p>
                            </div>
                          </div>

                          <div className="text-right">
                            <p className="text-sm font-bold gradient-text">
                              ₹{item.currentPrice.toLocaleString("en-IN")}
                            </p>
                            {isPriceDropped && (
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full mt-0.5">
                                <TrendingDown className="h-3 w-3" /> Price Drop!
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </motion.div>

                {/* Saved Comparisons Widget */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="rounded-2xl border p-6"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <GitCompare className="h-4 w-4 text-emerald-400" />
                      <h2 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                        Saved Comparisons
                      </h2>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {savedComparisons.map((comp) => (
                      <div
                        key={comp.id}
                        className="p-4 rounded-xl border space-y-2"
                        style={{ background: "var(--background)", borderColor: "var(--border)" }}
                      >
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-semibold truncate" style={{ color: "var(--foreground)" }}>
                            {comp.title}
                          </p>
                          <ArrowUpRight className="h-4 w-4 text-indigo-400" />
                        </div>
                        <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                          {comp.items.join(" vs ")}
                        </p>
                        <div className="flex items-center justify-between pt-2 text-xs border-t" style={{ borderColor: "var(--border)" }}>
                          <span style={{ color: "var(--foreground-muted)" }}>Best: {comp.bestPrice}</span>
                          <span className="text-[10px] opacity-75">{comp.updatedAt}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </div>

              {/* Right Column */}
              <div className="space-y-6">
                {/* Price Alerts Widget */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15 }}
                  className="rounded-2xl border p-6"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Bell className="h-4 w-4 text-amber-400" />
                      <h2 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                        Price Alerts
                      </h2>
                    </div>
                    <SlidersHorizontal className="h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                  </div>

                  <div className="space-y-3">
                    {priceAlerts.map((alert) => (
                      <div
                        key={alert.id}
                        className="p-3.5 rounded-xl border space-y-2"
                        style={{ background: "var(--background)", borderColor: "var(--border)" }}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>
                              {alert.productName}
                            </p>
                            <p className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>
                              {alert.store}
                            </p>
                          </div>
                          <button
                            onClick={() => toggleAlert(alert.id)}
                            className={`px-2 py-0.5 text-[10px] font-bold rounded-full transition-colors ${
                              alert.active
                                ? "bg-emerald-500/20 text-emerald-400"
                                : "bg-gray-500/20 text-gray-400"
                            }`}
                          >
                            {alert.active ? "ACTIVE" : "PAUSED"}
                          </button>
                        </div>

                        <div className="flex items-center justify-between text-xs pt-1">
                          <span style={{ color: "var(--foreground-muted)" }}>
                            Current: ₹{alert.currentPrice.toLocaleString("en-IN")}
                          </span>
                          <span className="font-semibold text-amber-400">
                            Target: ₹{alert.targetPrice.toLocaleString("en-IN")}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* Quick Actions Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.25 }}
                  className="rounded-2xl border p-6"
                  style={{ background: "var(--card)", borderColor: "var(--border)" }}
                >
                  <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--foreground)" }}>
                    Quick Navigation
                  </h3>
                  <div className="space-y-2">
                    <Link
                      href="/products"
                      className="flex items-center justify-between p-3 rounded-xl border hover:border-indigo-500 transition-colors text-xs font-medium"
                      style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                    >
                      <span className="flex items-center gap-2">
                        <ShoppingBag className="h-4 w-4 text-indigo-400" />
                        Browse Catalog
                      </span>
                      <ChevronRight className="h-4 w-4" />
                    </Link>

                    <Link
                      href="/dashboard/settings"
                      className="flex items-center justify-between p-3 rounded-xl border hover:border-indigo-500 transition-colors text-xs font-medium"
                      style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                    >
                      <span className="flex items-center gap-2">
                        <User className="h-4 w-4 text-purple-400" />
                        Edit Profile
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

function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 17) return "afternoon";
  return "evening";
}
