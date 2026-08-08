"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Zap, LogOut, LayoutDashboard, User, Heart } from "lucide-react";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { siteConfig } from "@/config/site";
import { useAuth } from "@/context/AuthContext";
import { useWishlist } from "@/context/WishlistContext";

import { getUserDisplayName, getUserFirstName, getUserInitials } from "@/utils/user";

import { NotificationBell } from "@/components/notifications/NotificationBell";

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const { wishlistCount } = useWishlist();

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsMobileOpen(false);
      setIsUserMenuOpen(false);
    }, 0);
    return () => clearTimeout(timeout);
  }, [pathname]);

  // Close user menu on outside click
  useEffect(() => {
    if (!isUserMenuOpen) return;
    const handleClick = () => setIsUserMenuOpen(false);
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, [isUserMenuOpen]);

  const isActive = (href: string) => pathname === href;

  const initials = getUserInitials(user);
  const displayName = getUserDisplayName(user);
  const firstName = getUserFirstName(user);

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

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-1">
              {siteConfig.nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  id={`nav-${item.label.toLowerCase()}`}
                  className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive(item.href)
                      ? "text-indigo-400 font-semibold"
                      : "hover:text-indigo-400"
                  }`}
                  style={{
                    color: isActive(item.href) ? undefined : "var(--foreground-muted)",
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </div>

            {/* Right Actions */}
            <div className="hidden md:flex items-center gap-3">
              <ThemeToggle />

              {isAuthenticated && user && (
                <>
                  <NotificationBell />
                  <Link
                    href="/dashboard/wishlist"
                    className="relative p-2 rounded-xl border hover:text-rose-400 hover:border-rose-400/30 transition-colors"
                    style={{ borderColor: "var(--border)", background: "var(--card)", color: "var(--foreground-muted)" }}
                    title="My Wishlist & Favorites"
                  >
                    <Heart className="h-4 w-4 text-rose-500 fill-rose-500/20" />
                    {wishlistCount > 0 && (
                      <span className="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-extrabold text-white animate-pulse">
                        {wishlistCount}
                      </span>
                    )}
                  </Link>
                </>
              )}

              {isLoading ? (
                <div className="h-8 w-8 rounded-lg bg-slate-800 animate-pulse" />
              ) : isAuthenticated && user ? (
                // Authenticated: User menu
                <div className="relative">
                  <button
                    id="nav-user-menu"
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsUserMenuOpen((v) => !v);
                    }}
                    className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl border transition-all duration-200 hover:border-indigo-500"
                    style={{ borderColor: "var(--border)", background: "var(--card)" }}
                  >
                    {user.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt={displayName}
                        className="h-7 w-7 rounded-lg object-cover flex-shrink-0"
                      />
                    ) : (
                      <div className="h-7 w-7 rounded-lg gradient-bg flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                        {initials}
                      </div>
                    )}
                    <span className="text-sm font-medium max-w-[120px] truncate" style={{ color: "var(--foreground)" }}>
                      {firstName}
                    </span>
                  </button>

                  <AnimatePresence>
                    {isUserMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 8, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 8, scale: 0.95 }}
                        transition={{ duration: 0.15 }}
                        className="absolute right-0 top-12 w-56 rounded-2xl border shadow-xl z-50 overflow-hidden"
                        style={{ background: "var(--card)", borderColor: "var(--border)" }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        {/* User Info */}
                        <div className="px-4 py-3 border-b flex items-center gap-3" style={{ borderColor: "var(--border)" }}>
                          {user.avatar_url ? (
                            <img
                              src={user.avatar_url}
                              alt={displayName}
                              className="h-9 w-9 rounded-xl object-cover flex-shrink-0"
                            />
                          ) : (
                            <div className="h-9 w-9 rounded-xl gradient-bg flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                              {initials}
                            </div>
                          )}
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-semibold truncate" style={{ color: "var(--foreground)" }}>
                              {displayName}
                            </p>
                            <p className="text-xs truncate mt-0.5" style={{ color: "var(--foreground-muted)" }}>
                              {user.email}
                            </p>
                          </div>
                        </div>

                        {/* Menu Items */}
                        <div className="p-2">
                          <Link
                            href="/dashboard"
                            id="nav-dashboard"
                            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors hover:text-indigo-400"
                            style={{ color: "var(--foreground-muted)" }}
                          >
                            <LayoutDashboard className="h-4 w-4" />
                            Dashboard
                          </Link>
                          <Link
                            href="/dashboard/settings"
                            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors hover:text-indigo-400"
                            style={{ color: "var(--foreground-muted)" }}
                          >
                            <User className="h-4 w-4" />
                            Profile
                          </Link>
                          <div className="h-px my-1" style={{ background: "var(--border)" }} />
                          <button
                            onClick={logout}
                            id="nav-logout"
                            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm w-full transition-colors hover:text-red-400"
                            style={{ color: "var(--foreground-muted)" }}
                          >
                            <LogOut className="h-4 w-4" />
                            Sign out
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                // Unauthenticated: Login + Register
                <>
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
                </>
              )}
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
                {isAuthenticated && user ? (
                  <>
                    <Link
                      href="/dashboard"
                      className="flex-1 text-center px-4 py-2.5 rounded-lg text-sm font-medium"
                      style={{ background: "var(--secondary)", color: "var(--foreground)" }}
                    >
                      Dashboard
                    </Link>
                    <button
                      onClick={logout}
                      className="flex-1 text-center px-4 py-2.5 rounded-lg text-sm font-semibold text-red-400"
                      style={{ background: "rgba(239,68,68,0.1)" }}
                    >
                      Sign out
                    </button>
                  </>
                ) : (
                  <>
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
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
