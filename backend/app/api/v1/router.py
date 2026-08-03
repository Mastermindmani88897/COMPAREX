"""
COMPAREX Backend – API v1 Router

Aggregates all v1 endpoint routers into a single router
that is mounted at /api/v1 in main.py.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, marketplaces, products, users

v1_router = APIRouter()

# Health
v1_router.include_router(health.router)

# Auth
v1_router.include_router(auth.router)

# Users
v1_router.include_router(users.router)

# Products
v1_router.include_router(products.router)

# Marketplaces
v1_router.include_router(marketplaces.router)
