# MarketingHub — Project overview

This document summarizes **core features**, **architecture**, and **how the pieces fit together** for the MarketingHub Django application.

---

## What MarketingHub is

MarketingHub is a **multi-role web platform** (customers, employees, administrators) built around:

- **Invitation-based customer signup** (customers register with an employee’s invite code).
- **Wallet-style balances**, **deposits**, and **withdrawal requests** with admin approval.
- **KYC** (identity documents + face video + withdrawal wallet details) before withdrawals.
- **Order batches**: admins define **batches**, **products**, and **orders**; customers receive **per-customer copies** of orders and **submit** (“grab”) them to earn **commission** credited to their balance.
- **Employee dashboards** listing customers referred via their invitation code, plus **deposit rollups** (`Employee` app models).
- **Operational admin tools** under `/admin-control/` (finance, users, batches, Telegram links, marketing images).

The product can run in **Docker** (PostgreSQL and Redis) or on **Railway** / similar hosts (see `CSRF_TRUSTED_ORIGINS`, `Procfile`). See **[DOCKER.md](DOCKER.md)** for container setup.

---

## Running with Docker

Use **Docker Compose** for PostgreSQL, Redis, and the web app. Summary:

- `docker compose up --build` from the repo root
- Migrations and `collectstatic` run on web startup ([`docker/entrypoint.sh`](docker/entrypoint.sh))
- **Media** is stored in a named volume (`media_data`); **Redis** backs cache and sessions when `REDIS_URL` is set (see [DOCKER.md](DOCKER.md))

Full steps, volumes, and `createsuperuser` are documented in **[DOCKER.md](DOCKER.md)**.

---

## Technology stack

| Layer | Details |
|--------|---------|
| **Framework** | Django **5.0.x** (`project/`) |
| **WSGI server (production)** | **Gunicorn** (`Procfile`: `gunicorn project.wsgi`) |
| **Database** | **SQLite** when `DATABASE_URL` is unset; **PostgreSQL** when `DATABASE_URL` is set (e.g. Docker). See [DOCKER.md](DOCKER.md). |
| **Cache / sessions** | **Redis** when `REDIS_URL` is set (Docker Compose); otherwise in-memory cache and database sessions. |
| **User model** | Custom: `AUTH_USER_MODEL = 'accounts.User'` |
| **CORS** | `django-cors-headers` with **`CORS_ALLOW_ALL_ORIGINS = True`** (permissive; review for production). |
| **Media / static** | `MEDIA_ROOT`, `STATIC_ROOT` / `STATICFILES_DIRS`, Pillow for uploads |
| **i18n** | Multiple languages in `settings.LANGUAGES`, `LOCALE_PATHS`, language selection view |
| **Pinned Python deps** | See [`requirements.txt`](requirements.txt) (Django, cors headers, Gunicorn, Pillow, Postgres driver, Redis client, `dj-database-url`). |

---

## Repository layout (high level)

```
MarketingHub/
├── project/           # Django project: settings, root urls, wsgi/asgi
├── docker/            # entrypoint.sh (migrate, collectstatic, gunicorn)
├── accounts/          # Auth, roles, registration, dashboards entry
├── home/              # Customer app: balance, KYC, deposits, withdrawals, orders
├── adminControl/      # Admin operations, catalog, batches, customer assignments
├── Employee/          # Employee deposit aggregation models (no URL module in root urls)
├── Base/              # Abstract `BaseModel` (UUID PK, timestamps)
├── templates/         # HTML templates
├── static/            # Static assets (dev)
├── locale/            # Translation files (if populated)
├── requirements.txt
├── Procfile             # Railway-style process definition
└── manage.py
```

---

## URL map (user-facing)

Root URL config: `project/urls.py`.

