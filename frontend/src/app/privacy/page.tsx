"use client";

import React, { useState } from "react";
import { Lock, Download, Trash2, ShieldCheck, Check } from "lucide-react";

export default function PrivacyCenterPage() {
  const [exported, setExported] = useState(false);
  const [purged, setPurged] = useState(false);

  const handleExport = () => {
    setExported(true);
    setTimeout(() => setExported(false), 3000);
  };

  const handlePurge = () => {
    setPurged(true);
    setTimeout(() => setPurged(false), 3000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider">
            <Lock className="w-3.5 h-3.5" />
            Module 14: Smart Privacy
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-blue-300 bg-clip-text text-transparent">
            Smart Privacy Center
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            Full user data ownership. Opt-in learning, data export, and complete AI memory purging.
          </p>
        </div>

        {/* Guarantees Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <ShieldCheck className="w-6 h-6 text-blue-400" />
            <h3 className="text-sm font-bold text-white">No Passwords</h3>
            <p className="text-xs text-slate-400">
              We never ask for or store passwords from external shopping sites.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <ShieldCheck className="w-6 h-6 text-blue-400" />
            <h3 className="text-sm font-bold text-white">No Payment Info</h3>
            <p className="text-xs text-slate-400">
              Payment information and credit card numbers are strictly untouched.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <ShieldCheck className="w-6 h-6 text-blue-400" />
            <h3 className="text-sm font-bold text-white">Opt-In Learning</h3>
            <p className="text-xs text-slate-400">
              Personalization algorithm runs only when explicit consent is enabled.
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Export Personal Data</h3>
              <p className="text-xs text-slate-400">
                Download a JSON payload containing all your profiles, memories, and preferences.
              </p>
            </div>

            <button
              onClick={handleExport}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm flex items-center gap-2 transition"
            >
              {exported ? <Check className="w-4 h-4" /> : <Download className="w-4 h-4" />}
              {exported ? "Exported!" : "Export JSON"}
            </button>
          </div>

          <div className="pt-6 border-t border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white text-rose-400">Purge AI Memory</h3>
              <p className="text-xs text-slate-400">
                Permanently erase all AI interaction memories, profile settings, and DNA traits.
              </p>
            </div>

            <button
              onClick={handlePurge}
              className="px-5 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 font-semibold text-sm flex items-center gap-2 transition"
            >
              <Trash2 className="w-4 h-4" />
              {purged ? "Purged!" : "Purge All Data"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
