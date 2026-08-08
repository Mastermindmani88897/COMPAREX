"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { wishlistService } from "@/services/api";
import { useAuth } from "@/context/AuthContext";
import type { WishlistItem } from "@/types";

interface WishlistContextType {
  wishlistItems: WishlistItem[];
  wishlistCount: number;
  totalSavings: number;
  isLoading: boolean;
  addToWishlist: (productId: string, preferredMarketplace?: string, targetPrice?: number, notes?: string) => Promise<boolean>;
  removeFromWishlist: (idOrProductId: string) => Promise<boolean>;
  isInWishlist: (productId: string) => boolean;
  getWishlistItem: (productId: string) => WishlistItem | undefined;
  refetchWishlist: () => Promise<void>;
}

const WishlistContext = createContext<WishlistContextType | undefined>(undefined);

export function WishlistProvider({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([]);
  const [totalSavings, setTotalSavings] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchWishlist = useCallback(async () => {
    if (!user || !isAuthenticated) {
      setWishlistItems([]);
      setTotalSavings(0);
      return;
    }

    setIsLoading(true);
    try {
      const res = await wishlistService.getWishlist();
      const data = res.data?.data;
      if (data) {
        setWishlistItems(data.items || []);
        setTotalSavings(Number(data.total_savings || 0));
      } else {
        setWishlistItems([]);
        setTotalSavings(0);
      }
    } catch (err) {
      console.error("Failed to load user wishlist:", err);
    } finally {
      setIsLoading(false);
    }
  }, [user, isAuthenticated]);

  useEffect(() => {
    fetchWishlist();
  }, [fetchWishlist]);

  // Listen to custom wishlist:updated event across components
  useEffect(() => {
    const handleUpdate = () => {
      fetchWishlist();
    };
    window.addEventListener("wishlist:updated", handleUpdate);
    return () => {
      window.removeEventListener("wishlist:updated", handleUpdate);
    };
  }, [fetchWishlist]);

  const notifyChange = () => {
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("wishlist:updated"));
    }
  };

  const addToWishlist = async (
    productId: string,
    preferredMarketplace: string = "Amazon",
    targetPrice?: number,
    notes?: string
  ): Promise<boolean> => {
    if (!user || !isAuthenticated) {
      window.location.href = "/login";
      return false;
    }

    try {
      const res = await wishlistService.addToWishlist({
        product_id: productId,
        preferred_marketplace: preferredMarketplace,
        target_price: targetPrice,
        notes: notes,
      });

      if (res.data?.data) {
        const newItem = res.data.data;
        setWishlistItems((prev) => {
          const exists = prev.some((i) => i.product_id === productId || i.id === newItem.id);
          if (exists) {
            return prev.map((i) => (i.product_id === productId || i.id === newItem.id ? newItem : i));
          }
          return [newItem, ...prev];
        });
        notifyChange();
        return true;
      }
      return false;
    } catch (err) {
      console.error("Failed to add to wishlist:", err);
      return false;
    }
  };

  const removeFromWishlist = async (idOrProductId: string): Promise<boolean> => {
    if (!user || !isAuthenticated) return false;

    // Optimistic removal
    setWishlistItems((prev) =>
      prev.filter((i) => i.id !== idOrProductId && i.product_id !== idOrProductId)
    );

    try {
      await wishlistService.removeFromWishlist(idOrProductId);
      notifyChange();
      return true;
    } catch (err) {
      console.error("Failed to remove from wishlist:", err);
      // Re-fetch state on failure
      fetchWishlist();
      return false;
    }
  };

  const isInWishlist = (productId: string): boolean => {
    if (!productId) return false;
    return wishlistItems.some(
      (i) => i.product_id === productId || i.product?.id === productId || i.id === productId
    );
  };

  const getWishlistItem = (productId: string): WishlistItem | undefined => {
    return wishlistItems.find(
      (i) => i.product_id === productId || i.product?.id === productId || i.id === productId
    );
  };

  return (
    <WishlistContext.Provider
      value={{
        wishlistItems,
        wishlistCount: wishlistItems.length,
        totalSavings,
        isLoading,
        addToWishlist,
        removeFromWishlist,
        isInWishlist,
        getWishlistItem,
        refetchWishlist: fetchWishlist,
      }}
    >
      {children}
    </WishlistContext.Provider>
  );
}

export function useWishlist() {
  const context = useContext(WishlistContext);
  if (!context) {
    throw new Error("useWishlist must be used within a WishlistProvider");
  }
  return context;
}
