"use client";

import React from "react";
import { Tag, Zap, Star, ShieldCheck, AlertCircle } from "lucide-react";

interface MarketplaceBadgeProps {
  type: "BEST_PRICE" | "EXPRESS_DELIVERY" | "TOP_RATED" | "OUT_OF_STOCK" | string;
}

export const MarketplaceBadge: React.FC<MarketplaceBadgeProps> = ({ type }) => {
  switch (type) {
    case "BEST_PRICE":
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          <Tag className="h-3 w-3" /> BEST PRICE
        </span>
      );
    case "EXPRESS_DELIVERY":
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
          <Zap className="h-3 w-3" /> EXPRESS
        </span>
      );
    case "TOP_RATED":
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
          <Star className="h-3 w-3 fill-amber-400" /> TOP RATED
        </span>
      );
    case "OUT_OF_STOCK":
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
          <AlertCircle className="h-3 w-3" /> OUT OF STOCK
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-gray-500/10 text-gray-300 border border-gray-500/20">
          <ShieldCheck className="h-3 w-3" /> {type}
        </span>
      );
  }
};
