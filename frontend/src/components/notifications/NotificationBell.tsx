"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, Check, CheckCheck, Trash2, X, TrendingDown, Sparkles, ExternalLink } from "lucide-react";
import { notificationService } from "@/services/api";
import type { NotificationItem } from "@/types";

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchNotifications = async () => {
    try {
      const res = await notificationService.getNotifications();
      const data = res.data?.data;
      if (data) {
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch {
      // silently handle when user unauthenticated
    }
  };

  useEffect(() => {
    fetchNotifications();
    const timer = setInterval(fetchNotifications, 60000); // refresh every 60s
    return () => clearInterval(timer);
  }, []);

  const handleMarkRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await notificationService.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markRead(undefined, true);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await notificationService.deleteNotification(id);
      const target = notifications.find((n) => n.id === id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      if (target && !target.is_read) {
        setUnreadCount((prev) => Math.max(0, prev - 1));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleClearAll = async () => {
    try {
      await notificationService.clearAll();
      setNotifications([]);
      setUnreadCount(0);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="relative">
      <button
        id="notification-bell"
        onClick={() => {
          setIsOpen((prev) => !prev);
          if (!isOpen) fetchNotifications();
        }}
        className="relative p-2 rounded-xl border transition-all hover:border-indigo-500"
        style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
        title="Notifications"
      >
        <Bell className="h-4 w-4 text-amber-400" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow-md animate-pulse">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-12 w-80 sm:w-96 rounded-2xl border shadow-2xl z-50 overflow-hidden"
            style={{ background: "var(--card)", borderColor: "var(--border)" }}
          >
            {/* Header */}
            <div className="p-4 border-b flex items-center justify-between" style={{ borderColor: "var(--border)" }}>
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4 text-amber-400" />
                <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
                  Notifications
                </h3>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/20 text-amber-300">
                    {unreadCount} UNREAD
                  </span>
                )}
              </div>

              <div className="flex items-center gap-1.5 text-xs">
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    className="p-1 rounded hover:text-indigo-400 transition-colors"
                    title="Mark All Read"
                  >
                    <CheckCheck className="h-4 w-4" />
                  </button>
                )}
                {notifications.length > 0 && (
                  <button
                    onClick={handleClearAll}
                    className="p-1 rounded hover:text-rose-400 transition-colors"
                    title="Clear All"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 rounded hover:text-gray-400"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* List */}
            <div className="max-h-80 overflow-y-auto divide-y" style={{ borderColor: "var(--border)" }}>
              {notifications.length === 0 ? (
                <div className="p-8 text-center space-y-2">
                  <Sparkles className="h-8 w-8 text-indigo-400 mx-auto" />
                  <p className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>
                    No notifications yet
                  </p>
                  <p className="text-[11px]" style={{ color: "var(--foreground-muted)" }}>
                    We'll notify you when price drop alerts trigger!
                  </p>
                </div>
              ) : (
                notifications.map((n) => (
                  <div
                    key={n.id}
                    className={`p-3.5 flex items-start justify-between gap-3 transition-colors ${
                      !n.is_read ? "bg-amber-500/10" : "hover:bg-indigo-500/5"
                    }`}
                  >
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 shrink-0 mt-0.5">
                        <TrendingDown className="h-4 w-4" />
                      </div>

                      <div className="min-w-0 flex-1 space-y-1">
                        <p className="text-xs font-bold leading-tight truncate" style={{ color: "var(--foreground)" }}>
                          {n.title}
                        </p>
                        <p className="text-[11px] leading-relaxed line-clamp-2" style={{ color: "var(--foreground-muted)" }}>
                          {n.message}
                        </p>
                        {n.current_price && (
                          <div className="flex items-center gap-2 text-[11px]">
                            <span className="font-extrabold text-emerald-400">
                              ₹{Number(n.current_price).toLocaleString("en-IN")}
                            </span>
                            {n.marketplace && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold">
                                {n.marketplace}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1 shrink-0">
                      {!n.is_read && (
                        <button
                          onClick={(e) => handleMarkRead(n.id, e)}
                          className="p-1 text-emerald-400 hover:bg-emerald-500/20 rounded"
                          title="Mark Read"
                        >
                          <Check className="h-3.5 w-3.5" />
                        </button>
                      )}
                      <button
                        onClick={(e) => handleDelete(n.id, e)}
                        className="p-1 text-gray-400 hover:text-rose-400 rounded"
                        title="Delete"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className="p-2.5 border-t text-center" style={{ borderColor: "var(--border)" }}>
                <a
                  href="/dashboard#alerts"
                  onClick={() => setIsOpen(false)}
                  className="text-[11px] font-bold text-indigo-400 hover:underline inline-flex items-center gap-1"
                >
                  Manage All Price Alerts <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
