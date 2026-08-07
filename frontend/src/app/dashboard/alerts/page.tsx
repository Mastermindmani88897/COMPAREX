"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Bell,
  Trash2,
  Edit2,
  Power,
  ChevronLeft,
  ShoppingBag,
  ExternalLink,
  Plus,
  RefreshCw,
  AlertCircle,
  Check,
} from "lucide-react";
import { alertsService } from "@/services/api";
import { AuthGuard } from "@/components/shared/AuthGuard";
import type { PriceAlertItem } from "@/types";

export default function PriceAlertsPage() {
  const [alerts, setAlerts] = useState<PriceAlertItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [editingAlert, setEditingAlert] = useState<PriceAlertItem | null>(null);
  const [newTargetPrice, setNewTargetPrice] = useState<number>(0);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const res = await alertsService.getAlerts();
      setAlerts(res.data?.data || []);
    } catch (err) {
      console.error("Error fetching price alerts:", err);
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleToggleStatus = async (alert: PriceAlertItem) => {
    try {
      await alertsService.updateAlert(alert.id, { is_active: !alert.is_active });
      setAlerts((prev) =>
        prev.map((a) => (a.id === alert.id ? { ...a, is_active: !a.is_active } : a))
      );
    } catch (err) {
      console.error("Error toggling alert status:", err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this price alert?")) return;
    try {
      await alertsService.deleteAlert(id);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      console.error("Error deleting alert:", err);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingAlert) return;
    try {
      await alertsService.updateAlert(editingAlert.id, { target_price: Number(newTargetPrice) });
      setAlerts((prev) =>
        prev.map((a) => (a.id === editingAlert.id ? { ...a, target_price: Number(newTargetPrice) } : a))
      );
      setEditingAlert(null);
    } catch (err) {
      console.error("Error updating target price:", err);
    }
  };

  return (
    <AuthGuard>
      <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-1 text-xs font-bold text-indigo-400 hover:underline mb-2"
              >
                <ChevronLeft className="h-3.5 w-3.5" /> Back to Dashboard
              </Link>
              <h1 className="text-3xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>
                Price Alerts Management
              </h1>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                Monitor active price drop rules across Amazon, Flipkart, Croma, Reliance & more.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={fetchAlerts}
                className="p-2.5 rounded-xl border hover:border-indigo-500 transition-colors"
                style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
                title="Refresh Alerts"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin text-indigo-400" : ""}`} />
              </button>

              <Link
                href="/products"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl gradient-bg text-white text-xs font-bold shadow-md hover:opacity-90 transition-opacity"
              >
                <Plus className="h-4 w-4" /> Create New Alert
              </Link>
            </div>
          </div>

          {/* Edit Modal */}
          {editingAlert && (
            <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
              <div className="max-w-md w-full rounded-3xl border p-6 space-y-4 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                <h3 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                  Edit Target Price
                </h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  {editingAlert.product_name}
                </p>

                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 font-bold text-sm text-indigo-400">₹</span>
                  <input
                    type="number"
                    value={newTargetPrice}
                    onChange={(e) => setNewTargetPrice(Number(e.target.value))}
                    className="w-full pl-8 pr-4 py-3 rounded-xl text-base font-bold border"
                    style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => setEditingAlert(null)}
                    className="px-4 py-2 rounded-xl text-xs font-bold border"
                    style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveEdit}
                    className="px-4 py-2 rounded-xl text-xs font-bold gradient-bg text-white"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Table / List View */}
          {isLoading ? (
            <div className="p-16 rounded-3xl border text-center space-y-3" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <RefreshCw className="h-8 w-8 animate-spin text-indigo-400 mx-auto" />
              <p className="text-xs font-semibold" style={{ color: "var(--foreground-muted)" }}>
                Loading your price alerts...
              </p>
            </div>
          ) : alerts.length === 0 ? (
            <div className="p-16 rounded-3xl border text-center space-y-4 shadow-xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <div className="h-16 w-16 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center mx-auto">
                <Bell className="h-8 w-8" />
              </div>
              <h3 className="text-lg font-bold" style={{ color: "var(--foreground)" }}>
                No active price alerts
              </h3>
              <p className="text-xs max-w-md mx-auto" style={{ color: "var(--foreground-muted)" }}>
                You haven't set any price drop alerts yet. Browse the product catalog and click 🔔 to set an alert!
              </p>
              <Link
                href="/products"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl gradient-bg text-white text-xs font-bold"
              >
                <ShoppingBag className="h-4 w-4" /> Browse Catalog
              </Link>
            </div>
          ) : (
            <div className="rounded-3xl border overflow-hidden shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b text-xs font-bold uppercase tracking-wider" style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}>
                      <th className="py-4 px-6">Product</th>
                      <th className="py-4 px-4">Marketplace</th>
                      <th className="py-4 px-4">Current Price</th>
                      <th className="py-4 px-4">Target Price</th>
                      <th className="py-4 px-4">Status</th>
                      <th className="py-4 px-6 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y" style={{ borderColor: "var(--border)" }}>
                    {alerts.map((alert) => (
                      <tr key={alert.id} className="hover:bg-indigo-500/5 transition-colors">
                        {/* Product Column */}
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className="h-12 w-12 rounded-xl bg-indigo-500/10 p-1 flex items-center justify-center shrink-0">
                              {alert.product_image ? (
                                <img src={alert.product_image} alt={alert.product_name} className="h-10 w-10 object-contain rounded-lg" />
                              ) : (
                                <ShoppingBag className="h-5 w-5 text-indigo-400" />
                              )}
                            </div>
                            <div>
                              <Link
                                href={`/products/${alert.product_id}`}
                                className="text-sm font-bold hover:text-indigo-400 transition-colors line-clamp-1"
                                style={{ color: "var(--foreground)" }}
                              >
                                {alert.product_name}
                              </Link>
                              <span className="text-[11px] block" style={{ color: "var(--foreground-muted)" }}>
                                Notification: {alert.notification_method.toUpperCase()}
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* Marketplace Column */}
                        <td className="py-4 px-4">
                          <span className="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                            {alert.marketplace}
                          </span>
                        </td>

                        {/* Current Price */}
                        <td className="py-4 px-4">
                          <span className="text-base font-extrabold text-emerald-400">
                            ₹{Number(alert.current_price).toLocaleString("en-IN")}
                          </span>
                        </td>

                        {/* Target Price */}
                        <td className="py-4 px-4">
                          <span className="text-base font-extrabold text-amber-400">
                            ₹{Number(alert.target_price).toLocaleString("en-IN")}
                          </span>
                        </td>

                        {/* Status Toggle */}
                        <td className="py-4 px-4">
                          <button
                            onClick={() => handleToggleStatus(alert)}
                            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black transition-all ${
                              alert.is_active
                                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                                : "bg-gray-500/20 text-gray-400 border border-gray-500/30"
                            }`}
                          >
                            <Power className="h-3 w-3" />
                            {alert.is_active ? "ENABLED" : "DISABLED"}
                          </button>
                        </td>

                        {/* Actions Column */}
                        <td className="py-4 px-6 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => {
                                setEditingAlert(alert);
                                setNewTargetPrice(alert.target_price);
                              }}
                              className="p-2 rounded-xl border hover:text-indigo-400 transition-colors"
                              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
                              title="Edit Target Price"
                            >
                              <Edit2 className="h-4 w-4" />
                            </button>

                            <button
                              onClick={() => handleDelete(alert.id)}
                              className="p-2 rounded-xl border text-gray-400 hover:text-rose-400 hover:border-rose-500/30 transition-colors"
                              style={{ borderColor: "var(--border)" }}
                              title="Delete Alert"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </AuthGuard>
  );
}
