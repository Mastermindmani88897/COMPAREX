"use client";

import { motion, type Variants } from "framer-motion";
import Link from "next/link";
import {
  ArrowRight,
  ShoppingBag,
  Sparkles,
  TrendingDown,
  Zap,
  Star,
} from "lucide-react";

const floatingBadges = [
  { icon: TrendingDown, text: "42% cheaper", color: "#10b981", delay: 0 },
  { icon: Star, text: "4.9 ★ Rated", color: "#f59e0b", delay: 0.3 },
  { icon: ShoppingBag, text: "10M+ products", color: "#6366f1", delay: 0.6 },
];

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12, delayChildren: 0.2 },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" as const } },
};

export function HeroSection() {
  return (
    <section
      className="relative min-h-screen flex items-center overflow-hidden pt-16"
      id="hero"
    >
      {/* Background */}
      <div className="absolute inset-0 bg-grid opacity-50" />
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99,102,241,0.15), transparent)",
        }}
      />

      {/* Floating orbs */}
      <motion.div
        className="absolute top-1/4 left-1/4 h-72 w-72 rounded-full opacity-20 blur-3xl"
        style={{ background: "var(--brand-primary)" }}
        animate={{ scale: [1, 1.2, 1], opacity: [0.15, 0.25, 0.15] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full opacity-15 blur-3xl"
        style={{ background: "var(--brand-secondary)" }}
        animate={{ scale: [1.2, 1, 1.2], opacity: [0.1, 0.2, 0.1] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left – Copy */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="flex flex-col gap-6"
          >
            {/* Badge */}
            <motion.div variants={itemVariants}>
              <span
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold border"
                style={{
                  borderColor: "rgba(99,102,241,0.3)",
                  background: "rgba(99,102,241,0.1)",
                  color: "var(--brand-primary)",
                }}
              >
                <Zap className="h-3 w-3" />
                AI-Powered Shopping Intelligence
              </span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              variants={itemVariants}
              className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-tight"
              style={{ color: "var(--foreground)" }}
            >
              Shop Smarter.
              <br />
              <span className="gradient-text">Pay Less.</span>
              <br />
              Always.
            </motion.h1>

            {/* Description */}
            <motion.p
              variants={itemVariants}
              className="text-lg sm:text-xl leading-relaxed max-w-xl"
              style={{ color: "var(--foreground-muted)" }}
            >
              COMPAREX uses advanced AI to compare products across 10+ marketplaces,
              track price history, and surface the best deals — personalized to your
              needs, in real time.
            </motion.p>

            {/* CTAs */}
            <motion.div variants={itemVariants} className="flex flex-wrap gap-4">
              <Link
                href="/register"
                id="hero-cta-primary"
                className="group inline-flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white gradient-bg transition-all duration-300 hover:shadow-xl hover:scale-105"
                style={{ boxShadow: "0 4px 20px rgba(99,102,241,0.35)" }}
              >
                Get Started Free
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                href="/about"
                id="hero-cta-secondary"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-semibold border transition-all duration-300 hover:border-indigo-500"
                style={{
                  borderColor: "var(--border)",
                  color: "var(--foreground)",
                }}
              >
                <Sparkles className="h-4 w-4 text-indigo-400" />
                Learn More
              </Link>
            </motion.div>

            {/* Social Proof */}
            <motion.div
              variants={itemVariants}
              className="flex items-center gap-4 pt-2"
            >
              <div className="flex -space-x-2">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="h-8 w-8 rounded-full border-2 gradient-bg flex items-center justify-center text-white text-xs font-bold"
                    style={{ borderColor: "var(--background)", zIndex: 5 - i }}
                  >
                    {String.fromCharCode(65 + i)}
                  </div>
                ))}
              </div>
              <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                <span className="font-semibold" style={{ color: "var(--foreground)" }}>
                  50,000+
                </span>{" "}
                shoppers already saving money
              </p>
            </motion.div>
          </motion.div>

          {/* Right – Visual */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8, x: 40 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
            className="relative flex justify-center lg:justify-end"
          >
            {/* Main card */}
            <div className="relative animate-float">
              <div
                className="glass rounded-3xl p-8 w-80 sm:w-96"
                style={{
                  boxShadow:
                    "0 25px 50px -12px rgba(0,0,0,0.3), 0 0 60px rgba(99,102,241,0.15)",
                }}
              >
                {/* Mock UI content */}
                <div className="flex items-center gap-3 mb-6">
                  <div className="h-10 w-10 rounded-xl gradient-bg flex items-center justify-center">
                    <ShoppingBag className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <div
                      className="text-sm font-semibold"
                      style={{ color: "var(--foreground)" }}
                    >
                      Sony WH-1000XM5
                    </div>
                    <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                      Headphones • Electronics
                    </div>
                  </div>
                </div>

                {/* Price comparisons */}
                {[
                  { market: "Amazon", price: "₹28,990", badge: "Best Price", badgeColor: "#10b981" },
                  { market: "Flipkart", price: "₹31,499", badge: null, badgeColor: null },
                  { market: "Croma", price: "₹33,000", badge: null, badgeColor: null },
                ].map((item, i) => (
                  <motion.div
                    key={item.market}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 + i * 0.15 }}
                    className="flex items-center justify-between py-2.5 border-b last:border-0"
                    style={{ borderColor: "var(--border)" }}
                  >
                    <span className="text-sm font-medium" style={{ color: "var(--foreground)" }}>
                      {item.market}
                    </span>
                    <div className="flex items-center gap-2">
                      <span
                        className="text-sm font-bold"
                        style={{ color: i === 0 ? "#10b981" : "var(--foreground)" }}
                      >
                        {item.price}
                      </span>
                      {item.badge && (
                        <span
                          className="text-xs px-2 py-0.5 rounded-full font-semibold"
                          style={{ background: "rgba(16,185,129,0.15)", color: item.badgeColor! }}
                        >
                          {item.badge}
                        </span>
                      )}
                    </div>
                  </motion.div>
                ))}

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.4 }}
                  className="mt-5 p-3 rounded-xl text-center"
                  style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.2)" }}
                >
                  <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                    You save
                  </p>
                  <p className="text-2xl font-bold gradient-text">₹4,010</p>
                  <p className="text-xs text-green-400">vs. highest price</p>
                </motion.div>
              </div>

              {/* Floating badges */}
              {floatingBadges.map((badge, i) => {
                const positions = [
                  { top: "-16px", right: "-24px" },
                  { bottom: "80px", left: "-32px" },
                  { bottom: "-16px", right: "32px" },
                ];
                return (
                  <motion.div
                    key={badge.text}
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1.2 + badge.delay, type: "spring" }}
                    className="absolute glass rounded-xl px-3 py-2 flex items-center gap-2"
                    style={{ ...positions[i], boxShadow: "0 4px 20px rgba(0,0,0,0.2)" }}
                  >
                    <badge.icon className="h-4 w-4" style={{ color: badge.color }} />
                    <span
                      className="text-xs font-semibold whitespace-nowrap"
                      style={{ color: "var(--foreground)" }}
                    >
                      {badge.text}
                    </span>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
