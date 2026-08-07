import axios, { AxiosError, type AxiosInstance, type AxiosResponse } from "axios";
import type { TokenResponse, UserPublic } from "@/types";

const getBaseUrl = (): string => {
  let url = process.env.NEXT_PUBLIC_API_URL || "https://comparex-backend-33jp.onrender.com/api/v1";
  url = url.trim().replace(/\/+$/, "");
  if (!url.endsWith("/api/v1")) {
    if (url.endsWith("/api")) {
      url = `${url}/v1`;
    } else {
      url = `${url}/api/v1`;
    }
  }
  return url;
};

const API_BASE_URL = getBaseUrl();

const ACCESS_TOKEN_KEY = "comparex_access_token";
const REFRESH_TOKEN_KEY = "comparex_refresh_token";

export function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return (
    localStorage.getItem(ACCESS_TOKEN_KEY) ||
    sessionStorage.getItem(ACCESS_TOKEN_KEY)
  );
}

export function getStoredRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return (
    localStorage.getItem(REFRESH_TOKEN_KEY) ||
    sessionStorage.getItem(REFRESH_TOKEN_KEY)
  );
}

export function saveStoredTokens(
  access: string,
  refresh: string,
  rememberMe: boolean = true
): void {
  if (typeof window === "undefined") return;
  if (rememberMe) {
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  } else {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, access);
    sessionStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
  document.cookie = "comparex_auth=1; path=/; max-age=604800; SameSite=Lax";
}

export function clearStoredTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  document.cookie = "comparex_auth=; path=/; max-age=0; SameSite=Lax";
}

/**
 * Configured Axios instance for all API calls.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// ── Request interceptor — attach JWT from storage ─────────────────────────────
apiClient.interceptors.request.use(
  (config) => {
    const token = getStoredAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor — auto-refresh on 401 ────────────────────────────────
let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as typeof error.config & {
      _retry?: boolean;
      _retryCount?: number;
    };

    // Retry transient network or 502/503/504 server errors up to 2 times
    if (
      originalRequest &&
      (!error.response || [502, 503, 504].includes(error.response.status)) &&
      (originalRequest._retryCount || 0) < 2
    ) {
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;
      const backoffMs = originalRequest._retryCount * 1000;
      await new Promise((res) => setTimeout(res, backoffMs));
      return apiClient(originalRequest);
    }

    if (error.response?.status === 401 && !originalRequest?._retry) {
      if (typeof window === "undefined") return Promise.reject(error);

      const refreshToken = getStoredRefreshToken();
      if (!refreshToken) {
        clearStoredTokens();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((newToken) => {
            if (originalRequest) {
              originalRequest.headers = originalRequest.headers || {};
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            resolve(apiClient(originalRequest!));
          });
        });
      }

      isRefreshing = true;
      if (originalRequest) originalRequest._retry = true;

      try {
        const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token }: TokenResponse = res.data.data;
        const isLocalStorage = Boolean(localStorage.getItem(REFRESH_TOKEN_KEY));
        saveStoredTokens(access_token, refresh_token, isLocalStorage);

        onTokenRefreshed(access_token);
        if (originalRequest) {
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch {
        clearStoredTokens();
        if (
          typeof window !== "undefined" &&
          !window.location.pathname.startsWith("/login")
        ) {
          window.location.href = "/login";
        }
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// ── Auth Service ──────────────────────────────────────────────────────────────
export const authService = {
  register: (
    name: string,
    email: string,
    password: string,
    confirm_password: string
  ) =>
    apiClient.post<{ data: UserPublic; message: string; success: boolean }>(
      "/auth/register",
      {
        name,
        email,
        password,
        confirm_password,
      }
    ),

  login: (email: string, password: string) =>
    apiClient.post<{ data: TokenResponse; message: string; success: boolean }>(
      "/auth/login",
      {
        email,
        password,
      }
    ),

  logout: () =>
    apiClient.post<{ data: null; message: string; success: boolean }>(
      "/auth/logout"
    ),

  refresh: (refresh_token: string) =>
    apiClient.post<{ data: TokenResponse; message: string; success: boolean }>(
      "/auth/refresh",
      {
        refresh_token,
      }
    ),

  getMe: () =>
    apiClient.get<{ data: UserPublic; message: string; success: boolean }>(
      "/users/me"
    ),

  googleAuth: (payload: {
    id_token?: string;
    access_token?: string;
    google_id?: string;
    email?: string;
    name?: string;
    avatar_url?: string;
  }) =>
    apiClient.post<{ data: TokenResponse; message: string; success: boolean }>(
      "/auth/google",
      payload
    ),
};

export const healthCheck = () => apiClient.get("/health");

export const wishlistService = {
  getWishlist: (params?: { search?: string; category?: string; sort_by?: string }) =>
    apiClient.get("/wishlist", { params }),

  addToWishlist: (payload: { product_id: string; preferred_marketplace?: string; target_price?: number; notes?: string }) =>
    apiClient.post("/wishlist", payload),

  updateWishlistItem: (id: string, payload: { target_price?: number; preferred_marketplace?: string; notes?: string }) =>
    apiClient.patch(`/wishlist/${id}`, payload),

  removeFromWishlist: (idOrProductId: string) =>
    apiClient.delete(`/wishlist/${idOrProductId}`),
};

export const alertsService = {
  getAlerts: () => apiClient.get("/alerts"),

  createAlert: (payload: { product_id: string; target_price: number; marketplace?: string; notification_method?: string }) =>
    apiClient.post("/alerts", payload),

  updateAlert: (id: string, payload: { target_price?: number; marketplace?: string; notification_method?: string; is_active?: boolean }) =>
    apiClient.patch(`/alerts/${id}`, payload),

  deleteAlert: (id: string) => apiClient.delete(`/alerts/${id}`),
};

export const notificationService = {
  getNotifications: () => apiClient.get("/notifications"),

  markRead: (notificationId?: string, markAll: boolean = false) =>
    apiClient.patch("/notifications/read", { notification_id: notificationId, mark_all: markAll }),

  deleteNotification: (id: string) => apiClient.delete(`/notifications/${id}`),

  clearAll: () => apiClient.post("/notifications/clear-all"),
};

export const priceHistoryService = {
  getProductHistory: (productId: string, params?: { product_name?: string; base_price?: number; time_range?: string }) =>
    apiClient.get(`/price-history/product/${productId}`, { params }),
};
