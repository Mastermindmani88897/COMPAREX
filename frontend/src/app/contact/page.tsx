"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Mail, MessageSquare, MapPin, SendHorizonal, CheckCircle } from "lucide-react";
import type { ContactFormData } from "@/types";

const contactInfo = [
  { icon: Mail, label: "Email", value: "support@comparex.io", href: "mailto:support@comparex.io" },
  { icon: MessageSquare, label: "Live Chat", value: "Available 9AM – 6PM IST", href: "#" },
  { icon: MapPin, label: "Office", value: "Bengaluru, India", href: "#" },
];

export default function ContactPage() {
  const [formData, setFormData] = useState<ContactFormData>({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Form submission logic in Phase 2
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen pt-24 pb-16" style={{ background: "var(--background)" }}>
      {/* Header */}
      <section className="relative py-16 overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-30" />
        <div
          className="absolute inset-0"
          style={{ background: "radial-gradient(ellipse 60% 40% at 50% 0%, rgba(99,102,241,0.1), transparent)" }}
        />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-4" style={{ color: "var(--foreground)" }}>
            Get in <span className="gradient-text">Touch</span>
          </h1>
          <p className="text-xl" style={{ color: "var(--foreground-muted)" }}>
            Have a question or feedback? We&apos;d love to hear from you.
          </p>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Contact Info */}
          <div className="space-y-6">
            {contactInfo.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="flex items-start gap-4 p-5 rounded-xl border transition-all duration-200 hover:border-indigo-500 block"
                style={{ background: "var(--card)", borderColor: "var(--border)" }}
              >
                <div className="h-10 w-10 rounded-lg gradient-bg flex items-center justify-center flex-shrink-0">
                  <item.icon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--foreground-muted)" }}>
                    {item.label}
                  </p>
                  <p className="text-sm font-medium" style={{ color: "var(--foreground)" }}>
                    {item.value}
                  </p>
                </div>
              </a>
            ))}
          </div>

          {/* Form */}
          <div className="lg:col-span-2">
            <div
              className="rounded-2xl p-8 border"
              style={{ background: "var(--card)", borderColor: "var(--border)" }}
            >
              {submitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-12"
                >
                  <CheckCircle className="h-16 w-16 text-green-400 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold mb-2" style={{ color: "var(--foreground)" }}>
                    Message sent!
                  </h2>
                  <p style={{ color: "var(--foreground-muted)" }}>
                    We&apos;ll get back to you within 24 hours.
                  </p>
                </motion.div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-5" id="contact-form">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label htmlFor="contact-name" className="block text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
                        Your name
                      </label>
                      <input
                        id="contact-name"
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => setFormData((f) => ({ ...f, name: e.target.value }))}
                        placeholder="John Doe"
                        className="w-full px-4 py-2.5 text-sm rounded-lg"
                        style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                      />
                    </div>
                    <div>
                      <label htmlFor="contact-email" className="block text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
                        Email address
                      </label>
                      <input
                        id="contact-email"
                        type="email"
                        required
                        value={formData.email}
                        onChange={(e) => setFormData((f) => ({ ...f, email: e.target.value }))}
                        placeholder="you@example.com"
                        className="w-full px-4 py-2.5 text-sm rounded-lg"
                        style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="contact-subject" className="block text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
                      Subject
                    </label>
                    <input
                      id="contact-subject"
                      type="text"
                      required
                      value={formData.subject}
                      onChange={(e) => setFormData((f) => ({ ...f, subject: e.target.value }))}
                      placeholder="How can we help?"
                      className="w-full px-4 py-2.5 text-sm rounded-lg"
                      style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                    />
                  </div>
                  <div>
                    <label htmlFor="contact-message" className="block text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
                      Message
                    </label>
                    <textarea
                      id="contact-message"
                      required
                      rows={5}
                      value={formData.message}
                      onChange={(e) => setFormData((f) => ({ ...f, message: e.target.value }))}
                      placeholder="Tell us more about your question or feedback..."
                      className="w-full px-4 py-2.5 text-sm rounded-lg resize-none"
                      style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                    />
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    type="submit"
                    id="contact-submit"
                    className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white gradient-bg text-sm"
                    style={{ boxShadow: "0 4px 15px rgba(99,102,241,0.3)" }}
                  >
                    Send message
                    <SendHorizonal className="h-4 w-4" />
                  </motion.button>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