| Mount | App | Purpose |
|--------|-----|---------|
| `/` | `accounts` | Login, signup, role-specific dashboards, passwords, language, profile photo |
| `/home/` | `home` | Customer home, wallet, KYC, deposits/withdrawals, order UI, settings, static pages |
| `/admin-control/` | `adminControl` | Admin tools for money, KYC, users, batches/orders, Telegram, wallets |
| `/admin/` | Django admin | Built-in admin site |

**Note:** `Employee` is not included as a separate `path(...)` in `project/urls.py`. Employee UX uses **`accounts`** routes (`Employee-login/`, `Employee-Dashboard/`).

---

## User roles

Defined on `accounts.User` (`AbstractUser` extensions):

| Flag | Meaning |
|------|---------|
| `is_customer` | End user: balance, orders, deposits, withdrawals |
| `is_employee` | Has **`invitation_code`**; customers sign up with that code; dashboard lists referred customers |
| `is_admin` | Uses admin login + admin dashboard + `/admin-control/` style operations |

Login flows enforce **role + posted role id** (customer vs employee vs admin) so the same username cannot log in through the wrong portal by mistake (when validation succeeds).

---

## Core features (by area)

### 1. Authentication and session (`accounts`)

- **Customer login** (`/`): records **login IP** on `UserIp` when possible (uses `X-Forwarded-For` when behind a proxy).
- **Employee login** (`/Employee-login/`), **Admin login** (`/Admin-login/`).
- **Remember me**: optional session expiry (browser-close vs persistent).
- **Logout**, **change account password** (Django auth password), **change payment password** (numeric `PaymentPassword`).
- **Profile photo** upload.
- **Language selection** stored in session (`LANGUAGE_SESSION_KEY`).

### 2. Registration and onboarding (`accounts.register`)

- **Invitation-only** customer signup: `invite_code` must match an **`is_employee=True`** user’s `invitation_code`.
- Creates related records in one transaction: **`UserIp`**, **`Invite_Code`**, **`PaymentPassword`**, **`Telegram`** (random admin Telegram link from pool), **`OrderCount`**, **`User_Wallet_Address`** (random **USDT** pool address from `WalletAddress`), **`AccountBalance`**, **`GapAmount`**.
- Validates password length, email/username uniqueness, payment password format.

### 3. Customer “home” experience (`home`)

- **Dashboard / profile**: `index/`, `mine/`, `settings/`, `services/`, `about-us/` (uses `ExtraPictures` for branding/about assets).
- **KYC**: upload ID front/back, face video, wallet type/address → **`KYC`** model; admin verifies (`is_verified`).
- **Wallet management / verification** pages after upload.
- **Deposits**: JSON **POST** creates/updates **`Deposit`**, ties to user’s **`User_Wallet_Address`**, returns address for user to pay; **`deposite_records`** lists history.
- **Withdrawals**: requires **verified KYC**, **≥ 20 submitted orders** (`OrderCount`), no duplicate pending withdrawal; creates **`Withdraw`** row; **payment password** check; **does not** debit balance in the snippet shown—admin **approval** finalizes (`approve_withdraw`).
- **Withdrawal status** JSON by `withdrawal_id` (UUID on `Withdraw` via `BaseModel` / related—`Withdraw` uses `created_at` on model; status uses `uid` from `BaseModel` pattern where applicable—see `home.models.Withdraw` and views).
- **Order menu / management**: UI tiers colored by **balance bands** (e.g. &lt;350, 350–600, ≥600).
- **Grab order** (`grab_order`): loads next unsubmitted **`CustomerOrder`** for the user; **POST** marks orders submitted, computes **commission** from product **`commission_rate`** (Simple vs **Lucky** multi-product), updates **`AccountBalance`** and **`OrderCount`**; handles **insufficient balance** via **`GapAmount`**.

### 4. Admin control plane (`adminControl`)

