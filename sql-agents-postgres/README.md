# PostgreSQL SQL Agent

This directory contains a LangChain-based AI agent that queries a PostgreSQL database.

## Setup

Dependencies are shared via the root `pyproject.toml` and the same `.venv`.

```sh
uv sync
```

### Configure PostgreSQL connection

Rename `.env.example` to `.env` and edit the `POSTGRES_DATABASE_URL` value.

Set the connection string in the root `.env` file:

```env
POSTGRES_DATABASE_URL=postgresql://<user>:<pass>@<host>:<port>/<dbname>
```

## Run

```sh
uv run sql-agents-postgres\src\app.py
```

## Notes

- If you see an import error about Postgres drivers, install `psycopg2-binary`:

```sh
uv add psycopg2-binary

```
