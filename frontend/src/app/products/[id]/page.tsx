"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  ShoppingBag,
  ChevronLeft,
  Tag,
  ExternalLink,
  Star,
  TrendingDown,
  AlertCircle,
  Loader2,
  CheckCircle2,
  XCircle,
  Award,
  GitCompare,
} from "lucide-react";
import apiClient from "@/services/api";
import type { Product, PriceCompareResult } from "@/types";

export default function ProductDetailPage() {
  const params = useParams();
  const productId = params.id as string;

  const [product, setProduct] = useState<Product | null>(null);
  const [compareData, setCompareData] = useState<PriceCompareResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadProduct() {
      setError(null);
      try {
        const prodRes = await apiClient.get(`/products/${productId}`);
        if (isMounted) {
          setProduct(prodRes.data.data);
        }

        try {
          const compRes = await apiClient.get(`/products/${productId}/compare`);
          if (isMounted) {
            setCompareData(compRes.data);
          }
        } catch {
          // Listings comparison might be empty
        }
      } catch {
        if (isMounted) {
          setError("Product not found or failed to load details.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    if (productId) {
      loadProduct();
    }

    return () => {
      isMounted = false;
    };
  }, [productId]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--background)" }}>
        <Loader2 className="h-8 w-8 animate-spin text-indigo-400" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen py-24 px-4 text-center" style={{ background: "var(--background)" }}>
        <div className="max-w-md mx-auto space-y-4">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto" />
          <h1 className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
            Product Not Found
          </h1>
          <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
            {error || "The requested product does not exist."}
          </p>
          <Link
            href="/products"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl gradient-bg text-white text-sm font-semibold"
          >
            <ChevronLeft className="h-4 w-4" /> Back to Catalog
          </Link>
        </div>
      </div>
    );
  }

  const listings = compareData?.listings || [];

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8" style={{ background: "var(--background)", paddingTop: "88px" }}>
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Back Link */}
        <div className="flex items-center justify-between">
          <Link
            href="/products"
            className="inline-flex items-center gap-2 text-sm font-medium hover:text-indigo-400 transition-colors"
            style={{ color: "var(--foreground-muted)" }}
          >
            <ChevronLeft className="h-4 w-4" /> Back to Products
          </Link>

          <Link
            href={`/compare/${product.id}`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold gradient-bg text-white shadow-md"
          >
            <GitCompare className="h-4 w-4" /> Full Comparison View
          </Link>
        </div>

        {/* Product Overview Card */}
        <div className="rounded-2xl p-6 sm:p-8 border grid grid-cols-1 md:grid-cols-3 gap-8" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          {/* Image Column */}
          <div className="flex items-center justify-center p-6 rounded-xl border" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
            {product.image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={product.image_url} alt={product.name} className="max-h-56 object-contain" />
            ) : (
              <ShoppingBag className="h-24 w-24 text-indigo-400" />
            )}
          </div>

          {/* Info Column */}
          <div className="md:col-span-2 space-y-4 flex flex-col justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                {product.brand && (
                  <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 font-semibold">
                    <Tag className="h-3 w-3" /> {product.brand}
                  </span>
                )}
                {product.category && (
                  <span className="text-xs px-2.5 py-1 rounded-full border" style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}>
                    {product.category}
                  </span>
                )}
              </div>

              <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: "var(--foreground)" }}>
                {product.name}
              </h1>

              {product.description && (
                <p className="mt-3 text-sm leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  {product.description}
                </p>
              )}
            </div>

            {/* Price Summary Banner */}
            <div className="p-4 rounded-xl border flex flex-wrap items-center justify-between gap-4" style={{ background: "var(--background)", borderColor: "var(--border)" }}>
              <div>
                <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  Base Catalog Price
                </span>
                <p className="text-2xl font-bold gradient-text">
                  ₹{Number(product.base_price || 0).toLocaleString("en-IN")}
                </p>
              </div>

              {compareData?.lowest_price && (
                <div className="text-right">
                  <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1 justify-end">
                    <TrendingDown className="h-3.5 w-3.5" /> Best Deal Available
                  </span>
                  <p className="text-xl font-bold text-emerald-400">
                    ₹{Number(compareData.lowest_price).toLocaleString("en-IN")}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Marketplace Comparison Matrix */}
        <div className="rounded-2xl border p-6 sm:p-8 space-y-6" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
          <div className="flex items-center justify-between border-b pb-4" style={{ borderColor: "var(--border)" }}>
            <div>
              <h2 className="text-xl font-bold" style={{ color: "var(--foreground)" }}>
                Marketplace Price Comparison
              </h2>
              <p className="text-xs mt-0.5" style={{ color: "var(--foreground-muted)" }}>
                Compare current live prices across supported online retailers.
              </p>
            </div>

            {compareData && (
              <span className="text-xs font-medium px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400">
                {listings.length} Offer{listings.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>

          {listings.length === 0 ? (
            <div className="text-center py-12 space-y-2">
              <ShoppingBag className="h-10 w-10 text-gray-500 mx-auto" />
              <p className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
                No marketplace listings found
              </p>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Prices for this product will update automatically once marketplace crawlers run.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {listings.map((lst) => {
                const isBestDeal = compareData?.best_listing_id === lst.id;
                return (
                  <motion.div
                    key={lst.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-4 sm:p-5 rounded-xl border flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 transition-all ${
                      isBestDeal ? "border-emerald-500/50 bg-emerald-500/5" : ""
                    }`}
                    style={{
                      background: isBestDeal ? "rgba(16,185,129,0.05)" : "var(--background)",
                      borderColor: isBestDeal ? "rgba(16,185,129,0.4)" : "var(--border)",
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-xl gradient-bg flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                        {lst.marketplace?.name ? lst.marketplace.name[0] : "M"}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                            {lst.marketplace?.name || "Marketplace Store"}
                          </h3>
                          {isBestDeal && (
                            <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500 text-white">
                              <Award className="h-3 w-3" /> BEST PRICE
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-3 text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                          {lst.seller_name && <span>Seller: {lst.seller_name}</span>}
                          {lst.rating && (
                            <span className="flex items-center gap-1 text-amber-400 font-semibold">
                              <Star className="h-3 w-3 fill-amber-400" /> {lst.rating}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            {lst.is_available ? (
                              <span className="text-emerald-400 flex items-center gap-1"><CheckCircle2 className="h-3 w-3" /> In Stock</span>
                            ) : (
                              <span className="text-red-400 flex items-center gap-1"><XCircle className="h-3 w-3" /> Out of Stock</span>
                            )}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between sm:justify-end gap-6 pt-3 sm:pt-0 border-t sm:border-t-0" style={{ borderColor: "var(--border)" }}>
                      <div className="text-left sm:text-right">
                        <p className="text-xl font-bold gradient-text">
                          ₹{Number(lst.price).toLocaleString("en-IN")}
                        </p>
                        {lst.original_price && Number(lst.original_price) > Number(lst.price) && (
                          <p className="text-xs line-through" style={{ color: "var(--foreground-muted)" }}>
                            ₹{Number(lst.original_price).toLocaleString("en-IN")}
                          </p>
                        )}
                      </div>

                      <a
                        href={lst.listing_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold gradient-bg text-white hover:opacity-90 transition-opacity"
                      >
                        Buy Now <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
