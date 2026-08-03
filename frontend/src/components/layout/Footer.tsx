"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Zap, Heart } from "lucide-react";
import { siteConfig } from "@/config/site";

const footerLinks = {
  Product: [
    { label: "Features", href: "/#features" },
    { label: "About", href: "/about" },
    { label: "Contact", href: "/contact" },
  ],
  Legal: [
    { label: "Privacy Policy", href: "/privacy" },
    { label: "Terms & Conditions", href: "/terms" },
  ],
  Account: [
    { label: "Login", href: "/login" },
    { label: "Register", href: "/register" },
  ],
};

const socialLinks = [
  { href: siteConfig.links.github, label: "GitHub", text: "GH" },
  { href: siteConfig.links.twitter, label: "X (Twitter)", text: "X" },
  { href: siteConfig.links.linkedin, label: "LinkedIn", text: "in" },
];

export function Footer() {
  return (
    <footer
      className="border-t"
      style={{ borderColor: "var(--border)", background: "var(--background-secondary)" }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-12">
          {/* Brand */}
          <div className="md:col-span-2">
            <Link href="/" className="flex items-center gap-2 group mb-4" id="footer-logo">
              <div className="flex items-center justify-center h-8 w-8 rounded-lg gradient-bg">
                <Zap className="h-4 w-4 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">COMPAREX</span>
            </Link>
            <p className="text-sm leading-relaxed mb-6" style={{ color: "var(--foreground-muted)" }}>
              {siteConfig.description}
            </p>
            <div className="flex items-center gap-3">
              {socialLinks.map(({ href, label, text }) => (
                <motion.a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  id={`footer-social-${label.toLowerCase().replace(/[^a-z0-9]/g, "-")}`}
                  whileHover={{ scale: 1.1, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center justify-center h-9 w-9 rounded-lg border transition-colors hover:border-indigo-500 text-xs font-bold"
                  style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}
                >
                  {text}
                </motion.a>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([group, links]) => (
            <div key={group}>
              <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>
                {group}
              </h3>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      id={`footer-${link.label.toLowerCase().replace(/\s+/g, "-")}`}
                      className="text-sm transition-colors hover:text-indigo-400"
                      style={{ color: "var(--foreground-muted)" }}
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div
          className="mt-12 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 border-t"
          style={{ borderColor: "var(--border)" }}
        >
          <p className="text-sm flex items-center gap-1.5" style={{ color: "var(--foreground-muted)" }}>
            &copy; {new Date().getFullYear()} COMPAREX. Made with{" "}
            <Heart className="h-3.5 w-3.5 text-red-400 fill-red-400" /> All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <Link
              href="/privacy"
              className="text-xs transition-colors hover:text-indigo-400"
              style={{ color: "var(--foreground-muted)" }}
            >
              Privacy
            </Link>
            <Link
              href="/terms"
              className="text-xs transition-colors hover:text-indigo-400"
              style={{ color: "var(--foreground-muted)" }}
            >
              Terms
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
