# P4toolV2

PPPProfile is a FastAPI application for managing public-policy and personality
profile data. This repository combines the P4toolDev2 project documentation
with the working V1 application foundation.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The splash page is available at <http://localhost:8000/> and the interactive
API documentation is at <http://localhost:8000/docs>.

## Database modes

The default `DB_INIT=0` mode starts the splash page and health endpoint without
connecting to a database. Set `DB_INIT=1` and configure `DATABASE_URL` in
`.env` to enable the user CRUD routes and automatic development-time table
creation. PostgreSQL is the supported database for CRUD mode.

See [POSTGRES_SETUP.md](POSTGRES_SETUP.md) for database setup details.

## Project layout

- `app/` - FastAPI application, database layer, routes, models, and schemas
- `migrations/` - SQL migration scripts
- `static/` and `templates/` - splash page assets
- `tests/` - API tests
- `scripts/` - local setup and database utility scripts
