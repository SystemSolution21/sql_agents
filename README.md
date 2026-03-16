# SQL Agents

This project contains three separate SQL agent implementations using LangChain:

- **SQLite agent** (in `sqlite_sql_agent/`): uses a local `Chinook.db` SQLite database.
- **PostgreSQL agent** (in `postgres_sql_agent/`): uses a PostgreSQL database via `POSTGRES_DATABASE_URL`.
- **Skills agent** (in `skills_sql_agent/`): uses a PostgreSQL database via `POSTGRES_DATABASE_URL` and demonstrates skill-based interaction.

Each agent has its own `src/` folder and runs independently so you can keep both setups in the same repo without code conflicts.

## Getting Started

### 1) Install dependencies

This project uses a shared Python environment defined by `pyproject.toml`.

```sh
uv sync
```

### 2) Run the SQLite agent

```sh
uv run sqlite_sql_agent\src\app.py
```

### 3) Run the PostgreSQL agent

Make sure `.env` contains a valid `POSTGRES_DATABASE_URL`.

```sh
uv run postgres_sql_agent\src\app.py
```

### 4) Run the Skills agent

```sh
uv run skills_sql_agent\src\app.py
```
