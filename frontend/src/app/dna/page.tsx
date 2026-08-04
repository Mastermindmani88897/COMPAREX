"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Dna, Zap, Check } from "lucide-react";

const PERSONAS = [
  {
    name: "Deal Hunter",
    desc: "Always seeking maximum discount %, coupon codes, and bank offers.",
  },
  {
    name: "Tech Enthusiast",
    desc: "Prioritizes flagship hardware specs, benchmarks, and latest models.",
  },
  {
    name: "Budget Shopper",
    desc: "Strictly enforces budget constraints with high price sensitivity.",
  },
  {
    name: "Premium Buyer",
    desc: "Values verified sellers, extended warranty, and top tier build quality.",
  },
  {
    name: "Minimalist",
    desc: "Prefers clean, essential products without unnecessary marketing fluff.",
  },
];

export default function ShoppingDNAPage() {
  const [activePersona, setActivePersona] = useState("Deal Hunter");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold uppercase tracking-wider">
            <Dna className="w-3.5 h-3.5" />
            Module 5: Shopping DNA
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-purple-300 bg-clip-text text-transparent">
            Shopping DNA & Personas
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            Customize your Shopping Persona to tune AI deal scores and recommendation algorithms.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {PERSONAS.map((p) => {
            const isSelected = activePersona === p.name;
            return (
              <motion.div
                key={p.name}
                whileHover={{ scale: 1.01 }}
                onClick={() => setActivePersona(p.name)}
                className={`p-6 rounded-2xl border cursor-pointer transition flex items-start justify-between gap-4 ${
                  isSelected
                    ? "bg-purple-950/30 border-purple-500/50 shadow-lg shadow-purple-500/10"
                    : "bg-slate-900 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2 font-bold text-lg text-white">
                    <Zap className={`w-5 h-5 ${isSelected ? "text-purple-400" : "text-slate-500"}`} />
                    {p.name}
                  </div>
                  <p className="text-xs md:text-sm text-slate-400">{p.desc}</p>
                </div>

                <div
                  className={`w-6 h-6 rounded-full border flex items-center justify-center ${
                    isSelected ? "bg-purple-600 border-purple-400 text-white" : "border-slate-700"
                  }`}
                >
                  {isSelected && <Check className="w-3.5 h-3.5" />}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
