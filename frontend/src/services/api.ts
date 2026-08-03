import axios, { AxiosError, type AxiosInstance, type AxiosResponse } from "axios";
import type { TokenResponse, UserPublic } from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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
    };

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
};

export const healthCheck = () => apiClient.get("/health");
