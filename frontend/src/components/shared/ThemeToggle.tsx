"use client";

import { useTheme } from "@/hooks/useTheme";
import { Sun, Moon } from "lucide-react";
import { motion } from "framer-motion";

export function ThemeToggle() {
  const { resolvedTheme, toggleTheme } = useTheme();

  return (
    <motion.button
      onClick={toggleTheme}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="relative inline-flex h-9 w-9 items-center justify-center rounded-lg border transition-colors"
      style={{
        borderColor: "var(--border)",
        background: "var(--card)",
        color: "var(--foreground-muted)",
      }}
      aria-label="Toggle theme"
      id="theme-toggle"
    >
      <motion.span
        key={resolvedTheme}
        initial={{ opacity: 0, rotate: -90, scale: 0.5 }}
        animate={{ opacity: 1, rotate: 0, scale: 1 }}
        exit={{ opacity: 0, rotate: 90, scale: 0.5 }}
        transition={{ duration: 0.2 }}
      >
        {resolvedTheme === "dark" ? (
          <Sun className="h-4 w-4" />
        ) : (
          <Moon className="h-4 w-4" />
        )}
      </motion.span>
    </motion.button>
  );
}
