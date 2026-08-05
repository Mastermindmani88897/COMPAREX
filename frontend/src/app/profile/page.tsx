"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { UserCheck, Shield, Save, User, Mail, Globe, Check } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { getUserDisplayName, getUserInitials } from "@/utils/user";
import apiClient from "@/services/api";

export default function ShoppingProfilePage() {
  const { user, updateUser } = useAuth();
  const [optIn, setOptIn] = useState(true);
  const [brands, setBrands] = useState("Apple, Samsung, Sony, Bose");
  const [marketplaces, setMarketplaces] = useState("Amazon India, Flipkart, Croma");
  const [minBudget, setMinBudget] = useState(5000);
  const [maxBudget, setMaxBudget] = useState(150000);
  const [savedStatus, setSavedStatus] = useState(false);

  // Profile Edit State
  const displayName = getUserDisplayName(user);
  const initials = getUserInitials(user);
  const [nameInput, setNameInput] = useState(displayName);
  const [isUpdatingName, setIsUpdatingName] = useState(false);
  const [nameSavedSuccess, setNameSavedSuccess] = useState(false);

  const handleSave = () => {
    setSavedStatus(true);
    setTimeout(() => setSavedStatus(false), 2500);
  };

  const handleSaveName = async () => {
    if (!nameInput.trim() || !user) return;
    setIsUpdatingName(true);
    try {
      // Update local context user state
      const updatedUser = { ...user, name: nameInput.trim() };
      updateUser(updatedUser);
      setNameSavedSuccess(true);
      setTimeout(() => setNameSavedSuccess(false), 2500);
    } catch {
      // Ignore update error
    } finally {
      setIsUpdatingName(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12 pt-24">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <UserCheck className="w-3.5 h-3.5" />
            COMPAREX User & Shopping Profile
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
            User Account & Preferences
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            Manage your personal profile and customize your AI deal shopping preferences.
          </p>
        </div>

        {/* User Identity Card */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6"
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 pb-6 border-b border-slate-800">
            <div className="flex items-center gap-4">
              {user?.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={displayName}
                  className="w-16 h-16 rounded-2xl object-cover border-2 border-indigo-500/40"
                />
              ) : (
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-lg">
                  {initials}
                </div>
              )}
              <div className="space-y-1">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  {displayName}
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 font-medium">
                    {user?.login_provider === "google" ? "Google OAuth" : "Email & Password"}
                  </span>
                </h2>
                <p className="text-sm text-slate-400 flex items-center gap-2">
                  <Mail className="w-4 h-4 text-slate-500" />
                  {user?.email || "No email"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950/60 px-4 py-2 rounded-xl border border-slate-800">
              <Globe className="w-4 h-4 text-emerald-400" />
              <span>Status: <strong className="text-emerald-400">Active Member</strong></span>
            </div>
          </div>

          {/* Edit Profile Name */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div className="md:col-span-2 space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <User className="w-4 h-4 text-indigo-400" />
                Full Name / Display Name
              </label>
              <input
                type="text"
                value={nameInput}
                onChange={(e) => setNameInput(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                placeholder="Enter your full name"
              />
            </div>
            <button
              onClick={handleSaveName}
              disabled={isUpdatingName}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-all flex items-center justify-center gap-2"
            >
              {nameSavedSuccess ? (
                <>
                  <Check className="w-4 h-4 text-emerald-300" />
                  Updated!
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Update Name
                </>
              )}
            </button>
          </div>
        </motion.div>

        {/* Opt-in Consent Card */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/30 flex items-center justify-between gap-4"
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-semibold text-lg text-white">
              <Shield className="w-5 h-5 text-indigo-400" />
              Explicit AI Learning Consent
            </div>
            <p className="text-xs md:text-sm text-slate-400">
              When enabled, COMPAREX tailors deal scores and product matches to your preferences.
            </p>
          </div>

          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={optIn}
              onChange={(e) => setOptIn(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-14 h-7 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-indigo-600"></div>
          </label>
        </motion.div>

        {/* Form Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Preferred Brands
            </label>
            <input
              type="text"
              value={brands}
              onChange={(e) => setBrands(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Preferred Marketplaces
            </label>
            <input
              type="text"
              value={marketplaces}
              onChange={(e) => setMarketplaces(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Min Budget (₹)
            </label>
            <input
              type="number"
              value={minBudget}
              onChange={(e) => setMinBudget(Number(e.target.value))}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Max Budget (₹)
            </label>
            <input
              type="number"
              value={maxBudget}
              onChange={(e) => setMaxBudget(Number(e.target.value))}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-4 pt-4 border-t border-slate-800">
          <button
            onClick={handleSave}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-sm shadow-lg shadow-indigo-500/20 hover:opacity-90 transition-all flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {savedStatus ? "Preferences Saved!" : "Save Preferences"}
          </button>
        </div>
      </div>
    </div>
  );
}
