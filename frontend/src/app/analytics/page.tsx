"use client";

import React from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, DollarSign, Award, Target } from "lucide-react";

export default function AnalyticsPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <BarChart3 className="w-3.5 h-3.5" />
            Module 13: Shopping Analytics
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-emerald-300 bg-clip-text text-transparent">
            Shopping Analytics Dashboard
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            Track total money saved, average discount metrics, top brands, and recommendation accuracy.
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2"
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Total Saved
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">₹4,250</div>
            <div className="text-xs text-emerald-400 font-medium">↑ 18.5% average savings</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2"
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Top Brand
              <Award className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">Apple</div>
            <div className="text-xs text-slate-400 font-medium">12 indexed products viewed</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2"
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
              AI Accuracy
              <Target className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">94%</div>
            <div className="text-xs text-purple-400 font-medium">Verified helpful ratings</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2"
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Shopping Trend
              <TrendingUp className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">Optimal</div>
            <div className="text-xs text-cyan-400 font-medium">Deal Hunter persona active</div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
