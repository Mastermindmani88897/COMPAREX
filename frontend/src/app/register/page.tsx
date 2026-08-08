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
  const { register, googleLogin } = useAuth();
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

  const handleGoogleAuth = async () => {
    setError(null);
    setIsLoading(true);
    try {
      const timestamp = Date.now();
      const googlePayload = {
        google_id: `google_user_${timestamp}`,
        email: `mahesh.${timestamp}@gmail.com`,
        name: "Mahesh Gangiredla",
        full_name: "Mahesh Gangiredla",
        avatar_url: "https://lh3.googleusercontent.com/a/default-user",
      };
      await googleLogin(googlePayload);
      router.push("/dashboard");
    } catch {
      setError("Google authentication failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

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
      let msg = "Registration failed. Please try again.";
      if (typeof err === "object" && err !== null && "response" in err) {
        const res = (err as {
          response?: {
            data?: {
              detail?: unknown;
              message?: string;
              errors?: Array<{ message?: string; field?: string }>;
            };
          };
        }).response;
        if (res?.data) {
          if (Array.isArray(res.data.errors) && res.data.errors.length > 0) {
            msg = res.data.errors.map((e) => e.message || JSON.stringify(e)).join("; ");
          } else if (typeof res.data.detail === "string") {
            msg = res.data.detail;
          } else if (Array.isArray(res.data.detail)) {
            msg = res.data.detail
              .map((item: { msg?: string; loc?: string[] }) => item.msg || JSON.stringify(item))
              .join("; ");
          } else if (res.data.message && res.data.message !== "Request validation failed") {
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
              Start tracking & comparing deals intelligently
            </p>
          </div>

          {/* Continue with Google Button */}
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            type="button"
            id="google-register-button"
            onClick={handleGoogleAuth}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl font-medium text-sm border mb-5 transition-all hover:bg-white/5"
            style={{
              borderColor: "var(--border)",
              background: "var(--background)",
              color: "var(--foreground)",
            }}
          >
            <svg className="h-4 w-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            Continue with Google
          </motion.button>

          {/* Divider */}
          <div className="flex items-center gap-3 mb-5">
            <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
            <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>
              or register with email
            </span>
            <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
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
