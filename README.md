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

**Phase 1**: Completed project foundation (Frontend shell, FastAPI backend, Docker, GitHub Actions).  
**Phase 2**: Complete backend domain models & marketplace foundation architecture, full frontend authentication integration (Login/Register APIs, session persistence, automatic token refresh, Remember Me architecture), professional interactive dashboard widgets, full Product module (Catalog, Details, Search UI, Pagination, State management), and 100% clean CI/CD linters.

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

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker + Compose** | Containerization |
| **GitHub Actions** | CI/CD pipeline |

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
│   │   │   ├── login/               # Connected Login page
│   │   │   ├── register/            # Connected Register page
│   │   │   ├── dashboard/           # Professional Dashboard & Products management
│   │   │   ├── products/            # Public Product Catalog & Product Details [id]
│   │   │   ├── layout.tsx           # Root layout with AuthProvider
│   │   │   └── page.tsx             # Landing page
│   │   ├── components/
│   │   │   ├── layout/              # Navbar, Footer
│   │   │   └── shared/              # AuthGuard, ThemeToggle, LoadingSkeleton
│   │   ├── context/
│   │   │   └── AuthContext.tsx      # Auth State, Login, Register, Refresh Session
│   │   ├── services/
│   │   │   └── api.ts               # Axios client with 401 auto-refresh & token persistence
│   │   └── types/
│   │       └── index.ts             # TypeScript type definitions
│   ├── Dockerfile
│   └── next.config.ts
├── backend/
│   ├── app/
│   │   ├── adapters/                # BaseMarketplaceAdapter abstract interface
│   │   ├── api/v1/endpoints/        # auth, users, products, categories, marketplaces, listings
│   │   ├── core/                    # config, logging, security, redis (with test fallback)
│   │   ├── db/                      # base, session
│   │   ├── models/                  # User, Product, Category, Marketplace, ProductListing, PriceHistory
│   │   ├── repositories/            # Base, User, Product, Category, Marketplace, ProductListing
│   │   ├── schemas/                 # Auth, User, Product, Category, Marketplace, ProductListing
│   │   └── services/                # AuthService, UserService, ProductService, CategoryService, MarketplaceService, ProductListingService
│   ├── tests/                       # Pytest test suite with in-memory DB override
│   ├── .flake8                      # Flake8 lint configuration (100 char limit)
│   ├── Dockerfile
│   └── pyproject.toml
├── docker-compose.yml
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Mastermindmani88897/COMPAREX.git
cd COMPAREX
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: **http://localhost:3000**

### 3. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```
Backend runs at: **http://localhost:8000**  
Swagger docs at: **http://localhost:8000/docs**

---

## 🧪 Testing & Verification

### Frontend Verification
```bash
cd frontend
npm run lint      # ESLint (0 errors)
npm run build     # Production build check
```

### Backend Verification
```bash
cd backend
flake8 app/       # Flake8 lint check (0 errors)
pytest            # Pytest test suite (100% pass)
python -c "from app.main import app; print('✓ FastAPI app created successfully')"
```

---

## 📑 API Summary (v1)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/health` | Health check endpoint | No |
| `POST` | `/api/v1/auth/register` | User registration | No |
| `POST` | `/api/v1/auth/login` | Authenticate user & issue JWT tokens | No |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | No |
| `POST` | `/api/v1/auth/logout` | Revoke active access token | Yes |
| `GET` | `/api/v1/users/me` | Fetch authenticated user profile | Yes |
| `PATCH` | `/api/v1/users/me` | Update current user profile | Yes |
| `GET` | `/api/v1/products` | Search & list indexed products | No |
| `GET` | `/api/v1/products/{id}` | Get product details by ID | No |
| `GET` | `/api/v1/products/{id}/compare` | Compare product prices across marketplaces | No |
| `POST` | `/api/v1/products` | Add new product to index | Yes |
| `GET` | `/api/v1/categories` | List product categories | No |
| `GET` | `/api/v1/marketplaces` | List supported marketplaces | No |
| `POST` | `/api/v1/listings` | Upsert product price listing | Yes |

---

## 🗺 Roadmap

### ✅ Phase 1 – Foundation
- Landing page, layout structure, FastAPI & Docker setup.

### ✅ Phase 2 – Backend Completion & Frontend Integration
- Full JWT authentication, state management, session persistence, automatic token refresh, Remember Me support, protected routes.
- Professional Dashboard with Recent Searches, Wishlist, Saved Products, Saved Comparisons, Price Alerts widgets.
- Complete Product Catalog & Details module with real-time price comparison matrix.
- Domain models (`Product`, `Marketplace`, `ProductListing`, `PriceHistory`, `Category`) & Marketplace adapter foundation architecture.
- 100% passing CI linters & test suites.

### 🔜 Phase 3 – Marketplace Engine & Scraper Integrations
- Implementation of concrete marketplace adapters (Amazon, Flipkart, Myntra).
- Automated background price fetching & historical price tracking.

### 🔜 Phase 4 – AI Features & Advanced Extensions
- AI Shopping Assistant (LLM integration) & image search.
- Price drop alert notifications & browser extension.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
