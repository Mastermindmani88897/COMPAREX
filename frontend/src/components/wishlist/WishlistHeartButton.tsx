"use client";

import { useEffect, useState } from "react";
import { Heart } from "lucide-react";
import apiClient from "@/services/api";
import { useAuth } from "@/context/AuthContext";

interface WishlistHeartButtonProps {
  productId: string;
  initialIsWishlisted?: boolean;
  wishlistItemId?: string;
  onToggle?: (isWishlisted: boolean) => void;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function WishlistHeartButton({
  productId,
  initialIsWishlisted = false,
  wishlistItemId,
  onToggle,
  className = "",
  size = "md",
}: WishlistHeartButtonProps) {
  const { user } = useAuth();
  const [isWishlisted, setIsWishlisted] = useState<boolean>(initialIsWishlisted);
  const [itemId, setItemId] = useState<string | undefined>(wishlistItemId);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const iconSizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
  };

  useEffect(() => {
    let isMounted = true;
    setIsWishlisted(initialIsWishlisted);

    if (user && productId && !initialIsWishlisted) {
      apiClient
        .get("/wishlist")
        .then((res) => {
          if (!isMounted) return;
          const items = res.data?.data?.items || [];
          const match = items.find(
            (i: { product_id: string; product?: { id: string }; id: string }) =>
              i.product_id === productId || i.product?.id === productId
          );
          if (match) {
            setIsWishlisted(true);
            setItemId(match.id);
          }
        })
        .catch(() => {
          // Ignore error silently on initial state check
        });
    }

    return () => {
      isMounted = false;
    };
  }, [user, productId, initialIsWishlisted]);

  const handleToggle = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!user) {
      window.location.href = "/login";
      return;
    }

    const nextState = !isWishlisted;
    setIsWishlisted(nextState);
    setIsLoading(true);

    try {
      if (nextState) {
        // Add to wishlist
        const res = await apiClient.post("/wishlist", {
          product_id: productId,
          preferred_marketplace: "Amazon",
        });
        if (res.data?.data?.id) {
          setItemId(res.data.data.id);
        }
      } else {
        // Remove from wishlist
        const targetId = itemId || wishlistItemId || productId;
        await apiClient.delete(`/wishlist/${targetId}`);
        setItemId(undefined);
      }

      if (onToggle) {
        onToggle(nextState);
      }
    } catch (err) {
      console.error("Failed to update wishlist:", err);
      // Revert on error
      setIsWishlisted(!nextState);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleToggle}
      disabled={isLoading}
      className={`p-2 rounded-xl transition-all duration-200 ${
        isWishlisted
          ? "bg-rose-500/10 text-rose-500 border border-rose-500/20 scale-105"
          : "bg-gray-500/10 text-gray-400 hover:text-rose-500 hover:bg-rose-500/10 border border-transparent"
      } ${className}`}
      title={isWishlisted ? "Remove from Wishlist" : "Add to Wishlist"}
    >
      <Heart
        className={`${iconSizes[size]} transition-all ${
          isWishlisted ? "fill-rose-500 stroke-rose-500" : "stroke-current"
        }`}
      />
    </button>
  );
}

