"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Bot, Send, CheckCircle } from "lucide-react";

export default function AICoachPage() {
  const [question, setQuestion] = useState("Should I buy Sony WH-1000XM5 now or wait for sale?");
  const [response, setResponse] = useState<{
    verdict: string;
    advice: string;
    key_factors: string[];
  } | null>({
    verdict: "BUY",
    advice:
      "Based on price history for Sony WH-1000XM5, current price of ₹24,990 is near the 30-day low. Verified 100% genuine seller with express delivery.",
    key_factors: [
      "100% Verified seller reputation score",
      "Price trend is 12% below 30-day average",
      "Auto-applying COMPAREX10 saves ₹1,500 extra",
    ],
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleAsk = () => {
    setIsLoading(true);
    setTimeout(() => {
      setResponse({
        verdict: "BUY",
        advice: `AI Coach Analysis for "${question}": Recommended to buy now as pricing is highly competitive with strong seller warranty.`,
        key_factors: [
          "Price matches lowest 90-day threshold",
          "High customer satisfaction index",
        ],
      });
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <Bot className="w-3.5 h-3.5" />
            Module 7: AI Shopping Coach
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-emerald-300 bg-clip-text text-transparent">
            AI Shopping Coach Advisor
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            Ask buying timing, seller trust, or price drop queries.
          </p>
        </div>

        {/* Input Bar */}
        <div className="p-2 rounded-2xl bg-slate-900 border border-slate-800 flex items-center gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="flex-1 bg-transparent px-4 py-3 text-sm text-slate-200 focus:outline-none"
            placeholder="Ask your shopping question..."
          />
          <button
            onClick={handleAsk}
            disabled={isLoading}
            className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm flex items-center gap-2 transition"
          >
            <Send className="w-4 h-4" />
            {isLoading ? "Thinking..." : "Ask Coach"}
          </button>
        </div>

        {/* Answer Card */}
        {response && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Coach Verdict
              </span>
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5" />
                VERDICT: {response.verdict}
              </span>
            </div>

            <p className="text-sm md:text-base text-slate-200 leading-relaxed">
              {response.advice}
            </p>

            <div className="space-y-3 pt-2 border-t border-slate-800">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Key Decision Factors
              </span>
              <div className="space-y-2">
                {response.key_factors.map((f, i) => (
                  <div key={i} className="text-xs md:text-sm text-slate-300 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400"></div>
                    {f}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
