"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { History, Search, Layers, Heart, Trash2 } from "lucide-react";

export default function ShoppingMemoryPage() {
  const [memories, setMemories] = useState([
    {
      id: "1",
      type: "SEARCH",
      query: "Wireless Noise Cancelling Headphones under ₹25,000",
      time: "10 mins ago",
    },
    {
      id: "2",
      type: "COMPARE",
      query: "Sony WH-1000XM5 vs Bose QuietComfort Ultra",
      time: "2 hours ago",
    },
    {
      id: "3",
      type: "WISHLIST",
      query: "Apple MacBook Air M3 16GB RAM",
      time: "Yesterday",
    },
  ]);

  const handleClear = () => {
    setMemories([]);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
              <History className="w-3.5 h-3.5" />
              Module 2: Shopping Memory
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-cyan-300 bg-clip-text text-transparent">
              Shopping Memory Timeline
            </h1>
            <p className="text-slate-400 text-sm md:text-base">
              View your search, compare, and wishlist history events. You remain in full control.
            </p>
          </div>

          <button
            onClick={handleClear}
            className="px-4 py-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 hover:bg-rose-500/20 text-sm font-semibold flex items-center gap-2 transition"
          >
            <Trash2 className="w-4 h-4" />
            Clear Memory
          </button>
        </div>

        <div className="space-y-4">
          {memories.length === 0 ? (
            <div className="p-12 rounded-2xl bg-slate-900 border border-slate-800 text-center text-slate-500">
              Your shopping memory timeline is empty.
            </div>
          ) : (
            memories.map((m, idx) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-slate-800 text-cyan-400">
                    {m.type === "SEARCH" && <Search className="w-5 h-5" />}
                    {m.type === "COMPARE" && <Layers className="w-5 h-5" />}
                    {m.type === "WISHLIST" && <Heart className="w-5 h-5" />}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">{m.query}</div>
                    <div className="text-xs text-slate-500">Event: {m.type} • {m.time}</div>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
