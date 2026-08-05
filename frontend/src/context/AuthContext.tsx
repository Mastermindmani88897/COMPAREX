"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import apiClient, {
  clearStoredTokens,
  getStoredAccessToken,
  getStoredRefreshToken,
  saveStoredTokens,
} from "@/services/api";
import type { AuthState, TokenResponse, UserPublic } from "@/types";

interface AuthContextType extends AuthState {
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  googleLogin: (payload: {
    id_token?: string;
    access_token?: string;
    google_id?: string;
    email?: string;
    name?: string;
    avatar_url?: string;
  }) => Promise<void>;
  register: (
    name: string,
    email: string,
    password: string,
    confirmPassword: string
  ) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (user: UserPublic) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });
  const isRefreshing = useRef(false);

  useEffect(() => {
    let isMounted = true;

    async function hydrate() {
      const token = getStoredAccessToken();
      if (!token) {
        if (isMounted) {
          setState({ user: null, isAuthenticated: false, isLoading: false });
        }
        return;
      }
      try {
        const res = await apiClient.get("/users/me");
        const user: UserPublic = res.data.data;
        if (isMounted) {
          setState({ user, isAuthenticated: true, isLoading: false });
        }
      } catch {
        const refreshToken = getStoredRefreshToken();
        if (!refreshToken || isRefreshing.current) {
          clearStoredTokens();
          if (isMounted) {
            setState({ user: null, isAuthenticated: false, isLoading: false });
          }
          return;
        }
        try {
          isRefreshing.current = true;
          const res = await apiClient.post("/auth/refresh", {
            refresh_token: refreshToken,
          });
          const tokenData: TokenResponse = res.data.data;
          const isLocalStorage = Boolean(localStorage.getItem("comparex_refresh_token"));
          saveStoredTokens(tokenData.access_token, tokenData.refresh_token, isLocalStorage);
          if (isMounted) {
            setState({
              user: tokenData.user,
              isAuthenticated: true,
              isLoading: false,
            });
          }
        } catch {
          clearStoredTokens();
          if (isMounted) {
            setState({ user: null, isAuthenticated: false, isLoading: false });
          }
        } finally {
          isRefreshing.current = false;
        }
      }
    }

    hydrate();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = useCallback(
    async (email: string, password: string, rememberMe: boolean = true): Promise<void> => {
      const res = await apiClient.post("/auth/login", { email, password });
      const tokenData: TokenResponse = res.data.data;
      saveStoredTokens(tokenData.access_token, tokenData.refresh_token, rememberMe);
      setState({ user: tokenData.user, isAuthenticated: true, isLoading: false });
    },
    []
  );

  const googleLogin = useCallback(
    async (payload: {
      id_token?: string;
      access_token?: string;
      google_id?: string;
      email?: string;
      name?: string;
      avatar_url?: string;
    }): Promise<void> => {
      const res = await apiClient.post("/auth/google", payload);
      const tokenData: TokenResponse = res.data.data;
      saveStoredTokens(tokenData.access_token, tokenData.refresh_token, true);
      setState({ user: tokenData.user, isAuthenticated: true, isLoading: false });
    },
    []
  );

  const register = useCallback(
    async (
      name: string,
      email: string,
      password: string,
      confirmPassword: string
    ): Promise<void> => {
      await apiClient.post("/auth/register", {
        name,
        email,
        password,
        confirm_password: confirmPassword,
      });
      await login(email, password, true);
    },
    [login]
  );

  const logout = useCallback(async (): Promise<void> => {
    try {
      const token = getStoredAccessToken();
      if (token) {
        await apiClient.post("/auth/logout");
      }
    } catch {
      // Ignore logout errors
    } finally {
      clearStoredTokens();
      setState({ user: null, isAuthenticated: false, isLoading: false });
      router.push("/login");
    }
  }, [router]);

  const updateUser = useCallback((user: UserPublic): void => {
    setState((prev) => ({ ...prev, user }));
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, googleLogin, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
