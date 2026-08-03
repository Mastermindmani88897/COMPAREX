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
  <br /><br />
  
  <h1>COMPAREX</h1>
  <p><strong>AI Shopping Intelligence Platform</strong></p>
  <p>Compare products across 10+ marketplaces with the power of AI — real-time prices, personalized recommendations, and instant deal alerts.</p>
</div>

---

## 🚀 Overview

COMPAREX is a production-quality AI Shopping Intelligence Platform that aggregates product pricing from multiple marketplaces, applies AI-driven analysis, and delivers personalized shopping insights to help users always get the best deal.

**Phase 1** establishes the complete project foundation: premium UI, clean backend architecture, Docker setup, and CI/CD pipeline.

---

## 🛠 Technology Stack

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 15** (App Router) | React framework with SSR |
| **TypeScript** | Type safety across the codebase |
| **Tailwind CSS v4** | Utility-first styling |
| **Framer Motion** | Smooth animations |
| **TanStack Query** | Data fetching & caching |
| **Lucide React** | Icon system |
| **next-themes** | Dark/light mode |

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | High-performance Python API framework |
| **SQLAlchemy 2.0** (async) | ORM with async support |
| **Alembic** | Database schema migrations |
| **Pydantic v2** | Data validation & settings |
| **Uvicorn** | ASGI server |
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
│   │   │   ├── (auth)/              # Auth pages group
│   │   │   │   ├── login/
│   │   │   │   ├── register/
│   │   │   │   └── forgot-password/
│   │   │   ├── about/
│   │   │   ├── contact/
│   │   │   ├── privacy/
│   │   │   ├── terms/
│   │   │   ├── dashboard/
│   │   │   ├── layout.tsx           # Root layout
│   │   │   ├── page.tsx             # Landing page
│   │   │   ├── not-found.tsx        # 404 page
│   │   │   └── loading.tsx          # Global loading skeleton
│   │   ├── components/
│   │   │   ├── layout/              # Navbar, Footer
│   │   │   ├── sections/            # HeroSection, FeaturesSection
│   │   │   └── shared/              # ThemeToggle, LoadingSkeleton
│   │   ├── config/
│   │   │   └── site.ts              # Site metadata & config
│   │   ├── hooks/
│   │   │   └── useTheme.tsx         # Theme provider & hook
│   │   ├── lib/
│   │   │   └── utils.ts             # Utility functions
│   │   ├── services/
│   │   │   └── api.ts               # Axios API client
│   │   └── types/
│   │       └── index.ts             # TypeScript type definitions
│   ├── .env.example
│   ├── Dockerfile
│   └── next.config.ts
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/           # health, auth, users, products, marketplaces
│   │   │   └── router.py            # v1 router aggregator
│   │   ├── core/                    # config, logging, security
│   │   ├── db/                      # base, session
│   │   ├── middleware/              # cors, error_handler
│   │   ├── models/                  # user, product, marketplace
│   │   ├── repositories/            # base, user, product
│   │   ├── schemas/                 # common, user, product, marketplace
│   │   ├── services/                # auth, user, product
│   │   └── main.py                  # FastAPI app factory
│   ├── alembic/
│   ├── .env.example
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- **Node.js** 20+
- **Python** 3.12+
- **PostgreSQL** 16+ (or use Docker)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Mastermindmani88897/COMPAREX.git
cd COMPAREX
```

### 2. Frontend Setup
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Frontend runs at: **http://localhost:3000**

### 3. Backend Setup
```bash
cd backend
cp .env.example .env
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python -m app.main
```

Backend runs at: **http://localhost:8000**  
Swagger docs at: **http://localhost:8000/docs**

### 4. Docker (Full Stack)
```bash
# Run entire stack with one command
docker-compose up --build
```

---

## 🔧 Development Workflow

### Frontend Commands
```bash
npm run dev       # Start dev server (localhost:3000)
npm run build     # Production build
npm run lint      # ESLint check
npm run start     # Start production server
```

### Backend Commands
```bash
# Run development server
python -m app.main

# Lint check
flake8 app/

# Format code
black app/
isort app/

# Database migrations (Phase 2)
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### API Endpoints (Phase 1)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check ✅ |
| `POST` | `/api/v1/auth/register` | Register (Phase 2) |
| `POST` | `/api/v1/auth/login` | Login (Phase 2) |
| `GET` | `/api/v1/users/me` | Current user (Phase 2) |
| `GET` | `/api/v1/products/` | List products (Phase 2) |
| `GET` | `/api/v1/marketplaces/` | List marketplaces (Phase 2) |

---

## 🌿 Environment Variables

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Backend (`backend/.env`)
```env
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/comparex
SECRET_KEY=your-super-secret-key
```

See `.env.example` files for the full list.

---

## 🗺 Roadmap

### ✅ Phase 1 – Foundation (Complete)
- Premium landing page with dark/light mode
- All core pages (auth, marketing, legal, dashboard shell)
- FastAPI backend with clean architecture
- Docker & CI/CD setup

### 🔜 Phase 2 – Core Features
- User authentication (JWT)
- Product search & indexing
- Marketplace integrations (Amazon, Flipkart)
- Price comparison engine
- Database migrations

### 🔜 Phase 3 – AI Features
- AI Shopping Assistant (LLM integration)
- Image-based product search
- Price prediction models
- Personalized recommendations

### 🔜 Phase 4 – Advanced
- Price alerts & notifications
- Browser extension
- Analytics dashboard
- Mobile app

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p>Built with ❤️ by the COMPAREX Team</p>
  <p>
    <a href="https://github.com/Mastermindmani88897/COMPAREX">GitHub</a> •
    <a href="mailto:support@comparex.io">Support</a>
  </p>
</div>
