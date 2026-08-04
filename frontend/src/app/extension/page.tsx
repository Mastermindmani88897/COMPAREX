"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Download,
  CheckCircle2,
  Cpu,
  Layers,
  Zap,
  ArrowRight,
  Settings,
  Store,
  RefreshCw,
} from "lucide-react";
import apiClient from "@/services/api";
import type { ExtensionStatusResponse } from "@/types";

export default function ExtensionOnboardingPage() {
  const [statusData, setStatusData] = useState<ExtensionStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkGatewayStatus = async () => {
    setIsLoading(true);
    try {
      const res = await apiClient.get("/extension/status");
      setStatusData(res.data.data);
    } catch {
      setStatusData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let isCancelled = false;
    async function loadStatus() {
      setIsLoading(true);
      try {
        const res = await apiClient.get("/extension/status");
        if (!isCancelled) {
          setStatusData(res.data.data);
        }
      } catch {
        if (!isCancelled) {
          setStatusData(null);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }
    loadStatus();
    return () => {
      isCancelled = true;
    };
  }, []);

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header Hero */}
        <div className="text-center space-y-4">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-extrabold border gradient-text" style={{ borderColor: "var(--border)" }}>
            <Cpu className="h-3.5 w-3.5 text-indigo-400" /> Phase 5 Browser Extension Ecosystem
          </span>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>
            COMPAREX <span className="gradient-text">Browser Assistant</span>
          </h1>
          <p className="text-base max-w-2xl mx-auto" style={{ color: "var(--foreground-muted)" }}>
            Compare prices instantly while browsing Amazon, Flipkart, Croma, Myntra, and 5+ major retail stores in real-time.
          </p>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            <a
              href="http://localhost:8000/api/v1/extension/status"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl gradient-bg text-white font-bold text-sm shadow-lg hover:opacity-90 transition-opacity"
            >
              <Download className="h-4 w-4" /> Download Extension Manifest V3
            </a>
            <Link
              href="/extension/settings"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl border font-bold text-sm transition-colors hover:border-indigo-400"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              <Settings className="h-4 w-4" /> Extension Settings
            </Link>
          </div>
        </div>

        {/* Backend Gateway Connection Status Panel */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border p-6 sm:p-8"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6" style={{ borderColor: "var(--border)" }}>
            <div className="space-y-1">
              <h2 className="text-xl font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                <Zap className="h-5 w-5 text-amber-400" /> Backend Gateway Connection Status
              </h2>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Extension Gateway API status & connector sync check.
              </p>
            </div>
            <button
              onClick={checkGatewayStatus}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-semibold hover:text-indigo-400 transition-colors"
              style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} /> Refresh Status
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 pt-6">
            <div className="p-4 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Gateway Status</span>
              <p className="text-lg font-extrabold flex items-center gap-2 mt-1">
                {statusData?.status === "online" ? (
                  <span className="text-emerald-400 flex items-center gap-1.5"><CheckCircle2 className="h-4 w-4" /> Online</span>
                ) : (
                  <span className="text-red-400">Offline / Error</span>
                )}
              </p>
            </div>

            <div className="p-4 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Active Connectors</span>
              <p className="text-lg font-extrabold gradient-text mt-1">
                {statusData?.active_connectors_count ?? 9} Retail Stores
              </p>
            </div>

            <div className="p-4 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Supported Version</span>
              <p className="text-lg font-extrabold text-indigo-400 mt-1">
                v{statusData?.min_supported_extension_version ?? "1.0.0"} (V3)
              </p>
            </div>

            <div className="p-4 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>Environment</span>
              <p className="text-lg font-extrabold text-amber-400 mt-1 uppercase">
                {statusData?.environment ?? "Development"}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Step-by-Step Installation Guide */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-center" style={{ color: "var(--foreground)" }}>
            Installation Guide (Chrome & Chromium Browsers)
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                step: "01",
                title: "Download Extension Folder",
                desc: "Download or clone the extension directory from the COMPAREX project repository.",
                icon: Download,
              },
              {
                step: "02",
                title: "Enable Developer Mode",
                desc: "Open chrome://extensions in your browser and toggle Developer Mode on top right.",
                icon: Layers,
              },
              {
                step: "03",
                title: "Load Unpacked Extension",
                desc: "Click Load unpacked and select the COMPAREX extension folder.",
                icon: CheckCircle2,
              },
            ].map((s) => (
              <div
                key={s.step}
                className="p-6 rounded-2xl border space-y-3 relative overflow-hidden"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <span className="text-4xl font-extrabold opacity-10 absolute right-4 bottom-2 font-mono">
                  {s.step}
                </span>
                <div className="p-3 rounded-xl gradient-bg w-fit text-white">
                  <s.icon className="h-5 w-5" />
                </div>
                <h3 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                  {s.title}
                </h3>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Supported Marketplaces Badge Grid */}
        <div
          className="rounded-2xl p-6 border space-y-4"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <h3 className="text-base font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
            <Store className="h-4 w-4 text-indigo-400" /> Supported Marketplace Domains (Auto-Detect)
          </h3>
          <div className="flex flex-wrap gap-2.5">
            {[
              "Amazon India (amazon.in)",
              "Flipkart (flipkart.com)",
              "Croma (croma.com)",
              "Reliance Digital (reliancedigital.in)",
              "Vijay Sales (vijaysales.com)",
              "Myntra (myntra.com)",
              "Ajio (ajio.com)",
              "Meesho (meesho.com)",
              "Nykaa (nykaa.com)",
            ].map((m) => (
              <span
                key={m}
                className="px-3.5 py-1.5 rounded-xl border text-xs font-semibold bg-indigo-500/10 text-indigo-400"
                style={{ borderColor: "rgba(99,102,241,0.2)" }}
              >
                {m}
              </span>
            ))}
          </div>
        </div>

        {/* CTA Footer */}
        <div className="text-center pt-4">
          <Link
            href="/compare"
            className="inline-flex items-center gap-2 text-sm font-bold text-indigo-400 hover:underline"
          >
            Launch Web App Live Price Aggregator <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
