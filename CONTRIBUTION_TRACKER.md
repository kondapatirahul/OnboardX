# OnboardX — GitHub Contribution Tracker

## Target: 30 PRs / 100+ Commits

---

## Cumulative Totals

| Metric | Count |
|--------|-------|
| PRs Created | 5 |
| PRs Merged | 3 |
| Total Commits | 13 |
| Branches Active | 2 |

---

## PR Log

### PR-01 — DAY 1 Project Setup
- **Branch:** `project_setup`
- **Status:** ✅ Merged
- **Commits:** 1
- **Commit messages:**
  - `added project setup with FastAPI backend and React frontend`
- **Files:** 50 files — full backend + frontend scaffold
- **Tests:** `npm run build` ✅ | `pytest` 1 passed ✅

---

### PR-02 — Database Models
- **Branch:** `database_models`
- **Status:** ✅ Merged
- **Commits:** 3
- **Commit messages:**
  - `updated database models with all enums and relationships`
  - `added initial alembic migration for all database tables`
  - `added model exports to models __init__`
- **DB changes:** Added 15 tables — organizations, departments, users, employees, onboarding_templates, onboarding_stages, onboarding_instances, onboarding_tasks, documents, document_reviews, training_courses, training_assignments, notifications, calendar_events, audit_logs
- **Tests:** Python import verification ✅

---

### PR-03 — Authentication Backend
- **Branch:** `authentication`
- **Status:** ✅ Merged
- **Commits:** 4
- **Commit messages:**
  - `added JWT and password hashing security utilities`
  - `added auth request and response schemas`
  - `added auth service and JWT dependency injection`
  - `added auth API routes for register, login and me endpoint`
- **API changes:** `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- **Files:** `security.py`, `deps.py`, `auth_service.py`, `schemas/auth.py`, `api/v1/auth.py`
- **Tests:** `pytest` 1 passed ✅ | Route registration verified ✅

---

### PR-04 — Login Page
- **Branch:** `login_page`
- **Status:** 🟡 Open — awaiting merge
- **Commits:** 3
- **Commit messages:**
  - `added login page with form validation and password toggle`
  - `updated auth css with field error states and password toggle styles`
  - `updated auth context to verify token on app load via me endpoint`
- **Files:** `LoginPage.jsx`, `auth.css`, `AuthContext.jsx`
- **Tests:** `npm run build` ✅

---

### PR-05 — Register Page
- **Branch:** `register_page`
- **Status:** 🟡 Open — awaiting merge
- **Commits:** 3
- **Commit messages:**
  - `added register page with role selection and form validation`
  - `updated auth css with role selector, field errors and password toggle styles`
  - `updated api service with patch method and 204 response handling`
- **Files:** `RegisterPage.jsx`, `auth.css`, `api.js`
- **Tests:** `npm run build` ✅

---

## Upcoming PRs

| # | Branch | Module | Status |
|---|--------|--------|--------|
| PR-06 | `dashboard_backend` | Dashboard stats API | 🔜 Next |
| PR-07 | `employee_dashboard` | Dashboard UI + charts | 🔜 |
| PR-08 | `employee_management` | Employee CRUD backend | 🔜 |
| PR-09 | `employee_profile` | Employee detail page | 🔜 |
| PR-10 | `onboarding_backend` | Onboarding templates API | 🔜 |
| PR-11 | `onboarding_workflow` | Onboarding UI | 🔜 |
| PR-12 | `document_management` | Document upload + storage | 🔜 |
| PR-13 | `document_approval` | HR review flow | 🔜 |
| PR-14 | `task_management` | Task CRUD + assignment | 🔜 |
| PR-15 | `task_dashboard` | Task UI | 🔜 |
| PR-16 | `notification_system` | Notification backend | 🔜 |
| PR-17 | `notification_ui` | Notification bell + panel | 🔜 |
| PR-18 | `training_backend` | Training courses API | 🔜 |
| PR-19 | `training_module` | Training UI | 🔜 |
| PR-20 | `calendar_module` | Calendar events | 🔜 |
| PR-21 | `reports_backend` | Analytics endpoints | 🔜 |
| PR-22 | `reports_dashboard` | Reports UI + charts | 🔜 |
| PR-23 | `organization_settings` | Org profile + departments | 🔜 |
| PR-24 | `audit_logs` | Audit log model + UI | 🔜 |
| PR-25 | `sidebar_navigation` | Sidebar polish + RBAC | 🔜 |
| PR-26 | `responsive_layout` | Mobile responsive | 🔜 |
| PR-27 | `api_integration` | Frontend hooks + error boundaries | 🔜 |
| PR-28 | `testing_suite` | Full pytest test suite | 🔜 |
| PR-29 | `bug_fixes` | Cross-module fixes | 🔜 |
| PR-30 | `deployment_prep` | Render config + final docs | 🔜 |

---

## PR Creation URLs (open in browser)

- PR-04 login_page → https://github.com/kondapatirahul/OnboardX/pull/new/login_page
- PR-05 register_page → https://github.com/kondapatirahul/OnboardX/pull/new/register_page
