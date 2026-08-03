"use client";

export function LoadingSkeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-shimmer rounded-lg ${className}`}
      style={{ background: "var(--background-secondary)", minHeight: "1rem" }}
      aria-label="Loading..."
    />
  );
}

export function CardSkeleton() {
  return (
    <div
      className="rounded-xl p-6 space-y-4"
      style={{ background: "var(--card)", border: "1px solid var(--border)" }}
    >
      <LoadingSkeleton className="h-10 w-10 rounded-lg" />
      <LoadingSkeleton className="h-5 w-3/4" />
      <LoadingSkeleton className="h-4 w-full" />
      <LoadingSkeleton className="h-4 w-5/6" />
    </div>
  );
}

export function PageSkeleton() {
  return (
    <div className="min-h-screen p-8 space-y-6">
      <LoadingSkeleton className="h-12 w-64 mx-auto" />
      <LoadingSkeleton className="h-6 w-96 mx-auto" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
    </div>
  );
}
