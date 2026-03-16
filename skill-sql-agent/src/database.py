"""PostgreSQL database connection for the SQL agent.

This module is intentionally separate from the sqlite agent implementation so
that the sqlite code can remain unchanged.
"""

import os

from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase

# Load environment variables (reuses the same .env file in the repo root)
load_dotenv()

# Postgres connection string expected in the .env file.
# Example: POSTGRES_DATABASE_URL=postgresql://user:pass@host:port/dbname
POSTGRES_DATABASE_URL: str | None = os.getenv("POSTGRES_DATABASE_URL")

if not POSTGRES_DATABASE_URL:
    raise ValueError(
        "POSTGRES_DATABASE_URL is not set. Please set it in your .env file."
    )

# Initialize database
try:
    db: SQLDatabase = SQLDatabase.from_uri(database_uri=POSTGRES_DATABASE_URL)
except ImportError as exc:
    raise ImportError(
        "PostgreSQL driver not installed. Install one of: psycopg[binary], psycopg2-binary, or asyncpg. "
        "For example: pip install psycopg[binary]"
    ) from exc
