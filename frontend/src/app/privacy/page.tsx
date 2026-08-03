import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Read COMPAREX's Privacy Policy to understand how we collect, use, and protect your personal data.",
};

const sections = [
  {
    title: "1. Information We Collect",
    content: `We collect information you provide directly to us (such as name, email address, and account details), information collected automatically when you use our platform (such as usage data, device information, and IP addresses), and information from third-party services when you connect them to COMPAREX.`,
  },
  {
    title: "2. How We Use Your Information",
    content: `We use your information to provide, maintain, and improve our services; send transactional and promotional communications; personalize your experience; analyze usage patterns to improve the platform; and comply with legal obligations.`,
  },
  {
    title: "3. Information Sharing",
    content: `We do not sell, trade, or rent your personal information to third parties. We may share anonymized, aggregated data for research or analytics. We may disclose information when required by law or to protect the rights and safety of users.`,
  },
  {
    title: "4. Data Retention",
    content: `We retain your personal data for as long as your account is active or as needed to provide services. You may request deletion of your account and associated data at any time by contacting us at support@comparex.io.`,
  },
  {
    title: "5. Security",
    content: `We implement industry-standard security measures including encryption in transit (TLS), encryption at rest, access controls, and regular security audits. No method of transmission is 100% secure; we cannot guarantee absolute security.`,
  },
  {
    title: "6. Cookies",
    content: `We use cookies and similar tracking technologies to enhance your experience. You can control cookie settings through your browser. Essential cookies are required for the platform to function correctly.`,
  },
  {
    title: "7. Your Rights",
    content: `Depending on your jurisdiction, you may have rights to access, correct, or delete your personal data; object to or restrict processing; and data portability. To exercise these rights, contact us at support@comparex.io.`,
  },
  {
    title: "8. Changes to This Policy",
    content: `We may update this Privacy Policy periodically. We will notify you of material changes via email or a prominent notice on our platform. Continued use of COMPAREX after changes constitutes acceptance of the updated policy.`,
  },
  {
    title: "9. Contact Us",
    content: `If you have any questions about this Privacy Policy, please contact us at support@comparex.io or write to COMPAREX, Bengaluru, India.`,
  },
];

export default function PrivacyPage() {
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
            Privacy Policy
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
            COMPAREX (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;) is committed to protecting your privacy. This policy describes
            how we collect, use, and share information when you use our platform and services.
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
