"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Eye, EyeOff, Mail, Lock, Zap, ArrowRight, AlertCircle, Loader2 } from "lucide-react";
import type { LoginFormData } from "@/types";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [formData, setFormData] = useState<LoginFormData>({
    email: "",
    password: "",
    rememberMe: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(formData.email, formData.password, formData.rememberMe);
      router.push("/dashboard");
    } catch (err: unknown) {
      let msg = "Invalid email or password. Please try again.";
      if (typeof err === "object" && err !== null && "response" in err) {
        const res = (err as { response?: { data?: { detail?: unknown; message?: string } } }).response;
        if (res?.data) {
          const detail = res.data.detail;
          if (typeof detail === "string") {
            msg = detail;
          } else if (Array.isArray(detail)) {
            msg = detail
              .map((item: { msg?: string; loc?: string[] }) => item.msg || JSON.stringify(item))
              .join("; ");
          } else if (res.data.message) {
            msg = res.data.message;
          }
        }
      } else if (err instanceof Error) {
        msg = err.message;
      }
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4 py-24 relative overflow-hidden"
      style={{ background: "var(--background)" }}
    >
      {/* Background */}
      <div className="absolute inset-0 bg-grid opacity-30" />
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 60% 40% at 50% 0%, rgba(99,102,241,0.12), transparent)",
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative w-full max-w-md"
      >
        {/* Card */}
        <div
          className="rounded-2xl p-8 border"
          style={{
            background: "var(--card)",
            borderColor: "var(--border)",
            boxShadow: "0 25px 50px -12px rgba(0,0,0,0.2)",
          }}
        >
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <div className="flex items-center gap-2 mb-2">
              <div className="h-9 w-9 rounded-xl gradient-bg flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <span className="text-2xl font-bold gradient-text">COMPAREX</span>
            </div>
            <h1 className="text-xl font-semibold mt-2" style={{ color: "var(--foreground)" }}>
              Welcome back
            </h1>
            <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
              Sign in to your account
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-start gap-3 rounded-xl px-4 py-3 mb-5 text-sm"
              style={{
                background: "rgba(239,68,68,0.1)",
                border: "1px solid rgba(239,68,68,0.3)",
                color: "#f87171",
              }}
            >
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5" id="login-form">
            {/* Email */}
            <div>
              <label
                htmlFor="login-email"
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
                  id="login-email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData((f) => ({ ...f, email: e.target.value }))}
                  placeholder="you@example.com"
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-lg"
                  style={{
                    background: "var(--background)",
                    border: "1px solid var(--border)",
                    color: "var(--foreground)",
                  }}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="login-password"
                  className="block text-sm font-medium"
                  style={{ color: "var(--foreground)" }}
                >
                  Password
                </label>
                <Link
                  href="/forgot-password"
                  id="login-forgot-link"
                  className="text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Lock
                  className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4"
                  style={{ color: "var(--foreground-muted)" }}
                />
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData((f) => ({ ...f, password: e.target.value }))}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-2.5 text-sm rounded-lg"
                  style={{
                    background: "var(--background)",
                    border: "1px solid var(--border)",
                    color: "var(--foreground)",
                  }}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--foreground-muted)" }}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Remember me */}
            <div className="flex items-center gap-2">
              <input
                id="login-remember"
                type="checkbox"
                checked={formData.rememberMe}
                onChange={(e) => setFormData((f) => ({ ...f, rememberMe: e.target.checked }))}
                className="h-4 w-4 rounded"
                style={{ accentColor: "var(--brand-primary)" }}
              />
              <label
                htmlFor="login-remember"
                className="text-sm"
                style={{ color: "var(--foreground-muted)" }}
              >
                Remember me for 30 days
              </label>
            </div>

            {/* Submit */}
            <motion.button
              whileHover={{ scale: isLoading ? 1 : 1.01 }}
              whileTap={{ scale: isLoading ? 1 : 0.99 }}
              type="submit"
              id="login-submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white gradient-bg text-sm disabled:opacity-70 disabled:cursor-not-allowed"
              style={{ boxShadow: "0 4px 15px rgba(99,102,241,0.3)" }}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Signing in…
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </motion.button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
            <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>
              New to COMPAREX?
            </span>
            <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
          </div>

          <Link
            href="/register"
            id="login-register-link"
            className="block text-center py-2.5 rounded-xl text-sm font-medium border transition-colors hover:border-indigo-500"
            style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            Create an account
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
