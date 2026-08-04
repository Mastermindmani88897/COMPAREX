# COMPAREX – Enterprise Placement & Portfolio Package

## Executive Summary & Elevator Pitch

> **COMPAREX** is an enterprise-grade, privacy-first, AI-powered Smart Shopping Intelligence Platform and Marketplace Operating System. It aggregates products across 9 major e-commerce marketplaces (Amazon, Flipkart, Croma, Reliance Digital, Vijay Sales, Myntra, Ajio, Meesho, Nykaa) using Clean Architecture, a multi-agent AI orchestrator, real-time price history analytics, auto-coupon matching, and an AI Marketplace Planner.

---

## Portfolio Bullet Points for Resume

- **Full-Stack AI Architecture**: Built an enterprise shopping intelligence platform connecting 9 e-commerce marketplaces with FastAPI, Next.js 16, PostgreSQL, Redis, and Chrome Extension Manifest V3.
- **Multi-Agent AI Orchestrator**: Designed an `AIAgentOrchestrator` coordinating 9 specialized LLM agents (`ShoppingAgent`, `RecommendationAgent`, `PriceAgent`, `ReviewAgent`, `ComparisonAgent`, `BudgetAgent`, `DealAgent`, `VisionAgent`, `CoachAgent`) with fact-grounding.
- **AI Marketplace Planner (Flagship)**: Developed a natural-language Shopping Operating System that parses multi-item goals (*e.g., "Engineering student setup under ₹90,000"*), optimizes budget distribution, and validates hardware ecosystem compatibility.
- **Explainable AI & CompareX Explain**: Built a transparent recommendation engine featuring CompareX Explain rationales (*"Why Product A > Product B"*), expected product lifespan, and upgrade paths.
- **Enterprise Security & Observability**: Implemented API rate limiting, security headers (CSP, HSTS, X-Frame-Options), prompt injection defense, structured logging, request ID tracing, and Prometheus metrics monitoring.

---

## System Architecture Diagram

```
                               ┌──────────────────────────────────────────────┐
                               │       Client Layer & Extension Gateway       │
                               │  (Next.js 16 Frontend + Manifest V3 Ext)    │
                               └──────────────────────┬───────────────────────┘
                                                      │
                               ┌──────────────────────▼───────────────────────┐
                               │  Enterprise Security & Observability Gateway  │
                               │   (Rate Limits, Security Headers, Tracing)   │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┼──────────────────────────────┐
                       │                              │                              │
        ┌──────────────▼──────────────┐┌──────────────▼──────────────┐┌──────────────▼──────────────┐
        │  Multi-Agent AI Orchestrator││   Live Marketplace Connector││   AI Marketplace Planner    │
        │    (9 Specialized Agents)   ││    (9 Supported Stores)     ││  (Goal, Budget, Compat Engine)│
        └──────────────┬──────────────┘└──────────────┬──────────────┘└──────────────┬──────────────┘
                       │                              │                              │
                       └──────────────────────────────┼──────────────────────────────┘
                                                      │
                               ┌──────────────────────▼───────────────────────┐
                               │      Data Storage & Cache Layer             │
                               │     (PostgreSQL + Redis Cache Store)         │
                               └──────────────────────────────────────────────┘
```

---

## Technical Interview Q&A Guide

### Q1: How does COMPAREX prevent AI hallucinations in product recommendations?
> **Answer**: COMPAREX implements a **Fact-Grounded Decision Engine**. The AI agent layer never invokes LLMs to invent prices or specifications. Instead, all candidate products are fetched live from database listings and connector APIs. The LLM receives structured JSON data context and is constrained to output structured Pydantic schemas.

### Q2: How does the AI Marketplace Planner perform budget optimization?
> **Answer**: The `BudgetOptimizer` uses a category prioritization algorithm. Products are marked as `REQUIRED`, `RECOMMENDED`, or `OPTIONAL`. If the user's budget is lower than the sum of baseline recommendations, non-required items are scaled down or converted into recommended alternatives while preserving required components.

### Q3: How is data privacy handled?
> **Answer**: User profiling strictly adheres to an **explicit opt-in consent model**. The platform tracks no sensitive passwords, payment credentials, or cookies. The Smart Privacy Center (`/privacy`) provides 1-click JSON data export and complete memory purging.

---

## Frequently Asked Questions (FAQ)

- **Which marketplaces are supported?**: Amazon India, Flipkart, Croma, Reliance Digital, Vijay Sales, Myntra, Ajio, Meesho, and Nykaa.
- **Can COMPAREX run offline or without API keys?**: Yes, fallback mock providers and synthetic price history generators guarantee 100% offline development and demo stability.
