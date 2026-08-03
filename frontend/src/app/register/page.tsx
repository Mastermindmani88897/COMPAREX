"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Eye, EyeOff, Mail, Lock, User, Zap, Check, ArrowRight, AlertCircle, Loader2 } from "lucide-react";
import type { RegisterFormData } from "@/types";
import { useAuth } from "@/context/AuthContext";

const passwordStrengthLevels = [
  { label: "Weak", color: "#ef4444" },
  { label: "Fair", color: "#f59e0b" },
  { label: "Good", color: "#10b981" },
  { label: "Strong", color: "#6366f1" },
];

function getPasswordStrength(password: string): number {
  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  return score;
}

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [formData, setFormData] = useState<RegisterFormData>({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const passwordStrength = getPasswordStrength(formData.password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    try {
      await register(formData.name, formData.email, formData.password, formData.confirmPassword);
      router.push("/dashboard");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string; message?: string } } };
      const msg =
        axiosErr?.response?.data?.detail ||
        axiosErr?.response?.data?.message ||
        "Registration failed. Please try again.";
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
      <div className="absolute inset-0 bg-grid opacity-30" />
      <div
        className="absolute inset-0"
        style={{
          background: "radial-gradient(ellipse 60% 40% at 50% 0%, rgba(139,92,246,0.12), transparent)",
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
          {/* Header */}
          <div className="flex flex-col items-center mb-8">
            <div className="flex items-center gap-2 mb-2">
              <div className="h-9 w-9 rounded-xl gradient-bg flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <span className="text-2xl font-bold gradient-text">COMPAREX</span>
            </div>
            <h1 className="text-xl font-semibold mt-2" style={{ color: "var(--foreground)" }}>
              Create your account
            </h1>
            <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
              Start saving money today — it&apos;s free
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

          <form onSubmit={handleSubmit} className="space-y-4" id="register-form">
            {/* Name */}
            <div>
              <label htmlFor="register-name" className="block text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
                Full name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                <input
                  id="register-name"
                  type="text"
                  autoComplete="name"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData((f) => ({ ...f, name: e.target.value }))}
                  placeholder="John Doe"
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-lg"
                  style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="register-email" className="block text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                <input
                  id="register-email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData((f) => ({ ...f, email: e.target.value }))}
                  placeholder="you@example.com"
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-lg"
                  style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="register-password" className="block text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                <input
                  id="register-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData((f) => ({ ...f, password: e.target.value }))}
                  placeholder="Min. 8 characters"
                  className="w-full pl-10 pr-10 py-2.5 text-sm rounded-lg"
                  style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--foreground-muted)" }}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {/* Strength Indicator */}
              {formData.password && (
                <div className="mt-2">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4].map((level) => (
                      <div
                        key={level}
                        className="flex-1 h-1 rounded-full transition-all duration-300"
                        style={{
                          background: level <= passwordStrength
                            ? passwordStrengthLevels[passwordStrength - 1]?.color || "#e4e4e7"
                            : "var(--border)",
                        }}
                      />
                    ))}
                  </div>
                  <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                    Strength:{" "}
                    <span style={{ color: passwordStrengthLevels[passwordStrength - 1]?.color }}>
                      {passwordStrengthLevels[passwordStrength - 1]?.label || "Too short"}
                    </span>
                  </p>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="register-confirm" className="block text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
                Confirm password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: "var(--foreground-muted)" }} />
                <input
                  id="register-confirm"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData((f) => ({ ...f, confirmPassword: e.target.value }))}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-2.5 text-sm rounded-lg"
                  style={{
                    background: "var(--background)",
                    border: `1px solid ${
                      formData.confirmPassword && formData.password !== formData.confirmPassword
                        ? "#ef4444"
                        : "var(--border)"
                    }`,
                    color: "var(--foreground)",
                  }}
                  disabled={isLoading}
                />
                {formData.confirmPassword && formData.password === formData.confirmPassword && (
                  <Check className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-green-400" />
                )}
              </div>
            </div>

            {/* Terms */}
            <div className="flex items-start gap-2">
              <input
                id="register-terms"
                type="checkbox"
                required
                checked={formData.agreeToTerms}
                onChange={(e) => setFormData((f) => ({ ...f, agreeToTerms: e.target.checked }))}
                className="h-4 w-4 mt-0.5 rounded flex-shrink-0"
                style={{ accentColor: "var(--brand-primary)" }}
              />
              <label htmlFor="register-terms" className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                I agree to the{" "}
                <Link href="/terms" className="text-indigo-400 hover:underline">Terms</Link>
                {" "}and{" "}
                <Link href="/privacy" className="text-indigo-400 hover:underline">Privacy Policy</Link>
              </label>
            </div>

            <motion.button
              whileHover={{ scale: isLoading ? 1 : 1.01 }}
              whileTap={{ scale: isLoading ? 1 : 0.99 }}
              type="submit"
              id="register-submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white gradient-bg text-sm disabled:opacity-70 disabled:cursor-not-allowed"
              style={{ boxShadow: "0 4px 15px rgba(99,102,241,0.3)" }}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Creating account…
                </>
              ) : (
                <>
                  Create account
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </motion.button>
          </form>

          <p className="text-center text-sm mt-6" style={{ color: "var(--foreground-muted)" }}>
            Already have an account?{" "}
            <Link href="/login" id="register-login-link" className="text-indigo-400 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
