# Docker (MarketingHub + PostgreSQL + Redis)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Compose v2

## Quick start

1. **Optional:** copy environment template and set a real secret key:

   ```bash
   cp .env.example .env
   # Edit .env — at minimum set SECRET_KEY for anything beyond local dev.
   ```

2. Build and run the stack (Django + Postgres + Redis):

   ```bash
   docker compose up --build
   ```

3. Open **http://localhost:8000/** (or the port you set with `WEB_HOST_PORT`, e.g. **http://localhost:8001/**).

If Gunicorn logs show **`WORKER TIMEOUT`** (default was 30s), the container now uses **`GUNICORN_TIMEOUT`** (default **120** in [`docker/entrypoint.sh`](docker/entrypoint.sh)). Raise it only if some views legitimately run longer; otherwise find the slow request or stuck client. **`(no URI read)`** after a timeout often means the client never finished sending the HTTP request (closed tab, bad proxy, or wrong URL/port).

Compose sets **`DATABASE_URL`** to the `db` service and **`REDIS_URL`** to the `redis` service. When `REDIS_URL` is set, Django uses **Redis** for the default cache and for **sessions** (shared across Gunicorn workers). If you unset `REDIS_URL`, Django falls back to in-memory cache and database sessions.

### Port 8000 already in use

If you see `Bind for 0.0.0.0:8000 failed: port is already allocated`, something else is using **8000** (often `python manage.py runserver`). Either stop that process or map the app to another host port:

```bash
WEB_HOST_PORT=8001 docker compose up --build
```

Then use **http://localhost:8001/**. Add the same origin to **`CSRF_TRUSTED_ORIGINS`** in `.env` (e.g. `http://localhost:8001`) so POST forms and login work.

You can set **`WEB_HOST_PORT`** in your `.env` file next to the other variables (see [`.env.example`](.env.example)). The **`web`** service always listens on port **8000 inside the container** (Compose sets `PORT=8000` there). Only **`WEB_HOST_PORT`** changes the port on your Mac; if `PORT` in `.env` pointed Gunicorn at another port inside the container, the browser would hit “connection reset” because Docker still forwarded to **8000**.

**Static files:** Gunicorn does not serve `/static/` by itself. The container runs **`collectstatic`** on each start ([`docker/entrypoint.sh`](docker/entrypoint.sh)), and **[WhiteNoise](https://whitenoise.readthedocs.io/)** middleware in [`project/settings.py`](project/settings.py) serves the Django admin CSS and JS from `STATIC_ROOT`. Migrations run in the same entrypoint before Gunicorn starts.

If the admin login page looks unstyled, open **`http://127.0.0.1:<WEB_HOST_PORT>/static/admin/css/base.css`** (same host and port as the admin page). You should see raw CSS, not a Django “Page not found” HTML page. If you see HTML, rebuild the web image (`docker compose build --no-cache web`) and recreate the container (`docker compose up -d web`), then hard-refresh the browser (cache can hold old 404s). Run **`docker compose down --remove-orphans`** if you ever used `docker compose run web …` without `--entrypoint` — that can leave extra `web-run-*` containers running.

## First-time admin user

With the stack already up (`docker compose up -d`):

```bash
docker compose exec web python manage.py createsuperuser
```

For a one-off container (no Gunicorn), override the entrypoint:

```bash
docker compose run --rm --no-deps --entrypoint python web manage.py createsuperuser
```

Then visit **http://localhost:8000/admin/** (or your `WEB_HOST_PORT`).

## Data volumes

| Volume           | Purpose                                      |
|-----------------|----------------------------------------------|
| `postgres_data` | PostgreSQL data (persists across restarts) |
| `redis_data`    | Redis AOF data (sessions/cache survive redis container recreation) |
| `media_data`    | User uploads (`MEDIA_ROOT` → `/app/media`) |

Uploaded files survive `docker compose down`; they are removed only if you delete the volume (e.g. `docker volume rm marketinghub_media_data` — names may include project prefix).

## Local development without Docker

Leave `DATABASE_URL` unset (or remove it from `.env`). Django falls back to **SQLite** at `db.sqlite3` (see [`project/settings.py`](project/settings.py)). Omit **`REDIS_URL`** to use local memory cache and database-backed sessions; for local Redis, set e.g. `REDIS_URL=redis://127.0.0.1:6379/0`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Production notes

- Set **`SECRET_KEY`**, **`DEBUG=False`**, and tight **`ALLOWED_HOSTS`** / **`CSRF_TRUSTED_ORIGINS`** via environment.
- Change the default Postgres user/password in [`docker-compose.yml`](docker-compose.yml) (or use secrets) before any real deployment.
- **`DATABASE_SSL_REQUIRE`**: set to `true` if your database URL points at a host that requires TLS.

## Static files

Static assets are collected into `/app/staticfiles` in the image and refreshed on container start. A separate static volume is not mounted by default; add one only if you need writable static storage and keep `collectstatic` in the entrypoint.
