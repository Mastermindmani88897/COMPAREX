"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { HelpCircle, Trophy, CheckCircle, XCircle } from "lucide-react";

export default function ExplainPage() {
  const [prodA, setProdA] = useState("Sony WH-1000XM5");
  const [prodB, setProdB] = useState("Bose QuietComfort Ultra");
  const [result] = useState<{
    winner: string;
    explanation: string;
    advantages: string[];
    disadvantages: string[];
  } | null>({
    winner: "Sony WH-1000XM5",
    explanation:
      "COMPAREX Decision Engine ranked Sony WH-1000XM5 higher than Bose QuietComfort Ultra due to superior battery endurance (30 hrs vs 24 hrs), lower price point (₹24,990 vs ₹29,900), and higher Deal Score (9.2/10).",
    advantages: [
      "Lower price point (₹24,990 vs ₹29,900)",
      "Longer battery life (30h vs 24h)",
      "Higher Deal Score rating (9.2/10)",
    ],
    disadvantages: [
      "Higher cost (₹29,900)",
      "Slightly heavier headband weight",
    ],
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold uppercase tracking-wider">
            <HelpCircle className="w-3.5 h-3.5" />
            Module 9: CompareX Explain
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-amber-300 bg-clip-text text-transparent">
            CompareX Explain: &quot;Why not Product B?&quot;
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            Transparent AI comparison explaining why Product A ranked higher than Product B.
          </p>
        </div>

        {/* Form Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Product A (Ranked Higher)
            </label>
            <input
              type="text"
              value={prodA}
              onChange={(e) => setProdA(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none"
            />
          </div>

          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Product B (Alternative)
            </label>
            <input
              type="text"
              value={prodB}
              onChange={(e) => setProdB(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none"
            />
          </div>
        </div>

        {/* Explanation Output */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6"
          >
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400">
                <Trophy className="w-6 h-6" />
              </div>
              <div>
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Winner Recommendation
                </div>
                <div className="text-xl font-bold text-white">{result.winner}</div>
              </div>
            </div>

            <p className="text-sm md:text-base text-slate-200 leading-relaxed">
              {result.explanation}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
              <div className="space-y-3">
                <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle className="w-4 h-4" />
                  Key Advantages of Product A
                </span>
                <div className="space-y-2">
                  {result.advantages.map((adv, i) => (
                    <div key={i} className="text-xs md:text-sm text-slate-300">
                      • {adv}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                  <XCircle className="w-4 h-4" />
                  Disadvantages of Product B
                </span>
                <div className="space-y-2">
                  {result.disadvantages.map((dis, i) => (
                    <div key={i} className="text-xs md:text-sm text-slate-300">
                      • {dis}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
