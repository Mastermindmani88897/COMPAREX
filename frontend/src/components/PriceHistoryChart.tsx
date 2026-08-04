'use client';

import React from 'react';

interface PricePoint {
  date: string;
  price: number;
  marketplace_slug?: string;
}

interface PriceHistoryProps {
  productName: string;
  todayPrice: number;
  lowestPrice: number;
  highestPrice: number;
  averagePrice: number;
  trend: string;
  volatilityIndex: number;
  buyingPeriod: string;
  predictedPrice: number;
  points?: PricePoint[];
}

export default function PriceHistoryChart({
  productName,
  todayPrice,
  lowestPrice,
  highestPrice,
  averagePrice,
  trend,
  volatilityIndex,
  buyingPeriod,
  predictedPrice,
  points = [],
}: PriceHistoryProps) {
  const getTrendBadge = (t: string) => {
    if (t === 'FALLING') {
      return <span className="px-2 py-1 text-xs font-semibold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">📉 Falling Price</span>;
    }
    if (t === 'RISING') {
      return <span className="px-2 py-1 text-xs font-semibold rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">📈 Price Spiked</span>;
    }
    return <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">⚖️ Stable Price</span>;
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <span>📊 Price History & Trends</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">{productName}</p>
        </div>
        <div className="flex items-center gap-3">
          {getTrendBadge(trend)}
          <span className="px-3 py-1 text-xs font-bold rounded-lg bg-indigo-600/30 text-indigo-300 border border-indigo-500/30">
            {buyingPeriod}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
          <div className="text-xs text-slate-400">Today&apos;s Price</div>
          <div className="text-xl font-extrabold text-white mt-1">₹{todayPrice.toLocaleString('en-IN')}</div>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-xl border border-emerald-500/30">
          <div className="text-xs text-emerald-400 font-medium">30-Day Lowest</div>
          <div className="text-xl font-extrabold text-emerald-400 mt-1">₹{lowestPrice.toLocaleString('en-IN')}</div>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-xl border border-rose-500/30">
          <div className="text-xs text-rose-400 font-medium">30-Day Highest</div>
          <div className="text-xl font-extrabold text-rose-400 mt-1">₹{highestPrice.toLocaleString('en-IN')}</div>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
          <div className="text-xs text-slate-400">Average Price</div>
          <div className="text-xl font-extrabold text-slate-300 mt-1">₹{averagePrice.toLocaleString('en-IN')}</div>
        </div>
      </div>

      {/* Visual Timeline Bars */}
      {points.length > 0 && (
        <div className="mb-6">
          <div className="text-xs font-semibold text-slate-400 mb-3 flex items-center justify-between">
            <span>30-DAY PRICE MOVEMENT CHART</span>
            <span>Predicted Target: ₹{predictedPrice.toLocaleString('en-IN')}</span>
          </div>
          <div className="h-28 flex items-end gap-1.5 p-2 bg-slate-950/60 rounded-xl border border-slate-800">
            {points.slice(-20).map((pt, idx) => {
              const maxP = Math.max(highestPrice, 1);
              const heightPct = Math.max(15, Math.min(100, (pt.price / maxP) * 100));
              const isLowest = pt.price === lowestPrice;

              return (
                <div key={idx} className="flex-1 flex flex-col items-center group relative">
                  <div
                    className={`w-full rounded-t-md transition-all duration-300 ${
                      isLowest ? 'bg-emerald-500 shadow-lg shadow-emerald-500/40' : 'bg-indigo-500/60 group-hover:bg-indigo-400'
                    }`}
                    style={{ height: `${heightPct}%` }}
                  />
                  <div className="opacity-0 group-hover:opacity-100 absolute -top-8 bg-slate-900 text-[10px] text-slate-200 px-2 py-1 rounded shadow border border-slate-700 pointer-events-none whitespace-nowrap z-20">
                    {pt.date}: ₹{pt.price.toLocaleString('en-IN')}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Volatility & Prediction Summary */}
      <div className="flex flex-col md:flex-row items-center justify-between text-xs text-slate-400 bg-slate-800/40 p-4 rounded-xl border border-slate-800 gap-2">
        <div>
          <span className="font-semibold text-slate-300">Price Volatility Index:</span> {(volatilityIndex * 100).toFixed(0)}%
        </div>
        <div>
          <span className="font-semibold text-slate-300">Smart Recommendation:</span> {buyingPeriod}
        </div>
      </div>
    </div>
  );
}
