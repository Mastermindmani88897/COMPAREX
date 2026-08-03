"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Zap } from "lucide-react";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { siteConfig } from "@/config/site";

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    // Close mobile menu whenever route changes — use a ref to avoid setState-in-effect lint
    const timeout = setTimeout(() => setIsMobileOpen(false), 0);
    return () => clearTimeout(timeout);
  }, [pathname]);

  const isActive = (href: string) => pathname === href;

  return (
    <>
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled ? "glass shadow-lg" : "bg-transparent"
        }`}
        style={{ borderBottom: isScrolled ? "1px solid var(--border)" : "none" }}
      >
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group" id="nav-logo">
              <div
                className="flex items-center justify-center h-8 w-8 rounded-lg gradient-bg"
                style={{ boxShadow: "0 0 20px rgba(99,102,241,0.4)" }}
              >
                <Zap className="h-4 w-4 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text tracking-tight">
                COMPAREX
              </span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-1">
              {siteConfig.nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  id={`nav-${item.label.toLowerCase()}`}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive(item.href)
                      ? "gradient-text font-semibold"
                      : "hover:text-indigo-400"
                  }`}
                  style={{ color: isActive(item.href) ? undefined : "var(--foreground-muted)" }}
                >
                  {item.label}
                </Link>
              ))}
            </div>

            {/* Desktop Actions */}
            <div className="hidden md:flex items-center gap-3">
              <ThemeToggle />
              <Link
                href="/login"
                id="nav-login"
                className="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 hover:opacity-80"
                style={{ color: "var(--foreground-muted)", background: "var(--secondary)" }}
              >
                Login
              </Link>
              <Link
                href="/register"
                id="nav-register"
                className="px-4 py-2 text-sm font-semibold rounded-lg gradient-bg text-white transition-all duration-200 hover:opacity-90 hover:shadow-lg"
                style={{ boxShadow: "0 4px 15px rgba(99,102,241,0.3)" }}
              >
                Register
              </Link>
            </div>

            {/* Mobile Actions */}
            <div className="flex md:hidden items-center gap-2">
              <ThemeToggle />
              <button
                onClick={() => setIsMobileOpen((v) => !v)}
                className="p-2 rounded-lg transition-colors"
                style={{ color: "var(--foreground)" }}
                aria-label="Toggle mobile menu"
                id="nav-mobile-toggle"
              >
                {isMobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </nav>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="fixed top-16 left-0 right-0 z-40 glass border-b md:hidden"
            style={{ borderColor: "var(--border)" }}
            id="nav-mobile-menu"
          >
            <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col gap-2">
              {siteConfig.nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    isActive(item.href) ? "gradient-text" : ""
                  }`}
                  style={{ color: isActive(item.href) ? undefined : "var(--foreground-muted)" }}
                >
                  {item.label}
                </Link>
              ))}
              <div className="flex gap-3 pt-2 border-t" style={{ borderColor: "var(--border)" }}>
                <Link
                  href="/login"
                  className="flex-1 text-center px-4 py-2.5 rounded-lg text-sm font-medium"
                  style={{ background: "var(--secondary)", color: "var(--foreground)" }}
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="flex-1 text-center px-4 py-2.5 rounded-lg text-sm font-semibold gradient-bg text-white"
                >
                  Register
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
