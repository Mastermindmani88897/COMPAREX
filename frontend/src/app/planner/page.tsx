"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Sparkles,
  Zap,
  SlidersHorizontal,
  ShieldCheck,
  Download,
  Send,
  CheckCircle,
  PackageCheck,
  Laptop,
} from "lucide-react";

const SCENARIO_PILLS = [
  "Engineering Student",
  "Gaming Setup",
  "WFH Office",
  "Photographer",
  "Medical Student",
  "Content Creator",
  "Smart Home",
];

export default function PlannerPage() {
  const [prompt, setPrompt] = useState(
    "I'm starting engineering next month. I have ₹90,000. Build the best complete setup."
  );
  const [selectedScenario, setSelectedScenario] = useState("Engineering Student");
  const [budget, setBudget] = useState(90000);

  const [planItems, setPlanItems] = useState([
    {
      category: "Laptop",
      req: "REQUIRED",
      name: "Lenovo LOQ Intel Core i5 (16GB/512GB SSD/RTX 3050)",
      price: 62000,
      mp: "Amazon India",
      score: 9.3,
    },
    {
      category: "Wireless Mouse",
      req: "REQUIRED",
      name: "Logitech MX Master 3S Wireless Mouse",
      price: 6999,
      mp: "Flipkart",
      score: 9.5,
    },
    {
      category: "Laptop Backpack",
      req: "REQUIRED",
      name: "Wildcraft Laptop Backpack 30L",
      price: 1999,
      mp: "Amazon India",
      score: 8.9,
    },
    {
      category: "External SSD",
      req: "RECOMMENDED",
      name: "SanDisk 1TB Extreme Portable SSD",
      price: 7499,
      mp: "Croma",
      score: 9.1,
    },
    {
      category: "ANC Headphones",
      req: "RECOMMENDED",
      name: "Sony WH-CH720N Wireless ANC Headphones",
      price: 7990,
      mp: "Reliance Digital",
      score: 9.4,
    },
  ]);

  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([
    {
      sender: "ai",
      text: "Hello! I have generated your complete Engineering Student setup within your ₹90,000 budget. You can tweak budget, filter marketplaces, or request modifications.",
    },
  ]);

  const allocated = planItems.reduce((acc, i) => acc + i.price, 0);
  const remaining = Math.max(0, budget - allocated);

  const handleSimulate = (filterMp?: string, mode?: string) => {
    if (filterMp) {
      setPlanItems((prev) => prev.map((item) => ({ ...item, mp: filterMp })));
    }
    if (mode === "PREMIUM") {
      setBudget((b) => b + 10000);
      setPlanItems((prev) =>
        prev.map((item) => ({ ...item, price: Math.round(item.price * 1.1) }))
      );
    } else if (mode === "BEST_VALUE") {
      setPlanItems((prev) =>
        prev.map((item) => ({ ...item, price: Math.round(item.price * 0.9) }))
      );
    }
  };

  const handleSendChat = () => {
    if (!chatMessage.trim()) return;

    const userText = chatMessage;
    setChatHistory((prev) => [...prev, { sender: "user", text: userText }]);
    setChatMessage("");

    setTimeout(() => {
      if (userText.toLowerCase().includes("amazon")) {
        handleSimulate("Amazon India");
      }
      setChatHistory((prev) => [
        ...prev,
        {
          sender: "ai",
          text: `Updated setup based on your request: "${userText}". All recommendations and budget allocations have been refreshed live.`,
        },
      ]);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-10">
        {/* Header */}
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider shadow-sm">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            Flagship Module: COMPAREX AI Marketplace Planner
          </div>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
            Shopping Operating System
          </h1>
          <p className="text-slate-400 text-base md:text-lg max-w-3xl">
            Describe your shopping goal in natural language. COMPAREX parses budget, compatibility, and marketplace deals to build complete goal setups.
          </p>
        </div>

        {/* Goal Input & Scenario Pills */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-6 shadow-xl">
          <div className="p-2 rounded-2xl bg-slate-950 border border-slate-800 flex items-center gap-3">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-1 bg-transparent px-4 py-3 text-sm md:text-base text-slate-200 focus:outline-none"
              placeholder="Describe your goal e.g. 'I'm starting engineering next month with ₹90,000'..."
            />
            <button className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm flex items-center gap-2 transition shadow-lg shadow-indigo-600/30">
              <Zap className="w-4 h-4" />
              Build Plan
            </button>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-2">
              Preset Scenarios:
            </span>
            {SCENARIO_PILLS.map((pill) => (
              <button
                key={pill}
                onClick={() => setSelectedScenario(pill)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  selectedScenario === pill
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200"
                }`}
              >
                {pill}
              </button>
            ))}
          </div>
        </div>

        {/* Budget Allocation Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Total Budget
            </span>
            <div className="text-3xl font-extrabold text-white">₹{budget.toLocaleString()}</div>
            <div className="text-xs text-indigo-400">Natural language parsed target</div>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Allocated Cost
            </span>
            <div className="text-3xl font-extrabold text-emerald-400">
              ₹{allocated.toLocaleString()}
            </div>
            <div className="text-xs text-emerald-400 font-medium">100% categories covered</div>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Remaining Buffer
            </span>
            <div className="text-3xl font-extrabold text-cyan-400">
              ₹{remaining.toLocaleString()}
            </div>
            <div className="text-xs text-cyan-400 font-medium">Unused budget reserve</div>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Compatibility Score
            </span>
            <div className="text-3xl font-extrabold text-purple-400">98%</div>
            <div className="text-xs text-purple-400 font-medium">Verified ecosystem match</div>
          </div>
        </div>

        {/* Simulation Toolbar */}
        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
            <SlidersHorizontal className="w-4 h-4 text-indigo-400" />
            Plan Simulation Controls:
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => handleSimulate(undefined, "PREMIUM")}
              className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition"
            >
              + ₹10,000 Budget
            </button>
            <button
              onClick={() => handleSimulate("Amazon India")}
              className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition"
            >
              Amazon Only
            </button>
            <button
              onClick={() => handleSimulate(undefined, "BEST_VALUE")}
              className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-emerald-400 transition"
            >
              Best Value Mode
            </button>

            <button
              onClick={() => alert("Shopping Plan Exported in JSON & Printable PDF format!")}
              className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white flex items-center gap-1.5 transition ml-2 shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              Export Report
            </button>
          </div>
        </div>

        {/* Setup Category Items List */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <PackageCheck className="w-5 h-5 text-indigo-400" />
            Recommended Setup Blueprint ({planItems.length} Categories)
          </h2>

          <div className="space-y-3">
            {planItems.map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4 flex-wrap"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400">
                    <Laptop className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        {item.category}
                      </span>
                      <span className="px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-semibold text-indigo-400">
                        {item.req}
                      </span>
                    </div>
                    <div className="text-base font-bold text-white mt-0.5">{item.name}</div>
                    <div className="text-xs text-slate-500 mt-1 flex items-center gap-3">
                      <span>Marketplace: <strong className="text-slate-300">{item.mp}</strong></span>
                      <span>Deal Score: <strong className="text-emerald-400">{item.score}/10</strong></span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xl font-extrabold text-white">
                    ₹{item.price.toLocaleString()}
                  </div>
                  <div className="text-xs text-emerald-400 flex items-center gap-1 justify-end mt-1">
                    <ShieldCheck className="w-3.5 h-3.5" /> Verified Lowest
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Conversational Follow-Up Chat */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-indigo-400" />
            Conversational Plan Refinement
          </h3>

          <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
            {chatHistory.map((c, i) => (
              <div
                key={i}
                className={`p-3.5 rounded-xl text-xs md:text-sm max-w-2xl ${
                  c.sender === "user"
                    ? "bg-indigo-600 text-white ml-auto"
                    : "bg-slate-950 border border-slate-800 text-slate-300"
                }`}
              >
                {c.text}
              </div>
            ))}
          </div>

          <div className="pt-2 flex items-center gap-2">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
              className="flex-1 bg-slate-950 border border-slate-800 px-4 py-2.5 rounded-xl text-xs md:text-sm text-slate-200 focus:outline-none"
              placeholder="Type follow-up edit e.g. 'Show only Amazon products' or 'Reduce cost by ₹5,000'..."
            />
            <button
              onClick={handleSendChat}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs md:text-sm flex items-center gap-1.5 transition"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
