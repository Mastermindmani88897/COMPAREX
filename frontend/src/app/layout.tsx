import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/hooks/useTheme";
import { AuthProvider } from "@/context/AuthContext";
import { WishlistProvider } from "@/context/WishlistContext";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { siteConfig } from "@/config/site";

export const metadata: Metadata = {
  title: {
    default: `${siteConfig.name} – ${siteConfig.tagline}`,
    template: `%s | ${siteConfig.name}`,
  },
  description: siteConfig.description,
  keywords: [
    "price comparison",
    "AI shopping",
    "best deals",
    "product comparison",
    "shopping assistant",
    "price alerts",
    "COMPAREX",
  ],
  authors: [{ name: "COMPAREX Team" }],
  creator: "COMPAREX",
  metadataBase: new URL(siteConfig.url),
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteConfig.url,
    title: siteConfig.name,
    description: siteConfig.description,
    siteName: siteConfig.name,
  },
  twitter: {
    card: "summary_large_image",
    title: siteConfig.name,
    description: siteConfig.description,
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="page-wrapper font-sans antialiased">
        <ThemeProvider>
          <AuthProvider>
            <WishlistProvider>
              <Navbar />
              <main className="content-wrapper">{children}</main>
              <Footer />
            </WishlistProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
