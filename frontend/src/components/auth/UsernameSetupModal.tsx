"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, Check, AlertCircle, Loader2, Sparkles } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export function UsernameSetupModal() {
  const { user, setupUsername } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [usernameInput, setUsernameInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      const isLegacy = Boolean(
        user.username &&
          user.username.toLowerCase().startsWith("user1") &&
          user.username.length > 10
      );
      if (user.needs_username_setup || !user.username || isLegacy) {
        setIsOpen(true);
        const initial = (user.name && user.name.toLowerCase() !== "user" ? user.name : user.email.split("@")[0]) || "";
        setUsernameInput(initial);
      } else {
        setIsOpen(false);
      }
    } else {
      setIsOpen(false);
    }
  }, [user]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const clean = usernameInput.trim();
    if (clean.length < 3 || clean.length > 30) {
      setError("Username must be between 3 and 30 characters.");
      return;
    }

    if (!/^[A-Za-z0-9_ -]+$/.test(clean)) {
      setError("Username can only contain letters, numbers, spaces, underscores, or hyphens.");
      return;
    }

    setIsLoading(true);
    try {
      await setupUsername(clean);
      setIsOpen(false);
    } catch (err: unknown) {
      let msg = "Failed to update username. Please try again.";
      if (typeof err === "object" && err !== null && "response" in err) {
        const res = (err as { response?: { data?: { detail?: string; message?: string } } }).response;
        if (res?.data?.detail) {
          msg = res.data.detail;
        } else if (res?.data?.message) {
          msg = res.data.message;
        }
      }
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="relative w-full max-w-md rounded-2xl p-6 sm:p-8 border shadow-2xl overflow-hidden"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="flex items-center gap-2 mb-2 text-indigo-400">
            <Sparkles className="h-5 w-5 animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-wider">Welcome to COMPAREX</span>
          </div>

          <h2 className="text-2xl font-bold mb-1" style={{ color: "var(--foreground)" }}>
            Choose your username
          </h2>
          <p className="text-xs mb-6" style={{ color: "var(--foreground-muted)" }}>
            Personalize your display name across deal comparisons, wishlist, and price tracking.
          </p>

          {error && (
            <div
              className="flex items-start gap-2 rounded-xl p-3 mb-4 text-xs font-medium border"
              style={{
                background: "rgba(239,68,68,0.1)",
                borderColor: "rgba(239,68,68,0.3)",
                color: "#f87171",
              }}
            >
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username-input" className="block text-xs font-medium mb-1.5" style={{ color: "var(--foreground)" }}>
                Username / Display Name
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                <input
                  id="username-input"
                  type="text"
                  required
                  value={usernameInput}
                  onChange={(e) => setUsernameInput(e.target.value)}
                  placeholder="e.g. Mahesh"
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border font-medium focus:ring-2 focus:ring-indigo-500 outline-none"
                  style={{ background: "var(--background)", borderColor: "var(--border)", color: "var(--foreground)" }}
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="rounded-xl p-3 border space-y-1 text-[11px]" style={{ background: "rgba(255,255,255,0.02)", borderColor: "var(--border)", color: "var(--foreground-muted)" }}>
              <p className="font-semibold text-xs mb-1" style={{ color: "var(--foreground)" }}>Username requirements:</p>
              <p className="flex items-center gap-1"><Check className="h-3 w-3 text-green-400" /> 3–30 characters long</p>
              <p className="flex items-center gap-1"><Check className="h-3 w-3 text-green-400" /> Letters, numbers, spaces, underscores, or hyphens</p>
              <p className="flex items-center gap-1"><Check className="h-3 w-3 text-green-400" /> Case-insensitive unique handle</p>
            </div>

            <button
              type="submit"
              disabled={isLoading || !usernameInput.trim()}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm gradient-bg text-white shadow-lg transition-all disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving username…
                </>
              ) : (
                "Continue"
              )}
            </button>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
