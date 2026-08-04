"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  ShoppingBag,
  Bell,
  Settings,
  LogOut,
  User,
  Lock,
  Save,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { AuthGuard } from "@/components/shared/AuthGuard";
import apiClient from "@/services/api";

const sidebarItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/dashboard", active: false },
  { icon: ShoppingBag, label: "My Products", href: "/products", active: false },
  { icon: Bell, label: "Price Alerts", href: "/dashboard#alerts", active: false },
  { icon: Settings, label: "Settings", href: "/dashboard/settings", active: true },
];

export default function SettingsPage() {
  const { user, logout, updateUser } = useAuth();

  const [profileName, setProfileName] = useState(user?.name || "");
  const [profileStatus, setProfileStatus] = useState<"idle" | "saving" | "success" | "error">(
    "idle"
  );
  const [profileError, setProfileError] = useState("");

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordStatus, setPasswordStatus] = useState<"idle" | "saving" | "success" | "error">(
    "idle"
  );
  const [passwordError, setPasswordError] = useState("");

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "??";

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profileName.trim()) {
      setProfileError("Name cannot be empty");
      return;
    }
    setProfileStatus("saving");
    setProfileError("");
    try {
      const res = await apiClient.patch("/users/me", { name: profileName.trim() });
      updateUser(res.data.data);
      setProfileStatus("success");
      setTimeout(() => setProfileStatus("idle"), 3000);
    } catch {
      setProfileStatus("error");
      setProfileError("Failed to update profile. Please try again.");
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError("All password fields are required");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match");
      return;
    }
    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters");
      return;
    }
    setPasswordStatus("saving");
    setPasswordError("");
    try {
      await apiClient.patch("/users/me", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordStatus("success");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => setPasswordStatus("idle"), 3000);
    } catch {
      setPasswordStatus("error");
      setPasswordError("Failed to change password. Check your current password and try again.");
    }
  };

  return (
    <AuthGuard>
      <div
        className="min-h-screen flex"
        style={{ background: "var(--background)", paddingTop: "64px" }}
      >
        {/* Sidebar */}
        <aside
          className="hidden lg:flex flex-col w-64 border-r h-[calc(100vh-64px)] sticky top-16"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="p-4 border-b" style={{ borderColor: "var(--border)" }}>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl gradient-bg flex items-center justify-center flex-shrink-0 text-white font-bold text-sm">
                {initials}
              </div>
              <div className="min-w-0">
                <p
                  className="text-sm font-semibold truncate"
                  style={{ color: "var(--foreground)" }}
                >
                  {user?.name || "User"}
                </p>
                <p className="text-xs truncate" style={{ color: "var(--foreground-muted)" }}>
                  {user?.email || ""}
                </p>
              </div>
            </div>
          </div>

          <div className="flex-1 p-4 space-y-1 mt-2">
            {sidebarItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                id={`sidebar-${item.label.toLowerCase().replace(/\s+/g, "-")}`}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  item.active ? "gradient-bg text-white" : "hover:text-indigo-400"
                }`}
                style={item.active ? {} : { color: "var(--foreground-muted)" }}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </div>

          <div className="p-4 border-t" style={{ borderColor: "var(--border)" }}>
            <button
              onClick={logout}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium w-full transition-colors hover:text-red-400"
              style={{ color: "var(--foreground-muted)" }}
              id="settings-logout"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-2xl mx-auto space-y-8">
            {/* Page Header */}
            <div>
              <motion.h1
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-3xl font-bold"
                style={{ color: "var(--foreground)" }}
              >
                Account{" "}
                <span className="gradient-text">Settings</span>
              </motion.h1>
              <p className="mt-1 text-sm" style={{ color: "var(--foreground-muted)" }}>
                Manage your profile and security preferences.
              </p>
            </div>

            {/* Profile Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border p-6"
              style={{ background: "var(--card)", borderColor: "var(--border)" }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-xl gradient-bg">
                  <User className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h2 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                    Profile Information
                  </h2>
                  <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                    Update your display name
                  </p>
                </div>
              </div>

              <form onSubmit={handleProfileSave} className="space-y-4">
                {/* Email (read-only) */}
                <div className="space-y-1.5">
                  <label
                    className="text-sm font-medium"
                    style={{ color: "var(--foreground-muted)" }}
                  >
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={user?.email || ""}
                    disabled
                    className="w-full px-4 py-3 rounded-xl text-sm opacity-50 cursor-not-allowed"
                    style={{
                      background: "var(--background)",
                      border: "1px solid var(--border)",
                      color: "var(--foreground)",
                    }}
                    id="settings-email"
                  />
                  <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                    Email cannot be changed
                  </p>
                </div>

                {/* Display Name */}
                <div className="space-y-1.5">
                  <label
                    className="text-sm font-medium"
                    style={{ color: "var(--foreground)" }}
                    htmlFor="settings-name"
                  >
                    Display Name
                  </label>
                  <input
                    id="settings-name"
                    type="text"
                    value={profileName}
                    onChange={(e) => setProfileName(e.target.value)}
                    placeholder="Your full name"
                    className="w-full px-4 py-3 rounded-xl text-sm focus:outline-none"
                    style={{
                      background: "var(--background)",
                      border: "1px solid var(--border)",
                      color: "var(--foreground)",
                    }}
                  />
                </div>

                {profileError && (
                  <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    {profileError}
                  </div>
                )}

                {profileStatus === "success" && (
                  <div className="flex items-center gap-2 text-sm text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                    Profile updated successfully
                  </div>
                )}

                <button
                  type="submit"
                  disabled={profileStatus === "saving"}
                  id="settings-save-profile"
                  className="flex items-center gap-2 px-6 py-3 rounded-xl gradient-bg text-white text-sm font-semibold transition-opacity disabled:opacity-60"
                >
                  <Save className="h-4 w-4" />
                  {profileStatus === "saving" ? "Saving..." : "Save Profile"}
                </button>
              </form>
            </motion.div>

            {/* Password Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="rounded-2xl border p-6"
              style={{ background: "var(--card)", borderColor: "var(--border)" }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-xl gradient-bg">
                  <Lock className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h2 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
                    Change Password
                  </h2>
                  <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                    Update your account password
                  </p>
                </div>
              </div>

              <form onSubmit={handlePasswordChange} className="space-y-4">
                <div className="space-y-1.5">
                  <label
                    className="text-sm font-medium"
                    style={{ color: "var(--foreground)" }}
                    htmlFor="settings-current-password"
                  >
                    Current Password
                  </label>
                  <input
                    id="settings-current-password"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Enter current password"
                    className="w-full px-4 py-3 rounded-xl text-sm focus:outline-none"
                    style={{
                      background: "var(--background)",
                      border: "1px solid var(--border)",
                      color: "var(--foreground)",
                    }}
                  />
                </div>

                <div className="space-y-1.5">
                  <label
                    className="text-sm font-medium"
                    style={{ color: "var(--foreground)" }}
                    htmlFor="settings-new-password"
                  >
                    New Password
                  </label>
                  <input
                    id="settings-new-password"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    className="w-full px-4 py-3 rounded-xl text-sm focus:outline-none"
                    style={{
                      background: "var(--background)",
                      border: "1px solid var(--border)",
                      color: "var(--foreground)",
                    }}
                  />
                </div>

                <div className="space-y-1.5">
                  <label
                    className="text-sm font-medium"
                    style={{ color: "var(--foreground)" }}
                    htmlFor="settings-confirm-password"
                  >
                    Confirm New Password
                  </label>
                  <input
                    id="settings-confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat new password"
                    className="w-full px-4 py-3 rounded-xl text-sm focus:outline-none"
                    style={{
                      background: "var(--background)",
                      border: "1px solid var(--border)",
                      color: "var(--foreground)",
                    }}
                  />
                </div>

                {passwordError && (
                  <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    {passwordError}
                  </div>
                )}

                {passwordStatus === "success" && (
                  <div className="flex items-center gap-2 text-sm text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                    Password changed successfully
                  </div>
                )}

                <button
                  type="submit"
                  disabled={passwordStatus === "saving"}
                  id="settings-change-password"
                  className="flex items-center gap-2 px-6 py-3 rounded-xl gradient-bg text-white text-sm font-semibold transition-opacity disabled:opacity-60"
                >
                  <Lock className="h-4 w-4" />
                  {passwordStatus === "saving" ? "Changing..." : "Change Password"}
                </button>
              </form>
            </motion.div>

            {/* Account Info Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="rounded-2xl border p-6"
              style={{ background: "var(--card)", borderColor: "var(--border)" }}
            >
              <h2 className="text-base font-semibold mb-4" style={{ color: "var(--foreground)" }}>
                Account Details
              </h2>
              <dl className="space-y-3">
                {[
                  { label: "Account ID", value: user?.id || "-" },
                  { label: "Role", value: user?.role || "user" },
                  {
                    label: "Status",
                    value: user?.is_active ? "Active" : "Inactive",
                  },
                  {
                    label: "Email Verified",
                    value: user?.is_verified ? "Yes" : "No",
                  },
                ].map(({ label, value }) => (
                  <div
                    key={label}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                    style={{ borderColor: "var(--border)" }}
                  >
                    <dt className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                      {label}
                    </dt>
                    <dd
                      className="text-sm font-medium font-mono truncate max-w-xs"
                      style={{ color: "var(--foreground)" }}
                    >
                      {value}
                    </dd>
                  </div>
                ))}
              </dl>
            </motion.div>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
