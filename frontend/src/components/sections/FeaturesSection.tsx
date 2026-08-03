"use client";

import { motion, type Variants } from "framer-motion";
import {
  BarChart3,
  Bot,
  Camera,
  Bell,
  Sparkles,
  Globe2,
} from "lucide-react";
import { siteConfig } from "@/config/site";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  BarChart3,
  Bot,
  Camera,
  Bell,
  Sparkles,
  Globe2,
};

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" as const } },
};

export function FeaturesSection() {
  return (
    <section
      id="features"
      className="py-24 lg:py-32 relative overflow-hidden"
    >
      {/* Background */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 60% 40% at 50% 100%, rgba(139,92,246,0.08), transparent)",
        }}
      />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold border mb-4"
            style={{
              borderColor: "rgba(139,92,246,0.3)",
              background: "rgba(139,92,246,0.1)",
              color: "#8b5cf6",
            }}
          >
            <Sparkles className="h-3 w-3" />
            Everything you need
          </span>
          <h2
            className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4"
            style={{ color: "var(--foreground)" }}
          >
            Powerful features for{" "}
            <span className="gradient-text">smarter shopping</span>
          </h2>
          <p
            className="text-lg max-w-2xl mx-auto"
            style={{ color: "var(--foreground-muted)" }}
          >
            From AI-powered comparisons to real-time price alerts, COMPAREX gives you
            every tool you need to always get the best deal.
          </p>
        </motion.div>

        {/* Feature Cards Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {siteConfig.features.map((feature) => {
            const Icon = iconMap[feature.icon] || Sparkles;
            return (
              <motion.div
                key={feature.id}
                variants={cardVariants}
                whileHover={{ y: -6, scale: 1.01 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
                id={`feature-${feature.id}`}
                className="group relative rounded-2xl p-6 border cursor-default overflow-hidden"
                style={{
                  background: "var(--card)",
                  borderColor: "var(--border)",
                  boxShadow: "var(--shadow)",
                }}
              >
                {/* Hover glow */}
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{
                    background: `radial-gradient(circle at 30% 30%, ${feature.color.split(" ")[1]}15, transparent 70%)`,
                  }}
                />

                {/* Icon */}
                <div className="relative">
                  <div
                    className={`inline-flex items-center justify-center h-12 w-12 rounded-xl bg-gradient-to-br ${feature.color} mb-4`}
                    style={{ boxShadow: "0 4px 15px rgba(0,0,0,0.2)" }}
                  >
                    <Icon className="h-6 w-6 text-white" />
                  </div>

                  <h3
                    className="text-lg font-semibold mb-2"
                    style={{ color: "var(--foreground)" }}
                  >
                    {feature.title}
                  </h3>
                  <p className="text-sm leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                    {feature.description}
                  </p>

                  {/* Coming soon tag */}
                  <span
                    className="inline-block mt-4 text-xs font-medium px-2.5 py-1 rounded-full border"
                    style={{
                      borderColor: "var(--border)",
                      color: "var(--foreground-muted)",
                    }}
                  >
                    Coming in Phase 2
                  </span>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
