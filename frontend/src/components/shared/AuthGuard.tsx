"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Loader2, Zap } from "lucide-react";

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * AuthGuard — client-side fallback for route protection.
 * Shows a loading screen while checking auth state,
 * then redirects to /login if not authenticated.
 * The middleware handles server-side protection; this is the client-side layer.
 */
export function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-4"
        style={{ background: "var(--background)" }}
      >
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-xl gradient-bg flex items-center justify-center">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-2xl font-bold gradient-text">COMPAREX</span>
        </div>
        <Loader2 className="h-6 w-6 animate-spin" style={{ color: "var(--foreground-muted)" }} />
        <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
          Loading your dashboard…
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect via useEffect
  }

  return <>{children}</>;
}
