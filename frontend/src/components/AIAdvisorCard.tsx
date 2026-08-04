'use client';

import React from 'react';

interface Alternative {
  product_name: string;
  price: number;
  marketplace_name: string;
  tier: string;
  reasoning: string;
}

interface AIAdvisorProps {
  productName: string;
  currentPrice: number;
  verdict: string;
  verdictReasoning: string;
  expectedFuturePrice: number;
  valueForMoneyScore: number;
  riskAnalysis?: string[];
  budgetAlternatives?: Alternative[];
  premiumAlternatives?: Alternative[];
}

export default function AIAdvisorCard({
  productName,
  currentPrice,
  verdict,
  verdictReasoning,
  expectedFuturePrice,
  valueForMoneyScore,
  riskAnalysis = [],
  budgetAlternatives = [],
  premiumAlternatives = [],
}: AIAdvisorProps) {
  const isBuyNow = verdict === 'BUY_NOW';

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <span>🧠 COMPAREX AI Advisor: {productName}</span>
        </h3>
        <div className={`px-4 py-1.5 rounded-full text-xs font-black tracking-wide border ${
          isBuyNow
            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-lg shadow-emerald-500/20'
            : 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-lg shadow-amber-500/20'
        }`}>
          {isBuyNow ? '⚡ BUY NOW' : '⏳ WAIT FOR SALE'}
        </div>
      </div>

      <p className="text-sm text-slate-300 mb-6 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800">
        {verdictReasoning}
      </p>

      {/* Grid Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
          <div className="text-xs text-slate-400">Current Price</div>
          <div className="text-lg font-bold text-white mt-1">₹{currentPrice.toLocaleString('en-IN')}</div>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
          <div className="text-xs text-slate-400">Expected Sale Price</div>
          <div className="text-lg font-bold text-indigo-400 mt-1">₹{expectedFuturePrice.toLocaleString('en-IN')}</div>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
          <div className="text-xs text-slate-400">Value For Money Score</div>
          <div className="text-lg font-bold text-emerald-400 mt-1">{valueForMoneyScore} / 10</div>
        </div>
      </div>

      {/* Risk Analysis */}
      {riskAnalysis.length > 0 && (
        <div className="mb-6">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Market Risk Analysis
          </h4>
          <ul className="space-y-1.5 text-xs text-slate-300">
            {riskAnalysis.map((risk, idx) => (
              <li key={idx} className="flex items-center gap-2">
                <span className="text-amber-400">⚠️</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Alternatives */}
      {(budgetAlternatives.length > 0 || premiumAlternatives.length > 0) && (
        <div className="pt-4 border-t border-slate-800">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
            Smart Alternatives
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {budgetAlternatives.map((alt, idx) => (
              <div key={idx} className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
                  BUDGET PICK
                </span>
                <div className="text-xs font-bold text-white mt-1.5">{alt.product_name}</div>
                <div className="text-xs text-emerald-400 font-semibold mt-0.5">₹{alt.price.toLocaleString('en-IN')}</div>
                <div className="text-[11px] text-slate-400 mt-1">{alt.reasoning}</div>
              </div>
            ))}

            {premiumAlternatives.map((alt, idx) => (
              <div key={idx} className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400">
                  PREMIUM UPGRADE
                </span>
                <div className="text-xs font-bold text-white mt-1.5">{alt.product_name}</div>
                <div className="text-xs text-indigo-400 font-semibold mt-0.5">₹{alt.price.toLocaleString('en-IN')}</div>
                <div className="text-[11px] text-slate-400 mt-1">{alt.reasoning}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
