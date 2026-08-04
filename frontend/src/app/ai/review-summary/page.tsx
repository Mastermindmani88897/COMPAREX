"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  MessageSquareText,
  ThumbsUp,
  ThumbsDown,
  CheckCircle2,
  Award,
  Loader2,
} from "lucide-react";
import apiClient from "@/services/api";
import type { AIReviewSummaryResponse } from "@/types";

export default function AIReviewSummaryPage() {
  const [productName, setProductName] = useState("Apple MacBook Air M2");
  const [reviewsInput, setReviewsInput] = useState(
    "Battery life is phenomenal, easily lasts 15+ hours. Display is bright and vivid. Fanless design keeps it completely silent. Slightly pricey for the 256GB base storage model."
  );
  const [reviewData, setReviewData] = useState<AIReviewSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    async function loadSummary() {
      setIsLoading(true);
      try {
        const res = await apiClient.post("/ai/review-summary", {
          product_name: productName,
          reviews: [reviewsInput],
        });
        if (!isCancelled) {
          setReviewData(res.data.data);
        }
      } catch {
        if (!isCancelled) {
          setReviewData(null);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }
    loadSummary();
    return () => {
      isCancelled = true;
    };
  }, [productName, reviewsInput]);

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-extrabold border gradient-text" style={{ borderColor: "var(--border)" }}>
            <MessageSquareText className="h-3.5 w-3.5 text-indigo-400" /> Feature 5 AI Review Intelligence
          </span>
          <h1 className="text-3xl sm:text-5xl font-extrabold" style={{ color: "var(--foreground)" }}>
            Review <span className="gradient-text">Summarizer</span>
          </h1>
          <p className="text-sm max-w-xl mx-auto" style={{ color: "var(--foreground-muted)" }}>
            Synthesizes customer sentiment into pros, cons, verdict, and confidence metrics.
          </p>
        </div>

        {/* Input Box */}
        <div className="p-6 rounded-2xl border space-y-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="space-y-1.5">
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
            <label className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>Customer Reviews Text</label>
            <textarea
              rows={3}
              value={reviewsInput}
              onChange={(e) => setReviewsInput(e.target.value)}
              className="w-full p-3 rounded-xl text-xs font-medium border focus:outline-none"
              style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
            />
          </div>
        </div>

        {/* Intelligence Breakdown Card */}
        {isLoading ? (
          <div className="py-16 text-center space-y-3">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-400 mx-auto" />
            <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
              Extracting sentiment pros, cons, and buying verdict…
            </p>
          </div>
        ) : reviewData ? (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Pros and Cons Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Pros */}
              <div className="p-6 rounded-2xl border space-y-3" style={{ background: "rgba(16,185,129,0.04)", borderColor: "rgba(16,185,129,0.3)" }}>
                <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                  <ThumbsUp className="h-4 w-4" /> Pros & Highlights
                </h3>
                <ul className="space-y-2 text-xs">
                  {reviewData.pros.map((p, idx) => (
                    <li key={idx} className="flex items-start gap-2" style={{ color: "var(--foreground)" }}>
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Cons */}
              <div className="p-6 rounded-2xl border space-y-3" style={{ background: "rgba(239,68,68,0.04)", borderColor: "rgba(239,68,68,0.3)" }}>
                <h3 className="text-sm font-bold text-red-400 flex items-center gap-2">
                  <ThumbsDown className="h-4 w-4" /> Drawbacks & Cons
                </h3>
                <ul className="space-y-2 text-xs">
                  {reviewData.cons.map((c, idx) => (
                    <li key={idx} className="flex items-start gap-2" style={{ color: "var(--foreground)" }}>
                      <span className="h-1.5 w-1.5 rounded-full bg-red-400 flex-shrink-0 mt-1.5" />
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Summary & Verdict Card */}
            <div className="p-6 rounded-2xl border space-y-4" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  Buying Verdict
                </span>
                <span className="text-xs font-bold px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center gap-1">
                  <Award className="h-3.5 w-3.5" /> Confidence Score: {reviewData.review_confidence_score} / 10
                </span>
              </div>

              <h2 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                {reviewData.buying_verdict}
              </h2>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                {reviewData.summary}
              </p>
            </div>
          </motion.div>
        ) : null}
      </div>
    </div>
  );
}
