"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, X, Check, AlertCircle, ShoppingBag, ShieldCheck, Mail, Smartphone, Layers } from "lucide-react";
import { alertsService } from "@/services/api";

interface PriceAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  productId: string;
  productName: string;
  currentPrice: number;
}

export function PriceAlertModal({
  isOpen,
  onClose,
  productId,
  productName,
  currentPrice,
}: PriceAlertModalProps) {
  const [targetPrice, setTargetPrice] = useState<number>(Math.round(currentPrice * 0.9));
  const [marketplace, setMarketplace] = useState<string>("All Marketplaces");
  const [notificationMethod, setNotificationMethod] = useState<string>("both");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handlePercentageShortcut = (pct: number) => {
    setTargetPrice(Math.round(currentPrice * (1 - pct / 100)));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      await alertsService.createAlert({
        product_id: productId,
        target_price: Number(targetPrice),
        marketplace,
        notification_method: notificationMethod,
      });

      setSuccessMsg("Price alert set successfully! We will notify you when price drops.");
      setTimeout(() => {
        setSuccessMsg(null);
        onClose();
      }, 2000);
    } catch (err: any) {
      console.error("Price alert creation error:", err);
      setErrorMsg(err?.response?.data?.message || "Failed to set price alert. Please log in first.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 15 }}
            className="relative max-w-lg w-full rounded-3xl border p-6 sm:p-8 space-y-6 shadow-2xl overflow-hidden"
            style={{ background: "var(--card)", borderColor: "var(--border)" }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b pb-4" style={{ borderColor: "var(--border)" }}>
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-amber-500/20 text-amber-400">
                  <Bell className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold" style={{ color: "var(--foreground)" }}>
                    Set Price Alert
                  </h3>
                  <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                    Never miss a price drop on your favorite product.
                  </p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/10"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Product Summary */}
            <div className="p-4 rounded-2xl border flex items-center justify-between" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              <div>
                <span className="text-xs block font-medium" style={{ color: "var(--foreground-muted)" }}>
                  Product
                </span>
                <p className="text-sm font-bold line-clamp-1" style={{ color: "var(--foreground)" }}>
                  {productName}
                </p>
              </div>

              <div className="text-right">
                <span className="text-xs block font-medium" style={{ color: "var(--foreground-muted)" }}>
                  Current Price
                </span>
                <p className="text-base font-extrabold text-emerald-400">
                  ₹{Number(currentPrice).toLocaleString("en-IN")}
                </p>
              </div>
            </div>

            {/* Alert Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Target Price */}
              <div className="space-y-2">
                <label className="block text-xs font-bold" style={{ color: "var(--foreground)" }}>
                  Notify Me Below (Target Price in ₹)
                </label>
                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 font-bold text-sm text-indigo-400">
                    ₹
                  </span>
                  <input
                    type="number"
                    value={targetPrice}
                    onChange={(e) => setTargetPrice(Number(e.target.value))}
                    min={1}
                    className="w-full pl-8 pr-4 py-3 rounded-xl text-base font-extrabold border"
                    style={{
                      background: "var(--background)",
                      borderColor: "var(--border)",
                      color: "var(--foreground)",
                    }}
                    required
                  />
                </div>

                {/* Shortcuts */}
                <div className="flex items-center gap-2 pt-1">
                  <span className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>Quick select:</span>
                  {[5, 10, 15, 20].map((pct) => (
                    <button
                      key={pct}
                      type="button"
                      onClick={() => handlePercentageShortcut(pct)}
                      className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 hover:bg-indigo-500/20"
                    >
                      -{pct}%
                    </button>
                  ))}
                </div>
              </div>

              {/* Marketplace Dropdown */}
              <div className="space-y-2">
                <label className="block text-xs font-bold" style={{ color: "var(--foreground)" }}>
                  Preferred Marketplace
                </label>
                <select
                  value={marketplace}
                  onChange={(e) => setMarketplace(e.target.value)}
                  className="w-full py-3 px-3.5 rounded-xl text-sm font-medium border"
                  style={{
                    background: "var(--background)",
                    borderColor: "var(--border)",
                    color: "var(--foreground)",
                  }}
                >
                  <option value="All Marketplaces">All Marketplaces (Recommended)</option>
                  <option value="Amazon India">Amazon India</option>
                  <option value="Flipkart">Flipkart</option>
                  <option value="Croma">Croma</option>
                  <option value="Reliance Digital">Reliance Digital</option>
                  <option value="Tata CLiQ">Tata CLiQ</option>
                  <option value="Vijay Sales">Vijay Sales</option>
                  <option value="Meesho">Meesho</option>
                  <option value="Myntra">Myntra</option>
                </select>
              </div>

              {/* Notification Method */}
              <div className="space-y-2">
                <label className="block text-xs font-bold" style={{ color: "var(--foreground)" }}>
                  Notification Method
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: "both", label: "In-App & Email", icon: Bell },
                    { id: "in_app", label: "In-App Only", icon: Smartphone },
                    { id: "email", label: "Email Only", icon: Mail },
                  ].map((m) => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => setNotificationMethod(m.id)}
                      className={`p-3 rounded-xl border text-left flex flex-col justify-between transition-all ${
                        notificationMethod === m.id
                          ? "border-amber-400 bg-amber-400/10 text-amber-300 ring-2 ring-amber-400/20"
                          : "opacity-70 hover:opacity-100"
                      }`}
                      style={{ background: "var(--background)", borderColor: notificationMethod === m.id ? "#f59e0b" : "var(--border)" }}
                    >
                      <m.icon className="h-4 w-4 mb-2" />
                      <span className="text-[11px] font-bold block">{m.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Status Messages */}
              {errorMsg && (
                <div className="p-3 rounded-xl text-xs bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              {successMsg && (
                <div className="p-3 rounded-xl text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 flex items-center gap-2">
                  <Check className="h-4 w-4 shrink-0" />
                  <span>{successMsg}</span>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3.5 rounded-xl gradient-bg text-white text-sm font-bold shadow-lg hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {isSubmitting ? "Setting Alert..." : "Create Price Alert"}
              </button>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
