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
  google_id?: string | null;
  login_provider?: string;
  avatar_url?: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at?: string | null;
  updated_at?: string | null;
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

// ── Brand & Specification Types ───────────────────────────────────────────────
export interface Brand {
  id: string;
  name: string;
  slug: string;
  logo_url?: string | null;
  website_url?: string | null;
}

export interface ProductSpecification {
  id?: string;
  key: string;
  value: string;
  group?: string | null;
  unit?: string | null;
}

export interface ProductImage {
  id?: string;
  url: string;
  alt_text?: string | null;
  is_primary?: boolean;
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
  brand_id?: string | null;
  brand?: string | null;
  image_url?: string | null;
  ean?: string | null;
  base_price?: number | null;
  specifications?: ProductSpecification[];
  images?: ProductImage[];
  created_at: string;
  updated_at: string;
}

// ── Marketplace & Connector Types (Phase 4) ──────────────────────────────────
export interface ExtensionStatusResponse {
  status: string;
  environment: string;
  api_version: string;
  min_supported_extension_version: string;
  active_connectors_count: number;
  supported_marketplaces: string[];
}

// ── AI Intelligence Platform Types (Phase 6) ─────────────────────────────────
export interface ProductRecommendationItem {
  product_name: string;
  price: number;
  marketplace_name: string;
  deal_score: number;
  reasons: string[];
  is_best_value?: boolean;
}

export interface AIChatResponse {
  response_text: string;
  detected_intent: string;
  recommended_category?: string | null;
  recommendations: ProductRecommendationItem[];
  reasoning_summary: string;
}

export interface AIMatchResponse {
  is_match: boolean;
  confidence_score: number;
  matched_attributes: string[];
  discrepancies: string[];
  reasoning: string;
}

export interface AIImageSearchResponse {
  detected_product_type: string;
  extracted_features: string[];
  confidence_score: number;
  suggested_search_query: string;
  aggregated_results?: AggregatedSearchResponse | null;
}

export interface AIReviewSummaryResponse {
  product_name: string;
  pros: string[];
  cons: string[];
  summary: string;
  buying_verdict: string;
  review_confidence_score: number;
}

export interface AIDealAnalysisResponse {
  product_name: string;
  deal_score: number;
  decision: "BUY_NOW" | "GREAT_DEAL" | "FAIR_PRICE" | "PREMIUM_CHOICE" | "WAIT_FOR_PRICE_DROP";
  decision_label: string;
  score_breakdown: Record<string, number>;
  detailed_explanation: string;
  alternatives_suggested: Array<{
    product_name: string;
    price: number;
    marketplace_name: string;
    reason: string;
  }>;
}

export interface AISpecComparisonResponse {
  product_a_name: string;
  product_b_name: string;
  key_differences: Array<{
    attribute: string;
    product_a: string;
    product_b: string;
    insight: string;
  }>;
  verdict: string;
  winner_name?: string | null;
}

export interface Marketplace {
  id: string;
  name: string;
  slug: string;
  logo_url?: string | null;
  base_url: string;
  is_active: boolean;
  country_code: string;
}

export interface ConnectorMetadata {
  name: string;
  slug: string;
  base_url: string;
  supported_categories: string[];
  is_enabled: boolean;
  priority: number;
  supports_search: boolean;
  supports_details: boolean;
  supports_price_lookup: boolean;
  logo_url?: string | null;
}

export interface AggregatedListing {
  id?: string;
  title: string;
  price: number;
  original_price?: number | null;
  discount_percent?: number | null;
  currency: string;
  seller_name?: string | null;
  listing_url: string;
  marketplace_slug: string;
  marketplace_name: string;
  marketplace_logo?: string | null;
  marketplace_base_url?: string | null;
  is_available: boolean;
  is_prime: boolean;
  stock_status: string;
  delivery_estimate?: string | null;
  rating?: number | null;
  review_count?: number | null;
  deal_score?: number | null;
  badges?: string[];
}

export interface AggregatedSearchResponse {
  query: string;
  category?: string | null;
  total_listings: number;
  marketplaces_queried: string[];
  lowest_price?: number | null;
  highest_price?: number | null;
  average_price?: number | null;
  price_spread?: number | null;
  max_savings?: number | null;
  best_deal_listing_id?: string | null;
  listings: AggregatedListing[];
  from_cache: boolean;
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
  discount_percent?: number | null;
  currency: string;
  listing_url: string;
  marketplace_product_id?: string | null;
  seller_name?: string | null;
  is_available: boolean;
  is_prime: boolean;
  stock_status?: string | null;
  delivery_estimate?: string | null;
  rating?: number | null;
  review_count?: number | null;
  marketplace?: MarketplaceSummary | null;
  badges?: string[];
  created_at: string;
  updated_at: string;
}

export interface PriceCompareResult {
  product_id: string;
  product_name: string;
  listings: ProductListing[];
  total_listings?: number;
  lowest_price?: number | null;
  highest_price?: number | null;
  average_price?: number | null;
  price_spread?: number | null;
  max_savings?: number | null;
  best_listing_id?: string | null;
}

export interface PriceHistoryPoint {
  id: string;
  price: number;
  currency: string;
  timestamp: string;
}

export interface ListingPriceHistory {
  listing_id: string;
  marketplace_name: string;
  current_price: number;
  history: PriceHistoryPoint[];
}

export interface MatchingResult {
  is_duplicate: boolean;
  confidence_score: number;
  title_similarity?: number;
  brand_match?: boolean;
  spec_score?: number;
  match_reason: string;
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
