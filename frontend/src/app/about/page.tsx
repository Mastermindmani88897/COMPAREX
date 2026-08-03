import type { Metadata } from "next";
import { Target, Users, Zap, TrendingUp } from "lucide-react";

export const metadata: Metadata = {
  title: "About",
  description: "Learn about COMPAREX — our mission, vision, and the team building the future of AI-powered shopping.",
};

const stats = [
  { label: "Products Indexed", value: "10M+", icon: TrendingUp },
  { label: "Active Users", value: "50K+", icon: Users },
  { label: "Marketplaces", value: "12+", icon: Target },
  { label: "Avg. Savings", value: "28%", icon: Zap },
];

const team = [
  { name: "Aarav Sharma", role: "CEO & Co-founder", initials: "AS" },
  { name: "Priya Nair", role: "CTO & Co-founder", initials: "PN" },
  { name: "Rohan Mehta", role: "Lead AI Engineer", initials: "RM" },
  { name: "Sneha Joshi", role: "Head of Product", initials: "SJ" },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen pt-24 pb-16" style={{ background: "var(--background)" }}>
      {/* Hero */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-30" />
        <div
          className="absolute inset-0"
          style={{
            background: "radial-gradient(ellipse 60% 40% at 50% 0%, rgba(99,102,241,0.1), transparent)",
          }}
        />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <span
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold border mb-6"
            style={{ borderColor: "rgba(99,102,241,0.3)", background: "rgba(99,102,241,0.1)", color: "var(--brand-primary)" }}
          >
            Our Story
          </span>
          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-6" style={{ color: "var(--foreground)" }}>
            Building the Future of{" "}
            <span className="gradient-text">Smart Shopping</span>
          </h1>
          <p className="text-xl leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            COMPAREX was born from a simple frustration: why should shoppers spend hours comparing prices
            across different websites? We&apos;re using AI to solve this — once and for all.
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl p-6 text-center border"
              style={{ background: "var(--card)", borderColor: "var(--border)" }}
            >
              <div className="inline-flex items-center justify-center h-10 w-10 rounded-xl gradient-bg mb-3">
                <stat.icon className="h-5 w-5 text-white" />
              </div>
              <div className="text-3xl font-extrabold gradient-text mb-1">{stat.value}</div>
              <div className="text-sm" style={{ color: "var(--foreground-muted)" }}>{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Mission */}
      <section className="py-16 max-w-4xl mx-auto px-4 sm:px-6">
        <div
          className="rounded-2xl p-8 sm:p-12 border"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <h2 className="text-3xl font-bold mb-4" style={{ color: "var(--foreground)" }}>
            Our Mission
          </h2>
          <p className="text-lg leading-relaxed mb-6" style={{ color: "var(--foreground-muted)" }}>
            We believe every shopper deserves to make informed decisions without wasting time or money.
            COMPAREX aggregates real-time pricing data, applies AI-driven analysis, and delivers
            personalized insights that save you both.
          </p>
          <p className="text-lg leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            Our platform is built on transparency, fairness, and the conviction that technology
            should work for the consumer — not the retailer.
          </p>
        </div>
      </section>

      {/* Team */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center mb-12" style={{ color: "var(--foreground)" }}>
          Meet the Team
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {team.map((member) => (
            <div
              key={member.name}
              className="rounded-2xl p-6 text-center border transition-transform hover:-translate-y-1"
              style={{ background: "var(--card)", borderColor: "var(--border)" }}
            >
              <div className="h-16 w-16 rounded-2xl gradient-bg flex items-center justify-center text-white text-lg font-bold mx-auto mb-4">
                {member.initials}
              </div>
              <h3 className="font-semibold" style={{ color: "var(--foreground)" }}>{member.name}</h3>
              <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>{member.role}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
