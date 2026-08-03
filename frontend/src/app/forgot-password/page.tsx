"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Mail, Zap, ArrowLeft, SendHorizonal } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Email send logic in Phase 2
    setSubmitted(true);
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4 py-24 relative overflow-hidden"
      style={{ background: "var(--background)" }}
    >
      <div className="absolute inset-0 bg-grid opacity-30" />
      <div
        className="absolute inset-0"
        style={{
          background: "radial-gradient(ellipse 60% 40% at 50% 0%, rgba(99,102,241,0.1), transparent)",
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative w-full max-w-md"
      >
        <div
          className="rounded-2xl p-8 border"
          style={{
            background: "var(--card)",
            borderColor: "var(--border)",
            boxShadow: "0 25px 50px -12px rgba(0,0,0,0.2)",
          }}
        >
          <div className="flex flex-col items-center mb-8">
            <div className="h-9 w-9 rounded-xl gradient-bg flex items-center justify-center mb-4">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-xl font-semibold" style={{ color: "var(--foreground)" }}>
              {submitted ? "Check your email" : "Reset your password"}
            </h1>
            <p className="text-sm mt-2 text-center" style={{ color: "var(--foreground-muted)" }}>
              {submitted
                ? `We sent a reset link to ${email}. Check your inbox.`
                : "Enter your email and we'll send you a reset link."}
            </p>
          </div>

          {!submitted ? (
            <form onSubmit={handleSubmit} className="space-y-5" id="forgot-password-form">
              <div>
                <label
                  htmlFor="forgot-email"
                  className="block text-sm font-medium mb-2"
                  style={{ color: "var(--foreground)" }}
                >
                  Email address
                </label>
                <div className="relative">
                  <Mail
                    className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                    style={{ color: "var(--foreground-muted)" }}
                  />
                  <input
                    id="forgot-email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full pl-10 pr-4 py-2.5 text-sm rounded-lg"
                    style={{
                      background: "var(--background)",
                      border: "1px solid var(--border)",
                      color: "var(--foreground)",
                    }}
                  />
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                type="submit"
                id="forgot-submit"
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white gradient-bg text-sm"
                style={{ boxShadow: "0 4px 15px rgba(99,102,241,0.3)" }}
              >
                Send reset link
                <SendHorizonal className="h-4 w-4" />
              </motion.button>
            </form>
          ) : (
            <div
              className="rounded-xl p-4 text-center"
              style={{ background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)" }}
            >
              <p className="text-sm font-medium text-green-400">
                Reset email sent successfully!
              </p>
            </div>
          )}

          <Link
            href="/login"
            id="forgot-back-link"
            className="flex items-center justify-center gap-2 mt-6 text-sm transition-colors hover:text-indigo-400"
            style={{ color: "var(--foreground-muted)" }}
          >
            <ArrowLeft className="h-4 w-4" />
            Back to sign in
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
