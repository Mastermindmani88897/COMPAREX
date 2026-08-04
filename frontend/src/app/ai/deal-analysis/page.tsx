"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Award,
  Loader2,
  ShieldCheck,
  Tag,
} from "lucide-react";
import apiClient from "@/services/api";
import type { AIDealAnalysisResponse } from "@/types";

export default function AIDealAnalysisPage() {
  const [productName, setProductName] = useState("Sony WH-1000XM5 Wireless Headphones");
  const [price, setPrice] = useState(26990);
  const [dealData, setDealData] = useState<AIDealAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    async function loadData() {
      setIsLoading(true);
      try {
        const res = await apiClient.post("/ai/deal-analysis", {
          product_name: productName,
          price: price,
          original_price: price * 1.25,
          rating: 4.6,
          marketplace_slug: "amazon",
          delivery_estimate: "Prime Express Delivery",
        });
        if (!isCancelled) {
          setDealData(res.data.data);
        }
      } catch {
        if (!isCancelled) {
          setDealData(null);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }
    loadData();
    return () => {
      isCancelled = true;
    };
  }, [productName, price]);

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-extrabold border gradient-text" style={{ borderColor: "var(--border)" }}>
            <Award className="h-3.5 w-3.5 text-indigo-400" /> Shopping Decision Engine & Deal Score AI
          </span>
          <h1 className="text-3xl sm:text-5xl font-extrabold" style={{ color: "var(--foreground)" }}>
            Deal Score <span className="gradient-text">Analyzer</span>
          </h1>
          <p className="text-sm max-w-xl mx-auto" style={{ color: "var(--foreground-muted)" }}>
            Quantitative 0 to 10 deal scoring combining price, seller rating, delivery, and market alternatives.
          </p>
        </div>

        {/* Input Control Box */}
        <div className="p-6 rounded-2xl border space-y-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2 space-y-1.5">
              <label className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>Product Title</label>
              <input
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                className="w-full p-3 rounded-xl text-sm font-medium border"
                style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>Price (₹)</label>
              <input
                type="number"
                value={price}
                onChange={(e) => setPrice(Number(e.target.value))}
                className="w-full p-3 rounded-xl text-sm font-medium border"
                style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
              />
            </div>
          </div>
        </div>

        {/* Deal Score Display Card */}
        {isLoading ? (
          <div className="py-16 text-center space-y-3">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-400 mx-auto" />
            <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
              Evaluating deal metrics across 4 quantitative dimensions…
            </p>
          </div>
        ) : dealData ? (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            {/* Score & Verdict Banner */}
            <div className="p-8 rounded-2xl border flex flex-col sm:flex-row items-center justify-between gap-6" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <div className="space-y-2 text-center sm:text-left">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  {dealData.decision_label}
                </span>
                <h2 className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
                  {dealData.product_name}
                </h2>
                <p className="text-xs max-w-lg" style={{ color: "var(--foreground-muted)" }}>
                  {dealData.detailed_explanation}
                </p>
              </div>

              {/* Deal Score Circle */}
              <div className="flex flex-col items-center justify-center p-6 rounded-2xl gradient-bg text-white font-extrabold flex-shrink-0 shadow-lg">
                <span className="text-4xl font-mono">{dealData.deal_score}</span>
                <span className="text-[10px] uppercase tracking-widest opacity-80 mt-1">Deal Score / 10</span>
              </div>
            </div>

            {/* Score Breakdown Bars */}
            <div className="p-6 rounded-2xl border space-y-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <h3 className="text-sm font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                <ShieldCheck className="h-4 w-4 text-emerald-400" /> Score Dimension Breakdown
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {Object.entries(dealData.score_breakdown).map(([key, val]) => (
                  <div key={key} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span style={{ color: "var(--foreground)" }}>{key.replace("_", " ").toUpperCase()}</span>
                      <span className="gradient-text">{val} / 10</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-gray-700 overflow-hidden">
                      <div
                        className="h-full gradient-bg rounded-full"
                        style={{ width: `${(val / 10) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Feature 6: Smart Alternatives */}
            {dealData.alternatives_suggested.length > 0 && (
              <div className="p-6 rounded-2xl border space-y-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
                <h3 className="text-sm font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                  <Tag className="h-4 w-4 text-amber-400" /> Smart Alternatives Recommended by AI
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {dealData.alternatives_suggested.map((alt, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl border space-y-2"
                      style={{ background: "var(--background)", borderColor: "var(--border)" }}
                    >
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full border text-indigo-400" style={{ borderColor: "var(--border)" }}>
                        {alt.marketplace_name}
                      </span>
                      <h4 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
                        {alt.product_name}
                      </h4>
                      <p className="text-lg font-extrabold text-emerald-400">
                        ₹{alt.price.toLocaleString("en-IN")}
                      </p>
                      <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                        💡 {alt.reason}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        ) : null}
      </div>
    </div>
  );
}
