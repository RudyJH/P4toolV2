# P4toolV2 documentation

P4toolV2 is the cleaned successor to P4toolDev2 and V1. It uses the V1
FastAPI/SQLAlchemy application as its base and keeps the project documentation,
database setup notes, migrations, scripts, and splash-page assets in one
repository.

The application entry point is `app/main.py`. Configuration is loaded from
`.env` using `app/core/config.py`; copy `.env.example` before running locally.
The default development mode (`DB_INIT=0`) does not require PostgreSQL.

For installation and endpoint information, see [README.md](README.md).
