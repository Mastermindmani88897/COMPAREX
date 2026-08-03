import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "404 – Page Not Found",
  description: "The page you are looking for does not exist.",
};

export default function NotFound() {
  return (
    <div
      className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden"
      style={{ background: "var(--background)" }}
    >
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div
        className="absolute inset-0"
        style={{
          background: "radial-gradient(ellipse 60% 40% at 50% 50%, rgba(99,102,241,0.1), transparent)",
        }}
      />

      <div className="relative text-center max-w-lg">
        {/* Big 404 */}
        <div
          className="text-[180px] font-extrabold leading-none gradient-text select-none"
          style={{ opacity: 0.15 }}
        >
          404
        </div>
        <div className="mt-[-80px] relative">
          <h1 className="text-4xl font-extrabold tracking-tight mb-4" style={{ color: "var(--foreground)" }}>
            Page not found
          </h1>
          <p className="text-lg mb-8" style={{ color: "var(--foreground-muted)" }}>
            Oops! The page you&apos;re looking for doesn&apos;t exist or has been moved.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/"
              id="not-found-home"
              className="px-6 py-3 rounded-xl font-semibold text-white gradient-bg text-sm"
              style={{ boxShadow: "0 4px 15px rgba(99,102,241,0.3)" }}
            >
              Go home
            </Link>
            <Link
              href="/contact"
              id="not-found-contact"
              className="px-6 py-3 rounded-xl font-semibold text-sm border transition-colors hover:border-indigo-500"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              Contact support
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
