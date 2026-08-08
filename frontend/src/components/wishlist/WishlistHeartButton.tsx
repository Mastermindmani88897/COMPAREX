"use client";

import { useState } from "react";
import { Heart } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useWishlist } from "@/context/WishlistContext";

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
  onToggle,
  className = "",
  size = "md",
}: WishlistHeartButtonProps) {
  const { user } = useAuth();
  const { isInWishlist, addToWishlist, removeFromWishlist } = useWishlist();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const isWishlisted = isInWishlist(productId);

  const iconSizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
  };

  const handleToggle = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!user) {
      window.location.href = "/login";
      return;
    }

    setIsSubmitting(true);
    try {
      if (isWishlisted) {
        await removeFromWishlist(productId);
        if (onToggle) onToggle(false);
      } else {
        await addToWishlist(productId);
        if (onToggle) onToggle(true);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleToggle}
      disabled={isSubmitting}
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

