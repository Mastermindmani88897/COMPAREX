'use client';

import React, { useState } from 'react';

interface CouponProps {
  code: string;
  marketplaceSlug: string;
  title: string;
  description?: string;
  discountType: string;
  discountValue: number;
  minOrderValue: number;
  maxDiscountAmount?: number;
  offerType: string;
  bankName?: string;
  confidenceScore?: number;
}

export default function CouponCard({
  code,
  marketplaceSlug,
  title,
  description,
  discountType,
  discountValue,
  minOrderValue,
  maxDiscountAmount,
  offerType,
  bankName,
  confidenceScore = 0.95,
}: CouponProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-indigo-500/40 transition-all">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            {marketplaceSlug}
          </span>
          {bankName && (
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {bankName}
            </span>
          )}
        </div>
        <h4 className="text-sm font-bold text-white mb-1">{title}</h4>
        {description && <p className="text-xs text-slate-400 mb-2">{description}</p>}
        <div className="text-[11px] text-slate-500 mb-2">
          {offerType} • Min Order: ₹{minOrderValue.toLocaleString('en-IN')}
          {discountType === 'PERCENTAGE' ? ` (${discountValue}% off)` : ` (₹${discountValue} off)`}
          {maxDiscountAmount ? ` up to ₹${maxDiscountAmount}` : ''}
        </div>
      </div>

      <div className="pt-3 border-t border-slate-800 flex items-center justify-between mt-2">
        <div className="flex items-center gap-2">
          <code className="bg-slate-950 px-2.5 py-1 rounded text-xs font-mono text-emerald-400 font-bold border border-slate-800">
            {code}
          </code>
          <span className="text-[10px] text-slate-500">
            {(confidenceScore * 100).toFixed(0)}% Confidence
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="px-3 py-1 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
        >
          {copied ? '✓ Copied' : 'Copy Code'}
        </button>
      </div>
    </div>
  );
}
