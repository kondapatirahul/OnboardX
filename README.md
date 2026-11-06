# OnboardX

OnboardX is an employee onboarding and people-operations workspace for HR teams and employees. It brings organization setup, employee records, departments, onboarding templates, progress tracking, employee self-service and document workflows into one application.

## Technology

- **Frontend:** React, Vite, React Router, Recharts and custom CSS
- **Backend:** Python, FastAPI, SQLAlchemy and Pydantic
- **Database:** PostgreSQL with Alembic migrations
- **Authentication:** JWT bearer tokens, password hashing and role-based access

## Features

- Public product landing page with links to registration and sign in
- HR Admin organization registration and employee organization-code registration
- Authenticated dashboard and department overview
- Employee directory and employee profile management
- Employee self-service profile
- Onboarding templates, stages, assignments and progress
- Document management API and review workflows
- Organization-scoped data access and role-aware routes

## Local setup

### 1. Database

Create a PostgreSQL database named `onboardx`, or update `DATABASE_URL` to point to an existing database.

### 2. Backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` and set your database connection and a unique `SECRET_KEY`. For local development, the CORS setting can remain:

```env
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173
```

Run database migrations and start FastAPI:

```powershell
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend runs at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`.

### 3. Demo accounts

For a local presentation, keep `APP_ENV=development` in `backend/.env`, then open a second terminal:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m app.seed_demo
```

The command is idempotent: it creates the demo organization, department and accounts if they do not exist, and can be run again safely.

| Role | Email | Password |
|---|---|---|
| HR Admin | `hr.demo@onboardx.local` | `OnboardX-HR-Demo-2026!` |
| Employee | `employee.demo@onboardx.local` | `OnboardX-Employee-Demo-2026!` |

**Demo organization code:** `onboardx-demo`

Use the HR Admin account to demonstrate HR-facing areas. Use the Employee account to demonstrate employee self-service. These are local demonstration credentials only. Do not deploy these accounts or passwords to a public or production environment. Change or remove them before any public deployment.

### 4. Frontend

Open another terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The public landing page is the home route. Select **Get started** to register an organization or **Sign in** to enter the workspace.

The Vite development server proxies `/api` requests to `http://127.0.0.1:8000`. If your backend runs elsewhere, set `ONBOARDX_API_TARGET` before starting Vite, or configure `VITE_API_URL` for a direct API URL.

### 5. Production frontend build

```powershell
cd frontend
npm run build
npm run preview
```

## Registration flow

1. An HR Admin registers an organization and receives its organization code.
2. The HR Admin shares that code with employees.
3. Employees verify the organization code and create their accounts.
4. Manager accounts are provisioned by HR; public self-registration is restricted.

## Important deployment notes

- Replace the development `SECRET_KEY` with a long, randomly generated secret.
- Do not expose demo credentials in production.
- Configure production CORS origins explicitly.
- Use private object storage for uploaded documents and configure backups and retention before production use.
- Apply migrations as part of deployment and verify the database connection before accepting registrations.
