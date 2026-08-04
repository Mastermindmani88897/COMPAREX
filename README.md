<div align="center">
  <img src="https://img.shields.io/badge/COMPAREX-AI%20Shopping%20Intelligence-6366f1?style=for-the-badge&logo=lightning&logoColor=white" alt="COMPAREX" />
  <br /><br />
  
  <a href="#">
    <img src="https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/CI%2FCD-Passing-brightgreen?style=flat-square&logo=githubactions" />
  </a>
  <br /><br />
  
  <h1>COMPAREX</h1>
  <p><strong>AI Shopping Intelligence Platform</strong></p>
  <p>Compare products across 10+ marketplaces with real-time prices, personalized recommendations, and instant deal alerts.</p>
</div>

---

## 🚀 Overview

COMPAREX is a production-quality AI Shopping Intelligence Platform that aggregates product pricing from multiple marketplaces, applies AI-driven analysis, and delivers personalized shopping insights.

- **Phase 1**: Project foundation (Frontend shell, FastAPI backend, Docker, GitHub Actions).
- **Phase 2**: Core authentication, JWT state management, Remember Me, protected routes, interactive dashboard widgets, product catalog & price comparison matrix.
- **Phase 3**: Marketplace Intelligence Core — complete normalized domain models (`Product`, `Marketplace`, `ProductListing`, `PriceHistory`, `Category`, `Brand`, `ProductSpecification`, `ProductImage`), Marketplace Abstraction Layer & `MarketplaceFactory`, Comparison Engine, non-AI Product Matching Engine, dedicated Compare UI (`/compare/[id]`), and 100% clean CI linters.
- **Phase 4**: Production-Ready Marketplace Connector Framework — `ConnectorRegistry`, `CategoryCapabilityRegistry`, 9 specialized retail mock connectors (Amazon, Flipkart, Croma, Reliance Digital, Vijay Sales, Myntra, Ajio, Meesho, Nykaa), `MarketplaceAggregatorService` with concurrent query gathering, deduplication, deal-scoring, Redis response caching (TTL 300s), aggregator APIs (`/comparison/aggregate`), and Live Aggregator UI (`/compare`).
- **Phase 5**: Browser Extension Ecosystem — Manifest V3 extension (`extension/`), Background Service Worker, public product extractor, floating draggable comparison overlay (`overlay/`), popup UI (`popup/`), options page (`options/`), messaging bus, storage abstraction, extension gateway APIs (`/extension/product`, `/extension/status`, `/extension/version`), and web onboarding pages (`/extension`, `/extension/settings`).

---

## 🧩 Extension Architecture & Ecosystem

```
extension/
├── manifest.json                  # Manifest V3 configuration
├── background/
│   └── service_worker.js          # Service Worker lifecycle, messaging & health check
├── content/
│   ├── extractor.js               # Safe public product DOM information extractor
│   └── content_script.js          # Marketplace page detector & overlay trigger
├── popup/
│   ├── popup.html                 # Extension status & product summary popup
│   ├── popup.css
│   └── popup.js
├── options/
│   ├── options.html               # Theme, overlay position & store toggle settings
│   ├── options.css
│   └── options.js
├── overlay/
│   ├── overlay.js                 # Floating draggable comparison widget
│   └── overlay.css
├── services/
│   └── api_service.js             # Extension API gateway client
├── storage/
│   └── extension_storage.js       # Chrome storage / localStorage wrapper
├── messaging/
│   └── bus.js                     # Unified message passing abstraction
├── shared/
│   └── constants.js               # Extension constants & defaults
├── utils/
│   └── dom_helpers.js             # DOM parsing & price extraction helpers
└── assets/
    ├── icon-16.png                # Extension icons
    ├── icon-48.png
    └── icon-128.png
```

---

## 🛠 Technology Stack

### Frontend & Extension
| Technology | Purpose |
|---|---|
| **Next.js 15** (App Router) | React framework with SSR & Turbopack |
| **Manifest V3** | Chrome Extension architecture |
| **TypeScript** | Type safety across web app & DTO schemas |
| **Tailwind CSS** | Utility-first styling |
| **Framer Motion** | Smooth micro-animations |
| **Axios / Fetch** | Data fetching & API clients |
| **Lucide React** | Icon system |

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | High-performance Python API framework |
| **SQLAlchemy 2.0** (async) | ORM with async support & Repository pattern |
| **Alembic** | Database schema migrations |
| **Pydantic v2** | Data validation & settings |
| **Pytest** | Async unit & integration test suite |
| **Upstash / Local Redis** | Fast caching for aggregator responses & JWT blacklist |
| **PostgreSQL** | Primary database |

