# SQLite SQL Agent

This directory contains a LangChain-based AI agent that queries a local SQLite database (`Chinook.db`).

## Setup

Dependencies are shared via the root `pyproject.toml` and the same `.venv`.

```sh
uv sync
```

## Run

```sh
uv run sqlite_sql_agent\src\app.py
```

## What it does

- Downloads `Chinook.db` if missing.
- Creates a LangChain agent using `SQLDatabaseToolkit`.
- Prompts you for natural language questions.
- Executes generated SQL against the SQLite DB and prints the answer.
