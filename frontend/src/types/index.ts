// Global TypeScript types for COMPAREX

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  status: number;
  details?: Record<string, unknown>;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
  message: string;
  success: boolean;
}

// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Product types (placeholder for Phase 2+)
export interface Product {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  category: string;
  createdAt: string;
}

export interface Marketplace {
  id: string;
  name: string;
  logoUrl: string;
  baseUrl: string;
  isActive: boolean;
}

// Navigation types
export interface NavItem {
  label: string;
  href: string;
  icon?: string;
  external?: boolean;
}

// Feature card types
export interface FeatureCard {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
}

// Form types
export interface LoginFormData {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

export interface ForgotPasswordFormData {
  email: string;
}

export interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
}
