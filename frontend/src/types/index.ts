// Global TypeScript types for COMPAREX

// ── API Response Envelopes ────────────────────────────────────────────────────
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

// ── Auth & User Types ─────────────────────────────────────────────────────────
/** Matches backend UserPublic schema */
export interface UserPublic {
  id: string;
  email: string;
  name: string;
  avatar_url?: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

/** Matches backend TokenResponse schema */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserPublic;
}

export interface AuthState {
  user: UserPublic | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// ── Category Types ────────────────────────────────────────────────────────────
export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  parent_id?: string | null;
  created_at: string;
  updated_at: string;
}

// ── Product Types ─────────────────────────────────────────────────────────────
/** Matches backend ProductPublic schema */
export interface Product {
  id: string;
  name: string;
  description?: string | null;
  category_id?: string | null;
  category?: string | null;
  brand?: string | null;
  image_url?: string | null;
  ean?: string | null;
  base_price?: number | null;
  created_at: string;
  updated_at: string;
}

// ── Marketplace Types ─────────────────────────────────────────────────────────
export interface Marketplace {
  id: string;
  name: string;
  slug: string;
  logo_url?: string | null;
  base_url: string;
  is_active: boolean;
  country_code: string;
}

// ── Price Listing Types ───────────────────────────────────────────────────────
export interface MarketplaceSummary {
  id: string;
  name: string;
  slug: string;
  logo_url?: string | null;
  base_url: string;
}

export interface ProductListing {
  id: string;
  product_id: string;
  marketplace_id: string;
  price: number;
  original_price?: number | null;
  currency: string;
  listing_url: string;
  seller_name?: string | null;
  is_available: boolean;
  is_prime: boolean;
  rating?: number | null;
  review_count?: number | null;
  marketplace?: MarketplaceSummary | null;
  created_at: string;
  updated_at: string;
}

export interface PriceCompareResult {
  product_id: string;
  product_name: string;
  listings: ProductListing[];
  lowest_price?: number | null;
  highest_price?: number | null;
  average_price?: number | null;
  best_listing_id?: string | null;
}

// ── Navigation & UI Types ─────────────────────────────────────────────────────
export interface NavItem {
  label: string;
  href: string;
  icon?: string;
  external?: boolean;
}

export interface FeatureCard {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
}

// ── Form Types ────────────────────────────────────────────────────────────────
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
