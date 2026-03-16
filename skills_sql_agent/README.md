# Skills SQL Agent

This directory contains a LangChain-based AI agent that queries a PostgreSQL database using skills.

## Setup

Dependencies are shared via the root `pyproject.toml` and the same `.venv`.

```sh
uv sync
```

## Run

```sh
uv run sqlite_sql_agent\src\app.py
```

## Notes

- This agent uses the same `POSTGRES_DATABASE_URL` as the PostgreSQL agent.
- It demonstrates how to use skills to provide database schema and business logic to the agent.
- Skills are defined in the `skills/` directory and loaded dynamically by the agent.
- The `skill.py` module defines the `SkillMiddleware` class that injects the skills into the agent's system prompt.
- The `skill.md` files in each skill directory contain the skill content that is loaded by the agent.
