import type { Metadata } from "next";
import { LayoutDashboard, ShoppingBag, Bell, Settings, LogOut, Zap } from "lucide-react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Your COMPAREX dashboard — manage comparisons, alerts, and preferences.",
};

const sidebarItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/dashboard", active: true },
  { icon: ShoppingBag, label: "My Products", href: "/dashboard/products", active: false },
  { icon: Bell, label: "Price Alerts", href: "/dashboard/alerts", active: false },
  { icon: Settings, label: "Settings", href: "/dashboard/settings", active: false },
];

export default function DashboardPage() {
  return (
    <div
      className="min-h-screen flex"
      style={{ background: "var(--background)", paddingTop: "64px" }}
    >
      {/* Sidebar */}
      <aside
        className="hidden lg:flex flex-col w-64 border-r h-[calc(100vh-64px)] sticky top-16"
        style={{ background: "var(--card)", borderColor: "var(--border)" }}
      >
        <div className="flex-1 p-4 space-y-1 mt-4">
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
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium w-full transition-colors hover:text-red-400"
            style={{ color: "var(--foreground-muted)" }}
            id="dashboard-logout"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-10">
            <h1 className="text-3xl font-bold" style={{ color: "var(--foreground)" }}>
              Dashboard
            </h1>
            <p className="mt-1 text-sm" style={{ color: "var(--foreground-muted)" }}>
              Welcome back! Your shopping intelligence hub is ready.
            </p>
          </div>

          {/* Coming Soon Banner */}
          <div
            className="rounded-2xl p-8 text-center border"
            style={{
              background: "rgba(99,102,241,0.06)",
              borderColor: "rgba(99,102,241,0.2)",
            }}
          >
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl gradient-bg mb-4">
              <Zap className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold gradient-text mb-2">
              Dashboard Coming in Phase 2
            </h2>
            <p className="text-sm max-w-md mx-auto" style={{ color: "var(--foreground-muted)" }}>
              This is a placeholder layout. Full functionality — including product tracking,
              price alerts, AI recommendations, and analytics — will be implemented in Phase 2.
            </p>
          </div>

          {/* Placeholder Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-8">
            {["Products Tracked", "Active Alerts", "Money Saved"].map((label) => (
              <div
                key={label}
                className="rounded-xl p-6 border"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>{label}</p>
                <div
                  className="mt-2 h-8 w-20 rounded-lg animate-shimmer"
                  style={{ background: "var(--background-secondary)" }}
                />
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
