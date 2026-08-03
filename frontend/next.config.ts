import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable React strict mode for development best practices
  reactStrictMode: true,

  // Image optimization — add allowed domains in Phase 2
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.amazon.com",
      },
      {
        protocol: "https",
        hostname: "**.flipkart.com",
      },
    ],
  },

  // Output mode — standalone for Docker
  output: "standalone",

  // Disable x-powered-by header
  poweredByHeader: false,

  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-XSS-Protection", value: "1; mode=block" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
