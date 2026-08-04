"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Camera,
  Sparkles,
  CheckCircle2,
  ShoppingBag,
  Loader2,
} from "lucide-react";
import apiClient from "@/services/api";
import type { AIImageSearchResponse, AggregatedListing } from "@/types";

export default function AIImageSearchPage() {
  const [imageUrl, setImageUrl] = useState("https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80");
  const [searchData, setSearchData] = useState<AIImageSearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const runVisualSearch = async () => {
    if (!imageUrl || isLoading) return;
    setIsLoading(true);
    try {
      const res = await apiClient.post("/ai/image-search", {
        image_url: imageUrl,
        category_hint: "electronics",
      });
      setSearchData(res.data.data);
    } catch {
      setSearchData(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-extrabold border gradient-text" style={{ borderColor: "var(--border)" }}>
            <Camera className="h-3.5 w-3.5 text-indigo-400" /> Feature 4 Image Search Architecture
          </span>
          <h1 className="text-3xl sm:text-5xl font-extrabold" style={{ color: "var(--foreground)" }}>
            Visual Image <span className="gradient-text">Search</span>
          </h1>
          <p className="text-sm max-w-xl mx-auto" style={{ color: "var(--foreground-muted)" }}>
            Upload or paste any product image to extract features and search 9+ marketplace connectors.
          </p>
        </div>

        {/* Upload & Image Preview Panel */}
        <div className="p-6 rounded-2xl border space-y-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="space-y-1.5">
            <label className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>Product Image URL</label>
            <div className="flex gap-3">
              <input
                type="text"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="Paste image URL (https://...)"
                className="flex-1 p-3 rounded-xl text-sm font-medium border"
                style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
              />
              <button
                onClick={runVisualSearch}
                disabled={isLoading || !imageUrl}
                className="px-6 py-3 rounded-xl gradient-bg text-white font-bold text-xs shadow-md disabled:opacity-50 transition-opacity flex items-center gap-2"
              >
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                Analyze Image
              </button>
            </div>
          </div>

          {imageUrl && (
            <div className="h-48 w-full rounded-xl overflow-hidden border relative bg-black/20 flex items-center justify-center" style={{ borderColor: "var(--border)" }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={imageUrl} alt="Uploaded product" className="h-full object-contain" />
            </div>
          )}
        </div>

        {/* Vision Analysis Results */}
        {searchData && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Extracted Features Banner */}
            <div className="p-6 rounded-2xl border space-y-3" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  Detected Product Type
                </span>
                <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="h-3.5 w-3.5" /> AI Confidence: {Math.round(searchData.confidence_score * 100)}%
                </span>
              </div>

              <h2 className="text-xl font-bold" style={{ color: "var(--foreground)" }}>
                {searchData.detected_product_type} ({searchData.suggested_search_query})
              </h2>

              <div className="flex flex-wrap gap-2 pt-2">
                {searchData.extracted_features.map((feat, idx) => (
                  <span key={idx} className="px-3 py-1 rounded-xl text-xs font-semibold border bg-indigo-500/10 text-indigo-400" style={{ borderColor: "rgba(99,102,241,0.2)" }}>
                    ✨ {feat}
                  </span>
                ))}
              </div>
            </div>

            {/* Aggregated Marketplace Price Results */}
            {searchData.aggregated_results?.listings && (
              <div className="space-y-4">
                <h3 className="text-sm font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                  <ShoppingBag className="h-4 w-4 text-indigo-400" /> Matches Found Across Retail Connectors
                </h3>

                <div className="space-y-3">
                  {searchData.aggregated_results.listings.slice(0, 3).map((item: AggregatedListing, idx: number) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl border flex items-center justify-between gap-4"
                      style={{ background: "var(--card)", borderColor: "var(--border)" }}
                    >
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border text-indigo-400" style={{ borderColor: "var(--border)" }}>
                          {item.marketplace_name}
                        </span>
                        <h4 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
                          {item.title}
                        </h4>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="text-lg font-extrabold gradient-text">
                          ₹{item.price.toLocaleString("en-IN")}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
