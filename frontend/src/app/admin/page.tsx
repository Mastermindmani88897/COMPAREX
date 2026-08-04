"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  ShieldAlert,
  Users,
  Store,
  Cpu,
  Activity,
  Terminal,
  ToggleRight,
  CheckCircle,
} from "lucide-react";

export default function AdminPage() {
  const [logs] = useState([
    { time: "19:40:02", level: "INFO", msg: "Aggregator Service: 9 connectors executed cleanly" },
    { time: "19:42:15", level: "INFO", msg: "AIAgentOrchestrator: 9 specialized agents executed" },
    { time: "19:45:30", level: "INFO", msg: "PlannerOrchestrator: Goal setup generated (90k budget)" },
    { time: "19:50:11", level: "SUCCESS", msg: "Security Middleware: Audit status PASS" },
  ]);

  const [featureFlags, setFeatureFlags] = useState({
    AI_ADVISOR: true,
    AUTO_COUPONS: true,
    VOICE_SHOPPING_INTERFACE: true,
    SMART_SIMULATION: true,
  });

  const toggleFlag = (key: keyof typeof featureFlags) => {
    setFeatureFlags((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-10">
        {/* Header */}
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            Module 5: Admin Dashboard Portal
          </div>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight bg-gradient-to-r from-white via-slate-100 to-rose-300 bg-clip-text text-transparent">
            Enterprise Admin Control Center
          </h1>
          <p className="text-slate-400 text-base md:text-lg max-w-3xl">
            Real-time system health monitoring, marketplace connector status, AI token usage, feature flag management, and live system log streams.
          </p>
        </div>

        {/* System Overview Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2"
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Active Users
              <Users className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">12,850</div>
            <div className="text-xs text-rose-400 font-medium">↑ 14% growth this week</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2"
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Connected Stores
              <Store className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">9 / 9</div>
            <div className="text-xs text-indigo-400 font-medium">100% operational</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2"
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
              AI Tokens Today
              <Cpu className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">84,500</div>
            <div className="text-xs text-purple-400 font-medium">Multi-agent orchestrator</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2"
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
              System Health
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-3xl font-extrabold text-emerald-400">99.99%</div>
            <div className="text-xs text-emerald-400 font-medium">Enterprise SaaS status</div>
          </motion.div>
        </div>

        {/* Feature Flags & Logs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Feature Flags Management */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <ToggleRight className="w-5 h-5 text-indigo-400" />
              Enterprise Feature Flags
            </h3>

            <div className="space-y-4">
              {Object.entries(featureFlags).map(([key, enabled]) => (
                <div
                  key={key}
                  className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between"
                >
                  <div>
                    <div className="text-sm font-bold text-white">{key}</div>
                    <div className="text-xs text-slate-500">
                      {enabled ? "Active for all production users" : "Disabled"}
                    </div>
                  </div>

                  <button
                    onClick={() => toggleFlag(key as keyof typeof featureFlags)}
                    className={`px-4 py-1.5 rounded-xl text-xs font-bold transition ${
                      enabled
                        ? "bg-indigo-600 text-white"
                        : "bg-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {enabled ? "ENABLED" : "DISABLED"}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* System Audit Logs */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Terminal className="w-5 h-5 text-emerald-400" />
              Live System Audit Stream
            </h3>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-xs space-y-3 max-h-72 overflow-y-auto">
              {logs.map((log, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-slate-500">[{log.time}]</span>
                  <span className="text-emerald-400 font-bold">[{log.level}]</span>
                  <span className="text-slate-300">{log.msg}</span>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <CheckCircle className="w-4 h-4" />
              Enterprise Security Audit Log Stream Connected
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
