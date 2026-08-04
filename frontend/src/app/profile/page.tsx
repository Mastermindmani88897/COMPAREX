"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { UserCheck, Shield, Save, RotateCcw } from "lucide-react";

export default function ShoppingProfilePage() {
  const [optIn, setOptIn] = useState(true);
  const [brands, setBrands] = useState("Apple, Samsung, Sony, Bose");
  const [marketplaces, setMarketplaces] = useState("Amazon India, Flipkart, Croma");
  const [minBudget, setMinBudget] = useState(5000);
  const [maxBudget, setMaxBudget] = useState(150000);
  const [savedStatus, setSavedStatus] = useState(false);

  const handleSave = () => {
    setSavedStatus(true);
    setTimeout(() => setSavedStatus(false), 2500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <UserCheck className="w-3.5 h-3.5" />
            Module 1: Personal Shopping Profile
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
            Personal Shopping Profile
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            Configure your shopping preferences. COMPAREX learns only after explicit opt-in consent.
          </p>
        </div>

        {/* Opt-in Consent Card */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/30 flex items-center justify-between gap-4"
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-semibold text-lg text-white">
              <Shield className="w-5 h-5 text-indigo-400" />
              Explicit Learning Consent
            </div>
            <p className="text-xs md:text-sm text-slate-400">
              When enabled, COMPAREX tailors deal scores and product matches to your preferences.
            </p>
          </div>

          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={optIn}
              onChange={(e) => setOptIn(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-14 h-7 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-indigo-600"></div>
          </label>
        </motion.div>

        {/* Form Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Preferred Brands
            </label>
            <input
              type="text"
              value={brands}
              onChange={(e) => setBrands(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Preferred Marketplaces
            </label>
            <input
              type="text"
              value={marketplaces}
              onChange={(e) => setMarketplaces(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Min Budget (₹)
            </label>
            <input
              type="number"
              value={minBudget}
              onChange={(e) => setMinBudget(Number(e.target.value))}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Max Budget (₹)
            </label>
            <input
              type="number"
              value={maxBudget}
              onChange={(e) => setMaxBudget(Number(e.target.value))}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-between pt-4">
          <button
            onClick={() => {
              setOptIn(false);
              setBrands("");
              setMinBudget(0);
              setMaxBudget(500000);
            }}
            className="px-5 py-2.5 rounded-xl border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 text-sm font-semibold flex items-center gap-2 transition"
          >
            <RotateCcw className="w-4 h-4" />
            Reset Defaults
          </button>

          <button
            onClick={handleSave}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold flex items-center gap-2 transition shadow-lg shadow-indigo-600/20"
          >
            <Save className="w-4 h-4" />
            {savedStatus ? "Saved!" : "Save Profile"}
          </button>
        </div>
      </div>
    </div>
  );
}
