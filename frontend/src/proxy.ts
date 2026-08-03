import { NextRequest, NextResponse } from "next/server";

/**
 * COMPAREX – Next.js Route Protection Proxy
 *
 * Redirects unauthenticated users away from protected routes (/dashboard/*).
 * Redirects authenticated users away from auth pages (login/register).
 *
 * Uses a lightweight cookie `comparex_auth=1` set by AuthContext on login.
 */

// Routes that require authentication
const PROTECTED_PREFIXES = ["/dashboard"];

// Auth-only routes (redirect to dashboard if already logged in)
const AUTH_ROUTES = ["/login", "/register"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Read lightweight auth cookie (set by AuthContext on login)
  const authCookie = request.cookies.get("comparex_auth")?.value;
  const isAuthenticated = authCookie === "1";

  // Protect dashboard routes
  const isProtected = PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
  if (isProtected && !isAuthenticated) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users away from auth pages
  const isAuthRoute = AUTH_ROUTES.some((route) => pathname.startsWith(route));
  if (isAuthRoute && isAuthenticated) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  // Run on all routes except static files, images, and Next.js internals
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)" ],
};
