# SQL Agents

This repository contains two separate SQL agent implementations using LangChain:

- **SQLite agent** (in `sql-agents/`): uses a local `Chinook.db` SQLite database.
- **PostgreSQL agent** (in `sql-agents-postgres/`): uses a PostgreSQL database via `POSTGRES_DATABASE_URL`.

Each agent has its own `src/` folder and runs independently so you can keep both setups in the same repo without code conflicts.

## Getting Started

### 1) Install dependencies

This project uses a shared Python environment defined by `pyproject.toml`.

```sh
uv install
```

### 2) Run the SQLite agent

```sh
uv run sql-agents\src\app.py
```

### 3) Run the PostgreSQL agent

Make sure `.env` contains a valid `POSTGRES_DATABASE_URL`.

```sh
uv run sql-agents-postgres\src\app.py
```
