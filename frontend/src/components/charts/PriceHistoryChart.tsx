"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { TrendingDown, TrendingUp, Minus, Calendar, Sparkles, RefreshCw, Layers, Check } from "lucide-react";
import { priceHistoryService } from "@/services/api";

interface PriceHistoryChartProps {
  productId: string;
  productName: string;
  basePrice?: number;
}

interface StoreConfig {
  name: string;
  slug: string;
  color: string;
}

export function PriceHistoryChart({
  productId,
  productName,
  basePrice,
}: PriceHistoryChartProps) {

  const [timeRange, setTimeRange] = useState<string>("30d");
  const [activeStores, setActiveStores] = useState<Record<string, boolean>>({
    amazon: true,
    flipkart: true,
    croma: true,
    reliance_digital: true,
    tata_cliq: true,
    vijay_sales: true,
    meesho: true,
    myntra: true,
  });

  const [historyData, setHistoryData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [hoveredPoint, setHoveredPoint] = useState<any>(null);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const res = await priceHistoryService.getProductHistory(productId, {
        product_name: productName,
        base_price: basePrice,
        time_range: timeRange,
      });
      if (res.data?.data) {
        setHistoryData(res.data.data);
      }
    } catch (err) {
      console.error("Error fetching price history graph data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [productId, timeRange]);

  const toggleStore = (slug: string) => {
    setActiveStores((prev) => ({
      ...prev,
      [slug]: !prev[slug],
    }));
  };

  if (isLoading) {
    return (
      <div className="p-12 rounded-3xl border text-center space-y-3" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-400 mx-auto" />
        <p className="text-xs font-semibold" style={{ color: "var(--foreground-muted)" }}>
          Loading interactive price history graph...
        </p>
      </div>
    );
  }

  if (
    !historyData ||
    historyData.has_sufficient_history === false ||
    !historyData.points ||
    historyData.points.length < 2
  ) {
    const obsCount: number = historyData?.verified_observation_count ?? historyData?.total_points ?? 0;
    const curPrice = historyData?.today_price || historyData?.current_live_price || basePrice || 0;
    const lowPrice = historyData?.lowest_price || curPrice;
    const highPrice = historyData?.highest_price || curPrice;
    const avgPrice = historyData?.average_price || curPrice;

    return (
      <div
        className="rounded-3xl border p-6 sm:p-8 space-y-6 shadow-xl"
        style={{ background: "var(--card)", borderColor: "var(--border)" }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b pb-4" style={{ borderColor: "var(--border)" }}>
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Calendar className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold" style={{ color: "var(--foreground)" }}>
                Price History & Market Trend
              </h3>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Persistent verified price snapshot tracking.
              </p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 w-fit">
            Collecting verified price history
          </span>
        </div>

        {/* Live Market Stats Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-4 rounded-2xl border bg-emerald-500/5 border-emerald-500/20">
            <span className="text-[11px] font-semibold text-emerald-400 block">Lowest Verified</span>
            <p className="text-xl font-black text-emerald-300 mt-1">
              {lowPrice > 0 ? `₹${Number(lowPrice).toLocaleString("en-IN")}` : "Collecting"}
            </p>
          </div>
          <div className="p-4 rounded-2xl border bg-indigo-500/5 border-indigo-500/20">
            <span className="text-[11px] font-semibold text-indigo-400 block">Market Average</span>
            <p className="text-xl font-black text-indigo-300 mt-1">
              {avgPrice > 0 ? `₹${Number(avgPrice).toLocaleString("en-IN")}` : "Collecting"}
            </p>
          </div>
          <div className="p-4 rounded-2xl border bg-rose-500/5 border-rose-500/20">
            <span className="text-[11px] font-semibold text-rose-400 block">Highest Price</span>
            <p className="text-xl font-black text-rose-300 mt-1">
              {highPrice > 0 ? `₹${Number(highPrice).toLocaleString("en-IN")}` : "Collecting"}
            </p>
          </div>
          <div className="p-4 rounded-2xl border bg-purple-500/5 border-purple-500/20">
            <span className="text-[11px] font-semibold text-purple-400 block">Verified Snapshots</span>
            <p className="text-xl font-black text-purple-300 mt-1">
              {obsCount} observation{obsCount === 1 ? "" : "s"}
            </p>
          </div>
        </div>

        <div className="p-4 rounded-2xl border bg-amber-500/10 border-amber-500/20 text-xs leading-relaxed text-amber-300 flex items-start gap-2.5">
          <Sparkles className="h-4 w-4 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block">History & Trend Snapshot System Active</span>
            CompareX automatically records persistent price snapshots when verified marketplace prices are observed. The interactive line chart will render automatically as snapshots accumulate.
          </div>
        </div>
      </div>
    );
  }

  const {
    stores = [],
    price_points = [],
    lowest_recorded_price = 0,
    highest_recorded_price = 0,
    average_price = 0,
    current_live_price = 0,
    trend_badge = "⚠ Insufficient Data",
    best_time_to_buy = "Insufficient Data",
    gemini_prediction = "",
    price_change = null,
    price_change_percent = null,
    direction = null,
    verified_observation_count = 0,
  } = historyData;


  // Calculate SVG graph dimensions & scaling
  const visibleStores = stores.filter((s: StoreConfig) => activeStores[s.slug]);
  const width = 800;
  const height = 300;
  const padding = 40;

  // Find min/max values across visible stores
  let globalMin = Infinity;
  let globalMax = -Infinity;

  price_points.forEach((pt: any) => {
    visibleStores.forEach((s: StoreConfig) => {
      const v = pt[s.slug];
      if (v !== undefined) {
        if (v < globalMin) globalMin = v;
        if (v > globalMax) globalMax = v;
      }
    });
  });

  if (globalMin === Infinity) globalMin = current_live_price * 0.9;
  if (globalMax === -Infinity) globalMax = current_live_price * 1.1;

  const priceRange = globalMax - globalMin || 1;

  // Generate SVG polyline points per store
  const storePolylines: Record<string, string> = {};
  visibleStores.forEach((s: StoreConfig) => {
    const slug = s.slug;
    const pts = price_points.map((pt: any, idx: number) => {
      const x = padding + (idx / (price_points.length - 1 || 1)) * (width - 2 * padding);
      const val = pt[slug] || current_live_price;
      const y = height - padding - ((val - globalMin) / priceRange) * (height - 2 * padding);
      return `${x},${y}`;
    });
    storePolylines[slug] = pts.join(" ");
  });

  return (
    <div className="rounded-3xl border p-6 sm:p-8 space-y-6 shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
      {/* Header & Time Filters */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b pb-6" style={{ borderColor: "var(--border)" }}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>
              Price History & Market Trend
            </h2>
            <span className={`px-3 py-1 rounded-full text-xs font-black shadow-sm ${
              trend_badge.includes("Dropping") || trend_badge.includes("Falling") ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" :
              trend_badge.includes("Rising") ? "bg-rose-500/20 text-rose-400 border border-rose-500/30" :
              trend_badge.includes("Insufficient") ? "bg-gray-500/20 text-gray-400 border border-gray-500/30" :
              "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
            }`}>
              {trend_badge}
            </span>
            {price_change !== null && price_change_percent !== null && (
              <span className={`text-xs font-bold px-2 py-0.5 rounded-lg ${
                direction === "down" ? "text-emerald-400 bg-emerald-500/10" :
                direction === "up" ? "text-rose-400 bg-rose-500/10" :
                "text-gray-400 bg-gray-500/10"
              }`}>
                {price_change > 0 ? "+" : ""}{Number(price_change).toLocaleString("en-IN", { maximumFractionDigits: 0 })} ({price_change_percent > 0 ? "+" : ""}{Number(price_change_percent).toFixed(1)}%)
              </span>
            )}
          </div>
          <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
            Historical price comparison across Indian marketplaces over time.
            {verified_observation_count > 0 && ` · ${verified_observation_count} verified observations.`}
          </p>
        </div>

        {/* Time Filters */}
        <div className="flex flex-wrap items-center gap-1.5 p-1.5 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
          {[
            { id: "24h", label: "24H" },
            { id: "7d", label: "7D" },
            { id: "30d", label: "30D" },
            { id: "3m", label: "3M" },
            { id: "6m", label: "6M" },
            { id: "1y", label: "1Y" },
            { id: "all", label: "All" },
          ].map((tf) => (
            <button
              key={tf.id}
              onClick={() => setTimeRange(tf.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                timeRange === tf.id
                  ? "gradient-bg text-white shadow-md"
                  : "hover:text-indigo-400 text-gray-400"
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Key Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
          <span className="text-[11px] font-semibold block" style={{ color: "var(--foreground-muted)" }}>
            Current Live Price
          </span>
          <p className="text-xl sm:text-2xl font-black text-indigo-400">
            ₹{Number(current_live_price).toLocaleString("en-IN")}
          </p>
        </div>

        <div className="p-4 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
          <span className="text-[11px] font-semibold block" style={{ color: "var(--foreground-muted)" }}>
            Lowest Recorded
          </span>
          <p className="text-xl sm:text-2xl font-black text-emerald-400">
            ₹{Number(lowest_recorded_price).toLocaleString("en-IN")}
          </p>
        </div>

        <div className="p-4 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
          <span className="text-[11px] font-semibold block" style={{ color: "var(--foreground-muted)" }}>
            Highest Recorded
          </span>
          <p className="text-xl sm:text-2xl font-black text-rose-400">
            ₹{Number(highest_recorded_price).toLocaleString("en-IN")}
          </p>
        </div>

        <div className="p-4 rounded-2xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
          <span className="text-[11px] font-semibold block" style={{ color: "var(--foreground-muted)" }}>
            Average Price
          </span>
          <p className="text-xl sm:text-2xl font-black" style={{ color: "var(--foreground)" }}>
            ₹{Number(average_price).toLocaleString("en-IN")}
          </p>
        </div>
      </div>

      {/* Interactive Marketplace Legend Toggle */}
      <div className="space-y-2">
        <span className="text-xs font-bold block" style={{ color: "var(--foreground)" }}>
          Toggle Marketplaces On/Off:
        </span>
        <div className="flex flex-wrap items-center gap-2">
          {stores.map((s: StoreConfig) => {
            const isSelected = activeStores[s.slug];
            return (
              <button
                key={s.slug}
                onClick={() => toggleStore(s.slug)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold border transition-all ${
                  isSelected ? "shadow-sm scale-105" : "opacity-40 grayscale"
                }`}
                style={{
                  background: "var(--background)",
                  borderColor: isSelected ? s.color : "var(--border)",
                  color: "var(--foreground)",
                }}
              >
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: s.color }} />
                <span>{s.name}</span>
                {isSelected && <Check className="h-3.5 w-3.5 text-indigo-400" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* SVG Interactive Multi-Line Chart Container */}
      <div className="relative w-full overflow-hidden rounded-2xl border p-4" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto overflow-visible"
        >
          {/* Horizontal Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
            const y = height - padding - ratio * (height - 2 * padding);
            const priceVal = Math.round(globalMin + ratio * priceRange);
            return (
              <g key={idx}>
                <line
                  x1={padding}
                  y1={y}
                  x2={width - padding}
                  y2={y}
                  stroke="var(--border)"
                  strokeDasharray="4 4"
                  strokeOpacity={0.5}
                />
                <text
                  x={padding - 8}
                  y={y + 4}
                  fill="var(--foreground-muted)"
                  fontSize={10}
                  textAnchor="end"
                >
                  ₹{priceVal.toLocaleString("en-IN")}
                </text>
              </g>
            );
          })}

          {/* Render Multi-colored lines for each active store */}
          {visibleStores.map((s: StoreConfig) => (
            <polyline
              key={s.slug}
              fill="none"
              stroke={s.color}
              strokeWidth={2.5}
              strokeLinecap="round"
              strokeLinejoin="round"
              points={storePolylines[s.slug]}
            />
          ))}

          {/* Interactive Data Point Dots & Hover Handler */}
          {price_points.map((pt: any, idx: number) => {
            const x = padding + (idx / (price_points.length - 1 || 1)) * (width - 2 * padding);

            return (
              <g key={idx} className="group cursor-pointer">
                <line
                  x1={x}
                  y1={padding}
                  x2={x}
                  y2={height - padding}
                  stroke="transparent"
                  strokeWidth={12}
                  onMouseEnter={() => setHoveredPoint(pt)}
                />
                {visibleStores.map((s: StoreConfig) => {
                  const val = pt[s.slug];
                  if (val === undefined) return null;
                  const y = height - padding - ((val - globalMin) / priceRange) * (height - 2 * padding);
                  return (
                    <circle
                      key={s.slug}
                      cx={x}
                      cy={y}
                      r={3.5}
                      fill={s.color}
                      className="transition-transform group-hover:r-6"
                      onMouseEnter={() => setHoveredPoint(pt)}
                    />
                  );
                })}
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoveredPoint && (
          <div className="mt-3 p-3 rounded-xl border bg-black/80 text-white backdrop-blur-md text-xs flex flex-wrap items-center justify-between gap-4">
            <span className="font-bold text-amber-400">Date: {hoveredPoint.date}</span>
            <div className="flex flex-wrap items-center gap-3">
              {visibleStores.map((s: StoreConfig) => (
                <div key={s.slug} className="flex items-center gap-1">
                  <span className="h-2 w-2 rounded-full" style={{ backgroundColor: s.color }} />
                  <span className="font-semibold">{s.name}:</span>
                  <span className="font-bold">₹{Number(hoveredPoint[s.slug] || 0).toLocaleString("en-IN")}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Gemini AI Prediction & Buying Advice Banner */}
      <div className="p-5 rounded-2xl border space-y-2 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-amber-500/10 border-indigo-500/20">
        <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
          <Sparkles className="h-4 w-4" /> Gemini AI Price Trend Insight
        </div>
        <p className="text-xs leading-relaxed font-semibold" style={{ color: "var(--foreground)" }}>
          {gemini_prediction}
        </p>
        <span className="inline-block text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
          💡 Recommendation: {best_time_to_buy}
        </span>
      </div>
    </div>
  );
}
