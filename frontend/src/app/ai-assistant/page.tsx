"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Sparkles,
  Send,
  Bot,
  User,
  Award,
  Zap,
  ArrowRight,
  Loader2,
} from "lucide-react";
import apiClient from "@/services/api";
import type { AIChatResponse } from "@/types";

interface MessageItem {
  id: string;
  sender: "user" | "ai";
  text: string;
  data?: AIChatResponse;
}

const QUICK_PROMPTS = [
  "Best gaming laptop under ₹80000",
  "Top camera smartphone for photography",
  "Programming laptop for developers",
  "Wireless noise-canceling headphones",
];

export default function AIAssistantPage() {
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: "welcome",
      sender: "ai",
      text: "Hello! I am your COMPAREX AI Shopping Assistant. Ask me for product recommendations, budget advice, or feature comparisons across 9+ Indian marketplaces!",
    },
  ]);

  const handleSend = async (queryText?: string) => {
    const textToSubmit = (queryText || inputQuery).trim();
    if (!textToSubmit || isLoading) return;

    const userMsgId = `msg-${messages.length + 1}`;
    setMessages((prev) => [
      ...prev,
      { id: userMsgId, sender: "user", text: textToSubmit },
    ]);
    setInputQuery("");
    setIsLoading(true);

    try {
      const res = await apiClient.post("/ai/chat", { message: textToSubmit });
      const aiData: AIChatResponse = res.data.data;

      setMessages((prev) => [
        ...prev,
        {
          id: `ai-${prev.length + 1}`,
          sender: "ai",
          text: aiData.response_text,
          data: aiData,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${prev.length + 1}`,
          sender: "ai",
          text: "I experienced a temporary issue analyzing live connector prices. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header Hero */}
        <div className="text-center space-y-3">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-extrabold border gradient-text" style={{ borderColor: "var(--border)" }}>
            <Sparkles className="h-3.5 w-3.5 text-indigo-400" /> Phase 6 AI Shopping Intelligence Platform
          </span>
          <h1 className="text-3xl sm:text-5xl font-extrabold" style={{ color: "var(--foreground)" }}>
            AI Shopping <span className="gradient-text">Assistant</span>
          </h1>
          <p className="text-sm max-w-2xl mx-auto" style={{ color: "var(--foreground-muted)" }}>
            Natural language shopping intelligence powered by multi-connector real-time price aggregation.
          </p>
        </div>

        {/* Quick Prompts Chips */}
        <div className="flex flex-wrap items-center justify-center gap-2">
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleSend(prompt)}
              disabled={isLoading}
              className="px-3.5 py-1.5 rounded-xl text-xs font-semibold border hover:border-indigo-400 transition-all cursor-pointer"
              style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground-muted)" }}
            >
              ⚡ {prompt}
            </button>
          ))}
        </div>

        {/* Chat History Box */}
        <div className="rounded-2xl border p-6 space-y-6 min-h-[420px] max-h-[600px] overflow-y-auto" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          {messages.map((m) => (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-4 ${m.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              {m.sender === "ai" && (
                <div className="h-10 w-10 rounded-xl gradient-bg flex items-center justify-center text-white flex-shrink-0 shadow-sm">
                  <Bot className="h-5 w-5" />
                </div>
              )}

              <div className={`space-y-4 max-w-2xl ${m.sender === "user" ? "text-right" : "text-left"}`}>
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed ${
                    m.sender === "user"
                      ? "gradient-bg text-white font-medium shadow-md"
                      : "border font-normal"
                  }`}
                  style={m.sender === "ai" ? { background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" } : {}}
                >
                  {m.text}
                </div>

                {/* AI Recommendation Product Cards Grid */}
                {m.data?.recommendations && m.data.recommendations.length > 0 && (
                  <div className="space-y-3 pt-2">
                    <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5" style={{ color: "var(--foreground-muted)" }}>
                      <Zap className="h-3.5 w-3.5 text-amber-400" /> AI Ranked Deals ({m.data.recommendations.length})
                    </span>

                    {m.data.recommendations.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-xl border space-y-2 text-left"
                        style={{ background: "var(--background)", borderColor: "var(--border)" }}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="text-sm font-bold truncate" style={{ color: "var(--foreground)" }}>
                            {rec.product_name}
                          </h4>
                          {rec.is_best_value && (
                            <span className="inline-flex items-center gap-1 text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-500 text-white flex-shrink-0">
                              <Award className="h-3 w-3" /> BEST VALUE
                            </span>
                          )}
                        </div>

                        <div className="flex items-center justify-between text-xs">
                          <span className="font-extrabold text-emerald-400 text-base">
                            ₹{rec.price.toLocaleString("en-IN")}
                          </span>
                          <span className="px-2 py-0.5 rounded-full border text-[10px] font-bold" style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}>
                            {rec.marketplace_name}
                          </span>
                        </div>

                        <ul className="space-y-1 text-xs" style={{ color: "var(--foreground-muted)" }}>
                          {rec.reasons.map((r, rIdx) => (
                            <li key={rIdx} className="flex items-center gap-1.5">
                              <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 flex-shrink-0" />
                              {r}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {m.sender === "user" && (
                <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white flex-shrink-0 shadow-sm">
                  <User className="h-5 w-5" />
                </div>
              )}
            </motion.div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-3 text-xs font-semibold" style={{ color: "var(--foreground-muted)" }}>
              <Loader2 className="h-4 w-4 animate-spin text-indigo-400" />
              <span>Analyzing live marketplace connectors and scoring deals…</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative max-w-3xl mx-auto"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask AI: Best phone for photography under ₹40000, Best gaming laptop..."
            className="w-full pl-5 pr-14 py-4 rounded-2xl text-sm font-medium focus:outline-none border"
            style={{
              background: "var(--card)",
              borderColor: "var(--border)",
              color: "var(--foreground)",
            }}
          />
          <button
            type="submit"
            disabled={isLoading || !inputQuery.trim()}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2.5 rounded-xl gradient-bg text-white disabled:opacity-50 transition-opacity"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>

        {/* Navigation Quick Links */}
        <div className="flex flex-wrap items-center justify-center gap-6 text-xs font-bold pt-4" style={{ color: "var(--foreground-muted)" }}>
          <Link href="/ai/deal-analysis" className="hover:text-indigo-400 flex items-center gap-1">
            Shopping Decision Engine <ArrowRight className="h-3.5 w-3.5" />
          </Link>
          <Link href="/ai/review-summary" className="hover:text-indigo-400 flex items-center gap-1">
            AI Review Intelligence <ArrowRight className="h-3.5 w-3.5" />
          </Link>
          <Link href="/ai/image-search" className="hover:text-indigo-400 flex items-center gap-1">
            Product Visual Search <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