---

## 📁 Folder Structure

```
COMPAREX/
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions CI (lint + startup + 11 pytest tests)
├── extension/                       # Manifest V3 Browser Extension Ecosystem
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── compare/             # Live Multi-Marketplace Connector Aggregator Page
│   │   │   ├── compare/[id]/        # Product Comparison Matrix View
│   │   │   ├── dashboard/           # Dashboard & Settings
│   │   │   ├── extension/           # Onboarding & Extension Settings Sync
│   │   │   ├── products/            # Catalog & Details
│   │   │   └── page.tsx             # Landing Page
│   │   ├── components/              # Shared UI components & badges
│   │   ├── services/                # Axios API client
│   │   └── types/
│   │       └── index.ts             # TypeScript interfaces for Aggregator & Extension
├── backend/
│   ├── app/
│   │   ├── adapters/                # BaseMarketplaceAdapter, ConnectorRegistry, CategoryCapabilityRegistry, 9 Mock Connectors
│   │   ├── api/v1/endpoints/        # extension, comparison, marketplaces, products, brands, listings, auth, users
│   │   ├── core/                    # config, security, redis
│   │   ├── db/                      # base, session
│   │   ├── models/                  # SQLAlchemy ORM Models
│   │   ├── repositories/            # Data Access Repositories
│   │   ├── schemas/                 # Extension, Product, Marketplace, ProductListing, Brand, Comparison
│   │   └── services/                # MarketplaceAggregatorService, ComparisonEngineService, ProductMatchingEngine
│   ├── tests/                       # Pytest test suite (test_phase3.py, test_phase4.py, test_phase5.py)
│   └── .flake8
└── README.md
```

---

## 🧪 Testing & Verification

```bash
# Backend Verification
cd backend
flake8 app/       # Flake8 lint check (0 errors)
pytest            # Pytest test suite (100% pass - 11 tests)

# Frontend Verification
cd frontend
npm run lint      # ESLint (0 errors)
npm run build     # Production build check (18 routes generated)
```

---

## 📑 Extension Gateway API Summary (v1)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/extension/status` | Extension gateway connectivity & active connectors status | No |
| `GET` | `/api/v1/extension/version` | Extension client version compatibility check | No |
| `POST` | `/api/v1/extension/product` | Ingest product payload from content script & return live comparison | No |
| `POST` | `/api/v1/extension/compare` | Quick comparison matrix lookup for floating overlay | No |

---

## 🗺 Roadmap

### ✅ Phase 1 – Foundation
- Landing page, layout structure, FastAPI & Docker setup.

### ✅ Phase 2 – Backend Completion & Frontend Integration
- JWT auth, session persistence, Remember Me, protected routes, interactive dashboard widgets, product catalog & detail views.

### ✅ Phase 3 – Marketplace Intelligence Core
- Domain models (`Brand`, `ProductSpecification`, `ProductImage`, `ProductListing`, `PriceHistory`), `MarketplaceFactory`, `ComparisonEngineService`, `ProductMatchingEngine`.

### ✅ Phase 4 – Marketplace Connector Framework
- `BaseMarketplaceAdapter` & `BaseMarketplaceConnector` standard interface, `ConnectorRegistry` managing 9 retail connectors, `CategoryCapabilityRegistry`, `MarketplaceAggregatorService` with concurrent queries, Redis response caching (TTL 300s), and `/compare` live aggregator.

### ✅ Phase 5 – Browser Extension Ecosystem
- Top-level `extension/` directory with Manifest V3, Background Service Worker, Public Extractor, Floating Draggable Overlay, Popup UI, Options UI, Extension Gateway APIs (`/extension/product`, `/extension/status`, `/extension/version`), and web onboarding pages (`/extension`, `/extension/settings`).

### 🔜 Phase 6 – AI Features & Advanced Extensions
- AI Shopping Assistant (LLM integration) & image search.
- Price drop alert notifications & email triggers.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
