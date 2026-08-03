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

**Phase 1**: Project foundation (Frontend shell, FastAPI backend, Docker, GitHub Actions).  
**Phase 2**: Core authentication, JWT state management, Remember Me, protected routes, interactive dashboard widgets, product catalog & price comparison matrix.  
**Phase 3**: Marketplace Intelligence Core — complete normalized domain models (`Product`, `Marketplace`, `ProductListing`, `PriceHistory`, `Category`, `Brand`, `ProductSpecification`, `ProductImage`), Marketplace Abstraction Layer & `MarketplaceFactory`, Comparison Engine, non-AI Product Matching Engine, dedicated Compare UI (`/compare/[id]`), and 100% clean CI linters.

---

## 🛠 Technology Stack

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 15** (App Router) | React framework with SSR |
| **TypeScript** | Type safety across the codebase |
| **Tailwind CSS** | Utility-first styling |
| **Framer Motion** | Smooth animations |
| **Axios** | Data fetching & token interceptors |
| **Lucide React** | Icon system |

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | High-performance Python API framework |
| **SQLAlchemy 2.0** (async) | ORM with async support & Repository pattern |
| **Alembic** | Database schema migrations |
| **Pydantic v2** | Data validation & settings |
| **Pytest** | Async unit & integration test suite |
| **PostgreSQL** | Primary database |

---

## 🗄 Entity-Relationship (ER) Architecture

```mermaid
erDiagram
    CATEGORY ||--o{ PRODUCT : contains
    BRAND ||--o{ PRODUCT : manufactures
    PRODUCT ||--o{ PRODUCT_LISTING : listed_on
    PRODUCT ||--o{ PRODUCT_SPECIFICATION : has_specs
    PRODUCT ||--o{ PRODUCT_IMAGE : has_images
    MARKETPLACE ||--o{ PRODUCT_LISTING : hosts
    PRODUCT_LISTING ||--o{ PRICE_HISTORY : tracks_prices

    PRODUCT {
        uuid id PK
        string name
        text description
        uuid category_id FK
        uuid brand_id FK
        string ean
        decimal base_price
    }

    BRAND {
        uuid id PK
        string name
        string slug
        text logo_url
    }

    MARKETPLACE {
        uuid id PK
        string name
        string slug
        text base_url
    }

    PRODUCT_LISTING {
        uuid id PK
        uuid product_id FK
        uuid marketplace_id FK
        string marketplace_product_id
        decimal price
        decimal original_price
        decimal discount_percent
        string currency
        text listing_url
        string seller_name
        boolean is_available
        boolean is_prime
        string stock_status
        string delivery_estimate
        decimal rating
        integer review_count
    }

    PRICE_HISTORY {
        uuid id PK
        uuid listing_id FK
        decimal price
        string currency
        timestamp timestamp
    }
```

---

## 📁 Folder Structure

```
COMPAREX/
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions CI
├── frontend/
│   ├── src/
│   │   ├── app/                     # Next.js App Router pages
│   │   │   ├── compare/[id]/        # Dedicated Product Compare Page
│   │   │   ├── dashboard/           # Dashboard & Product Index Management
│   │   │   ├── products/            # Product Catalog & Detail View [id]
│   │   │   ├── login/ & register/   # Auth Pages
│   │   │   └── page.tsx             # Landing Page
│   │   ├── components/
│   │   │   ├── layout/              # Navbar, Footer
│   │   │   └── shared/              # MarketplaceBadge, AuthGuard, ThemeToggle
│   │   ├── context/
│   │   │   └── AuthContext.tsx      # Auth State Provider
│   │   ├── services/
│   │   │   └── api.ts               # Axios client with auto 401 refresh
│   │   └── types/
│   │       └── index.ts             # TypeScript type definitions
│   └── next.config.ts
├── backend/
│   ├── app/
│   │   ├── adapters/                # BaseMarketplaceAdapter & MarketplaceFactory
│   │   ├── api/v1/endpoints/        # comparison, products, listings, marketplaces, auth, users
│   │   ├── core/                    # config, security, redis
│   │   ├── db/                      # base, session
│   │   ├── models/                  # Product, Marketplace, ProductListing, PriceHistory, Category, Brand, ProductSpecification, ProductImage
│   │   ├── repositories/            # Product, Marketplace, ProductListing, PriceHistory, Brand, Category
│   │   ├── schemas/                 # Product, Marketplace, ProductListing, Brand, Comparison
│   │   └── services/                # ComparisonEngineService, ProductMatchingEngine, MarketplaceService, ProductService
│   ├── tests/                       # Pytest integration & unit tests
│   └── .flake8                      # Flake8 lint configuration
└── README.md
```

---

## ⚡ Quick Start

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
python -m app.main
```

---

## 🧪 Testing & Verification

```bash
# Backend Verification
cd backend
flake8 app/       # Flake8 lint check (0 errors)
pytest            # Pytest test suite (100% pass)

# Frontend Verification
cd frontend
npm run lint      # ESLint (0 errors)
npm run build     # Production build check
```

---

## 📑 API Summary (v1)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/health` | Health check endpoint | No |
| `POST` | `/api/v1/auth/register` | User registration | No |
| `POST` | `/api/v1/auth/login` | Authenticate user & issue JWT tokens | No |
| `GET` | `/api/v1/products` | Search & list indexed products | No |
| `GET` | `/api/v1/products/{id}` | Get canonical product details | No |
| `GET` | `/api/v1/products/{id}/compare` | Get comprehensive price comparison matrix | No |
| `GET` | `/api/v1/products/{id}/history` | Get historical price timeline points | No |
| `POST` | `/api/v1/products/match` | Evaluate non-AI product duplicate matching | No |
| `GET` | `/api/v1/marketplaces` | List supported marketplaces | No |
| `POST` | `/api/v1/listings` | Upsert product listing entry | Yes |

---

## 🗺 Roadmap

### ✅ Phase 1 – Foundation
- Landing page, layout structure, FastAPI & Docker setup.

### ✅ Phase 2 – Backend Completion & Frontend Integration
- JWT auth, session persistence, Remember Me, protected routes, interactive dashboard widgets, product catalog & detail views.

### ✅ Phase 3 – Marketplace Intelligence Core
- Complete normalized domain models (`Brand`, `ProductSpecification`, `ProductImage`, `ProductListing`, `PriceHistory`).
- `BaseMarketplaceAdapter` & `MarketplaceFactory` pattern.
- `ComparisonEngineService` (deal scores, price spread, max savings).
- `ProductMatchingEngine` (fuzzy string matching, spec matching, duplicate detection without AI).
- Dedicated Compare Page (`/compare/[id]`) with `MarketplaceBadge` components and responsive layout.

### 🔜 Phase 4 – AI Features & Advanced Extensions
- AI Shopping Assistant (LLM integration) & image search.
- Price drop alert notifications & browser extension.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
