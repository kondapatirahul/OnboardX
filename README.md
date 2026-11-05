# OnboardX

Employee Onboarding Management SaaS Platform

## Tech Stack

- **Frontend:** React + Vite + JavaScript
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy
- **Database:** PostgreSQL
- **Auth:** JWT + OAuth2 + RBAC
- **Migrations:** Alembic

## Project Structure

```
OnboardX/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/v1/   # Route handlers
│   │   ├── core/     # Config, security
│   │   ├── db/       # Database session
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── repositories/ # Data access
│   │   └── utils/    # Helpers
│   ├── alembic/      # DB migrations
│   └── tests/        # Pytest tests
└── frontend/         # React + Vite app
    └── src/
        ├── components/layout/
        ├── context/
        ├── pages/
        ├── services/
        └── styles/
```

## Getting Started

### Backend

```bash
cd backend
cp .env.example .env   # fill in your values
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/api/docs

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App: http://localhost:5173

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## User Roles

| Role | Description |
|------|-------------|
| SUPER_ADMIN | Platform-wide administration |
| HR_ADMIN | Employee & onboarding management |
| MANAGER | Team oversight & task assignment |
| EMPLOYEE | Personal onboarding dashboard |
