"use client";

import { useState } from "react";
import Link from "next/link";
import { ExternalLink, GitCompare, Heart, Bell, Check } from "lucide-react";
import { useWishlist } from "@/context/WishlistContext";
import { PriceAlertModal } from "@/components/alerts/PriceAlertModal";

export interface ProductLike {
  id: string;
  product_id?: string;
  name?: string;
  title?: string;
  base_price?: number | null;
  price?: number | null;
  listing_url?: string | null;
  listings?: Array<{ listing_url?: string | null }>;
  product_url?: string | null;
}

interface ProductActionButtonsProps {
  product: ProductLike;
  compact?: boolean;
}

export function ProductActionButtons({ product, compact = false }: ProductActionButtonsProps) {
  const resolvedId = product.id || product.product_id || "";
  const resolvedName = product.name || product.title || "Product";
  const resolvedPrice = Number(product.base_price || product.price || 0);

  const { isInWishlist, addToWishlist, removeFromWishlist } = useWishlist();
  const inWishlist = resolvedId ? isInWishlist(resolvedId) : false;

  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
  const [isAlertActive, setIsAlertActive] = useState(false);

  // Extract verified retailer URL
  const verifiedRetailerUrl =
    product.listing_url ||
    (product.listings && product.listings.length > 0 ? product.listings[0].listing_url : null) ||
    product.product_url ||
    null;

  const handleWishlistClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!resolvedId) return;

    if (inWishlist) {
      await removeFromWishlist(resolvedId);
    } else {
      await addToWishlist(resolvedId);
    }
  };

  const handleAlertClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsAlertModalOpen(true);
  };

  return (
    <>
      <div className={`flex items-center flex-wrap gap-2 ${compact ? "mt-2" : "mt-4"}`}>
        {/* View Product */}
        {resolvedId && (
          <Link
            href={`/products/${resolvedId}`}
            className="inline-flex items-center justify-center px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all hover:border-indigo-500 hover:text-indigo-400"
            style={{ borderColor: "var(--border)", color: "var(--foreground)", background: "var(--card)" }}
          >
            View Product
          </Link>
        )}

        {/* Compare */}
        {resolvedId && (
          <Link
            href={`/compare?ids=${resolvedId}`}
            className="inline-flex items-center justify-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all hover:border-purple-500 hover:text-purple-400"
            style={{ borderColor: "var(--border)", color: "var(--foreground)", background: "var(--card)" }}
          >
            <GitCompare className="h-3.5 w-3.5" />
            Compare
          </Link>
        )}

        {/* Wishlist Button */}
        {resolvedId && (
          <button
            onClick={handleWishlistClick}
            className={`inline-flex items-center justify-center p-2 rounded-xl border transition-all ${
              inWishlist
                ? "bg-rose-500/10 border-rose-500/30 text-rose-500"
                : "border-gray-700/40 text-gray-400 hover:text-rose-400 hover:border-rose-400/30"
            }`}
            title={inWishlist ? "Remove from Wishlist" : "Add to Wishlist"}
          >
            <Heart className={`h-3.5 w-3.5 ${inWishlist ? "fill-rose-500 text-rose-500" : ""}`} />
          </button>
        )}

        {/* Price Alert Button */}
        {resolvedId && (
          <button
            onClick={handleAlertClick}
            className={`inline-flex items-center justify-center gap-1 p-2 rounded-xl border transition-all ${
              isAlertActive
                ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
                : "border-gray-700/40 text-gray-400 hover:text-amber-400 hover:border-amber-400/30"
            }`}
            title="Configure Price Drop Alert"
          >
            {isAlertActive ? <Check className="h-3.5 w-3.5 text-amber-400" /> : <Bell className="h-3.5 w-3.5" />}
          </button>
        )}

        {/* Buy Now (Verified Retailer URL only) */}
        {verifiedRetailerUrl && verifiedRetailerUrl.startsWith("http") ? (
          <a
            href={verifiedRetailerUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-1 px-3.5 py-1.5 rounded-xl text-xs font-bold gradient-bg text-white shadow-md transition-all hover:opacity-90 ml-auto"
          >
            Buy Now <ExternalLink className="h-3 w-3" />
          </a>
        ) : (
          <span className="text-[11px] text-gray-500 italic ml-auto self-center">
            Marketplace link unavailable
          </span>
        )}
      </div>

      {/* Price Alert Modal */}
      {isAlertModalOpen && resolvedId && (
        <PriceAlertModal
          isOpen={isAlertModalOpen}
          onClose={() => {
            setIsAlertModalOpen(false);
            setIsAlertActive(true);
          }}
          productId={resolvedId}
          productName={resolvedName}
          currentPrice={resolvedPrice > 0 ? resolvedPrice : 19999}
        />
      )}
    </>
  );
}
