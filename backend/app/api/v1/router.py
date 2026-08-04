"""
COMPAREX Backend – API v1 Router

Aggregates all v1 endpoint routers into a single router
that is mounted at /api/v1 in main.py.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    brands,
    categories,
    comparison,
    extension,
    health,
    listings,
    marketplaces,
    products,
    users,
)

v1_router = APIRouter()

# Health
v1_router.include_router(health.router)

# Extension Gateway
v1_router.include_router(extension.router)

# Auth
v1_router.include_router(auth.router)

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
