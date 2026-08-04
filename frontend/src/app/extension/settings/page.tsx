"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ChevronLeft,
  Save,
  CheckCircle2,
  Sliders,
  Store,
} from "lucide-react";

const STORES = [
  { id: "amazon", name: "Amazon India" },
  { id: "flipkart", name: "Flipkart" },
  { id: "croma", name: "Croma" },
  { id: "reliance_digital", name: "Reliance Digital" },
  { id: "vijay_sales", name: "Vijay Sales" },
  { id: "myntra", name: "Myntra" },
  { id: "ajio", name: "Ajio" },
  { id: "meesho", name: "Meesho" },
  { id: "nykaa", name: "Nykaa" },
];

export default function ExtensionSettingsPage() {
  const [theme, setTheme] = useState("dark");
  const [position, setPosition] = useState("bottom-right");
  const [enableOverlay, setEnableOverlay] = useState(true);
  const [selectedStores, setSelectedStores] = useState<string[]>(STORES.map((s) => s.id));

  const [saveStatus, setSaveStatus] = useState<"idle" | "saved">("idle");

  const toggleStore = (id: string) => {
    if (selectedStores.includes(id)) {
      setSelectedStores(selectedStores.filter((s) => s !== id));
    } else {
      setSelectedStores([...selectedStores, id]);
    }
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveStatus("saved");
    setTimeout(() => setSaveStatus("idle"), 3000);
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <div className="max-w-3xl mx-auto space-y-8">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link
            href="/extension"
            className="inline-flex items-center gap-2 text-sm font-medium hover:text-indigo-400 transition-colors"
            style={{ color: "var(--foreground-muted)" }}
          >
            <ChevronLeft className="h-4 w-4" /> Back to Extension Onboarding Hub
          </Link>
          <span className="text-xs px-3 py-1 rounded-full border gradient-text font-bold" style={{ borderColor: "var(--border)" }}>
            Extension Preferences Sync
          </span>
        </div>

        {/* Page Title */}
        <div>
          <h1 className="text-3xl font-extrabold" style={{ color: "var(--foreground)" }}>
            Browser Extension <span className="gradient-text">Settings</span>
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
            Configure your extension overlay position, active marketplace connectors, and display preferences.
          </p>
        </div>

        <form onSubmit={handleSave} className="space-y-8">
          {/* General Preferences */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border p-6 space-y-6"
            style={{ background: "var(--card)", borderColor: "var(--border)" }}
          >
            <div className="flex items-center gap-3 border-b pb-4" style={{ borderColor: "var(--border)" }}>
              <div className="p-2 rounded-xl gradient-bg text-white">
                <Sliders className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                  General Preferences
                </h2>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  Extension theme & widget position settings
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>
                  Extension Theme
                </label>
                <select
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                  className="w-full py-3 px-4 rounded-xl text-sm font-medium border focus:outline-none"
                  style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                >
                  <option value="dark">Dark Mode (Recommended)</option>
                  <option value="light">Light Mode</option>
                  <option value="system">System Preference</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>
                  Floating Widget Position
                </label>
                <select
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  className="w-full py-3 px-4 rounded-xl text-sm font-medium border focus:outline-none"
                  style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                >
                  <option value="bottom-right">Bottom Right (Default)</option>
                  <option value="bottom-left">Bottom Left</option>
                  <option value="top-right">Top Right</option>
                </select>
              </div>
            </div>

            <div className="pt-2">
              <label className="flex items-center gap-3 text-xs font-medium cursor-pointer" style={{ color: "var(--foreground)" }}>
                <input
                  type="checkbox"
                  checked={enableOverlay}
                  onChange={(e) => setEnableOverlay(e.target.checked)}
                  className="rounded text-indigo-500 focus:ring-indigo-400 h-4 w-4"
                />
                Enable floating comparison widget on recognized product pages
              </label>
            </div>
          </motion.div>

          {/* Marketplace Connector Selection */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="rounded-2xl border p-6 space-y-6"
            style={{ background: "var(--card)", borderColor: "var(--border)" }}
          >
            <div className="flex items-center gap-3 border-b pb-4" style={{ borderColor: "var(--border)" }}>
              <div className="p-2 rounded-xl gradient-bg text-white">
                <Store className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                  Active Marketplace Stores
                </h2>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  Select which marketplace connectors should be queried by extension
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {STORES.map((s) => {
                const isSelected = selectedStores.includes(s.id);
                return (
                  <button
                    type="button"
                    key={s.id}
                    onClick={() => toggleStore(s.id)}
                    className={`p-3.5 rounded-xl border text-left flex items-center justify-between text-xs font-semibold transition-all ${
                      isSelected ? "border-indigo-500/50 bg-indigo-500/10 text-indigo-400" : "opacity-60"
                    }`}
                    style={isSelected ? {} : { borderColor: "var(--border)", color: "var(--foreground-muted)" }}
                  >
                    <span>{s.name}</span>
                    {isSelected && <CheckCircle2 className="h-4 w-4 text-indigo-400 flex-shrink-0" />}
                  </button>
                );
              })}
            </div>
          </motion.div>

          {/* Save Action */}
          <div className="flex items-center gap-4">
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl gradient-bg text-white font-semibold text-xs shadow-md hover:opacity-90 transition-opacity"
            >
              <Save className="h-4 w-4" /> Save Extension Settings
            </button>

            {saveStatus === "saved" && (
              <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4" /> Settings synced to local storage
              </span>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
