import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms & Conditions",
  description: "Read COMPAREX's Terms and Conditions to understand your rights and responsibilities when using our platform.",
};

const sections = [
  {
    title: "1. Acceptance of Terms",
    content: `By accessing or using COMPAREX, you agree to be bound by these Terms and Conditions and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using this platform.`,
  },
  {
    title: "2. Use of Service",
    content: `COMPAREX provides a platform for comparing product prices across marketplaces. You agree to use the service only for lawful purposes and in a way that does not infringe the rights of others. You must not misuse our platform by scraping, reverse engineering, or attempting to gain unauthorized access.`,
  },
  {
    title: "3. User Accounts",
    content: `You are responsible for maintaining the confidentiality of your account credentials. You must notify us immediately of any unauthorized use of your account. COMPAREX is not liable for any losses arising from unauthorized account access that is not our fault.`,
  },
  {
    title: "4. Intellectual Property",
    content: `The COMPAREX platform, including its design, logo, software, and content, is the intellectual property of COMPAREX and is protected by applicable copyright and trademark laws. You may not reproduce, distribute, or create derivative works without express written permission.`,
  },
  {
    title: "5. Disclaimer of Warranties",
    content: `COMPAREX is provided "as is" without any warranties, express or implied. We do not guarantee the accuracy, completeness, or availability of price data. Prices displayed are sourced from third parties and may not reflect actual current prices at time of purchase.`,
  },
  {
    title: "6. Limitation of Liability",
    content: `COMPAREX shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the platform. Our total liability for any claim shall not exceed the amount paid by you to COMPAREX in the 12 months preceding the claim.`,
  },
  {
    title: "7. Third-Party Links",
    content: `Our platform may contain links to third-party websites and marketplaces. These links are provided for convenience only. COMPAREX has no control over the content of those sites and accepts no responsibility for them.`,
  },
  {
    title: "8. Termination",
    content: `We reserve the right to suspend or terminate your account at any time for violation of these Terms. You may terminate your account at any time by contacting us. Upon termination, your right to use the platform ceases immediately.`,
  },
  {
    title: "9. Governing Law",
    content: `These Terms shall be governed by the laws of India. Any disputes arising under these Terms shall be subject to the exclusive jurisdiction of the courts of Bengaluru, Karnataka, India.`,
  },
  {
    title: "10. Changes to Terms",
    content: `COMPAREX reserves the right to update these Terms at any time. We will notify you of material changes via email. Continued use of the platform after changes constitutes acceptance of the updated Terms.`,
  },
];

export default function TermsPage() {
  return (
    <div className="min-h-screen pt-24 pb-16" style={{ background: "var(--background)" }}>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
        {/* Header */}
        <div className="mb-12">
          <span
            className="inline-block px-3 py-1 rounded-full text-xs font-semibold mb-4 border"
            style={{ borderColor: "rgba(99,102,241,0.3)", background: "rgba(99,102,241,0.1)", color: "var(--brand-primary)" }}
          >
            Legal
          </span>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4" style={{ color: "var(--foreground)" }}>
            Terms & Conditions
          </h1>
          <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
            Last updated: August 2026
          </p>
        </div>

        {/* Intro */}
        <div
          className="rounded-xl p-6 mb-10 border"
          style={{ background: "rgba(99,102,241,0.06)", borderColor: "rgba(99,102,241,0.2)" }}
        >
          <p className="text-sm leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            Please read these Terms and Conditions carefully before using the COMPAREX platform.
            By using COMPAREX, you agree to these terms.
          </p>
        </div>

        {/* Sections */}
        <div className="space-y-8">
          {sections.map((section) => (
            <div key={section.title}>
              <h2 className="text-lg font-semibold mb-3" style={{ color: "var(--foreground)" }}>
                {section.title}
              </h2>
              <p className="text-sm leading-7" style={{ color: "var(--foreground-muted)" }}>
                {section.content}
              </p>
              <div className="mt-6 h-px" style={{ background: "var(--border)" }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
