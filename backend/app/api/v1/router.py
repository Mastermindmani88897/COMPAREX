"""
COMPAREX Backend – API v1 Router

Aggregates all v1 endpoint routers into a single router
that is mounted at /api/v1 in main.py.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    ai,
    ai_modes,
    alerts,
    analytics,
    auth,
    brands,
    categories,
    coach,
    comparison,
    coupons,
    dashboard,
    explain,
    extension,
    feedback,
    health,
    listings,
    marketplaces,
    memory,
    metrics,
    persona,
    planner,
    price_history,
    privacy,
    products,
    profile,
    recommendations,
    users,
)

v1_router = APIRouter()

# Health & Metrics
v1_router.include_router(health.router)
v1_router.include_router(metrics.router)

# AI Shopping Intelligence Platform & Advanced Modes
v1_router.include_router(ai.router)
v1_router.include_router(ai_modes.router)

# Extension Gateway
v1_router.include_router(extension.router)

# Auth & Admin Portal
v1_router.include_router(auth.router)
v1_router.include_router(admin.router)

# Users
v1_router.include_router(users.router)

# Categories
v1_router.include_router(categories.router)

# Brands
v1_router.include_router(brands.router)

# Products
v1_router.include_router(products.router)

# Marketplaces
v1_router.include_router(marketplaces.router)

# Price Listings
v1_router.include_router(listings.router)

# Comparison & Matching Engine
v1_router.include_router(comparison.router)

# Price History Intelligence
v1_router.include_router(price_history.router)

# Price Drop Alerts & Watchlist
v1_router.include_router(alerts.router)

# Smart Coupon Engine
v1_router.include_router(coupons.router)

# Shopping Dashboard
v1_router.include_router(dashboard.router)

# Personal Shopping Profile & Preferences
v1_router.include_router(profile.router)

# Shopping Memory Timeline
v1_router.include_router(memory.router)

# Shopping DNA & Persona Engine
v1_router.include_router(persona.router)

# Personalized Recommendation Engine
v1_router.include_router(recommendations.router)

# AI Shopping Coach
v1_router.include_router(coach.router)

# Explainable AI & CompareX Explain
v1_router.include_router(explain.router)

# AI Feedback Loop
v1_router.include_router(feedback.router)

# Shopping Analytics Dashboard
v1_router.include_router(analytics.router)

# Smart Privacy Center
v1_router.include_router(privacy.router)

# Flagship AI Marketplace Planner
v1_router.include_router(planner.router)