- **Deposits**: `update_deposit` — mark pending deposit received, set amount; should align with balance updates per your business rules (verify signal/model `save` side effects).
- **Withdrawals**: `approve_withdraw` — set processed flag and amount (KYC must be verified).
- **KYC**: verify or delete KYC record.
- **Per-user maintenance**: update **Telegram** link, update **custodial/pool wallet** (`User_Wallet_Address`), **toggle `is_active`**, **reset order count**, **delete customer**.
- **Catalog & batches**: `orders_panel` creates **`Batch`**; `fetch_orders` / `add_orders` / `finalize_batch` / `delete_batch_order` manage **`Order`** and **`Product`** within batches.
- **Customer assignment**: grant batches to customers (`CustomerBatch`), single batch grant/remove, **`fetch_custom_orders`**, **`update_customer_order`** for per-customer order line overrides (`CustomerOrder` with custom product/amounts/`is_submitted`).
- **Cleanup**: `delete_unused_products`.
- **Pools**: `WalletAddress` (random USDT address for deposits), `AdminTelegram` (random support link), `ExtraPictures` (logos/about images).

### 5. Employee experience (`accounts` + `Employee` models)

- **Employee dashboard**: lists **`User`** rows where `invitation_code` matches the employee’s code and `is_customer=True`.
- **`EmployeeDeposit`**: aggregates referred customers’ **`AccountBalance`** deposit/withdrawal totals (`update_deposits` on the model).

### 6. Django admin & `Base`

- Standard **`/admin/`** for model administration.
- **`BaseModel`**: UUID primary key, `created_at` / `updated_at` (note: both fields use `auto_now` / `auto_now_add` in a way worth auditing if you rely on strict “created vs updated” semantics).

---

## Important domain objects (concise)

| Model / area | Role |
|--------------|------|
| `User` | Roles, invite code for employees, customers store employee’s code at signup |
| `AccountBalance` | Running balance, commissions, deposit/withdrawal totals |
| `Deposit` / `Withdraw` | Pending/completed money movement requests |
| `KYC` | Compliance gate for withdrawals |
| `Batch` / `Product` / `Order` | Admin-defined catalog and order templates (Simple vs Lucky) |
| `CustomerBatch` / `CustomerOrder` | Per-user clone of batches/orders for grabbing and submission |
| `OrderCount` | Submitted order count (withdrawal eligibility) |
| `GapAmount` | Shortfall when balance &lt; order total at grab time |
| `WalletAddress` / `User_Wallet_Address` | Pool vs per-user deposit addressing |
| `PaymentPassword` | Separate numeric PIN for sensitive money actions |

---

## Security and production checklist (read this before going live)

- **`DEBUG = True`** and **hard-coded `SECRET_KEY`** in `project/settings.py` are **not safe for production**; use environment variables and `DEBUG=False`.
- **`ALLOWED_HOSTS = ['*']`** and **`CORS_ALLOW_ALL_ORIGINS = True`** are broad; tighten for a public deployment.
- Several customer/admin views use **`@csrf_exempt`** on POST JSON endpoints—ensure you understand CSRF risk or protect via alternate means (tokens, same-site session, etc.).
- **Payment passwords** and withdrawal data are sensitive—audit logging, HTTPS-only, and hashing policy for any stored secrets.
- **Financial correctness**: trace full **deposit → balance credit** and **withdrawal → balance debit** paths across signals/views so they cannot double-apply or skip validation.

---

## How to run locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

Visit `/` for customer login, `/Admin-login/` and `/Employee-login/` for other roles, `/admin/` for Django admin.

---

## Related files (quick reference)

| Topic | File(s) |
|-------|---------|
| Settings | `project/settings.py` |
| Root routes | `project/urls.py` |
| Customer routes | `home/urls.py` |
| Auth & dashboards | `accounts/urls.py`, `accounts/views.py` |
| Admin tools | `adminControl/urls.py`, `adminControl/views.py` |
| Core customer money / KYC models | `home/models.py` |
| User & wallet models | `accounts/models.py` |
| Batch/order catalog | `adminControl/models.py` |
| Employee rollup | `Employee/models.py` |

---

*Generated from the codebase structure and main view/model flows. For line-accurate behavior, follow the implementations in the files above.*
