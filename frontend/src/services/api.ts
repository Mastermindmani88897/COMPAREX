import axios, { AxiosError, type AxiosInstance, type AxiosResponse } from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Configured Axios instance for all API calls.
 * Includes request/response interceptors for auth token injection
 * and standardized error handling.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Request interceptor — attach JWT from localStorage
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("comparex_access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — normalize errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear storage (auth logic in Phase 2)
      if (typeof window !== "undefined") {
        localStorage.removeItem("comparex_access_token");
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

/**
 * Health check — verify backend is reachable.
 */
export const healthCheck = () => apiClient.get("/health");
