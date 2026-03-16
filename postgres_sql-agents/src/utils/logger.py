"""Logging configuration module for the PostgreSQL agent application.

This is intentionally copied from the sqlite agent app so the two can
coexist without modifying the original codebase.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class SqlAgentLog:
    """Logger class for RAG applications with file and console output."""

    _instance: Optional[logging.Logger] = None

    @staticmethod
    def setup(module_name: str) -> logging.Logger:
        """Configure and return a logger instance with both file and console handlers.

        Args:
            module_name: Name of the module requesting the logger

        Returns:
            logging.Logger: Configured logger instance
        """
        if SqlAgentLog._instance is not None:
            return SqlAgentLog._instance

        # Create logs directory
        current_dir: Path = Path(__file__).parent.parent.parent.resolve()
        logs_dir: Path = current_dir / "logs"
        logs_dir.mkdir(exist_ok=True)

        # Configure log file
        log_file: Path = logs_dir / "postgres_sql_agent.log"

        # Create and configure logger
        logger: logging.Logger = logging.getLogger(name=module_name)
        logger.setLevel(level=logging.INFO)

        # Create formatters and handlers
        formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
        )

        # Rotating file handler
        file_handler: RotatingFileHandler = RotatingFileHandler(
            filename=log_file,
            maxBytes=10_000_000,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(fmt=formatter)

        # Console handler
        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setFormatter(fmt=formatter)

        # Add handlers to logger
        logger.addHandler(hdlr=file_handler)
        logger.addHandler(hdlr=console_handler)

        # Store instance
        SqlAgentLog._instance = logger

        return logger

    @staticmethod
    def get_logger(module_name: str) -> logging.Logger:
        """Get or create a logger instance.

        Args:
            module_name: Name of the module requesting the logger

        Returns:
            logging.Logger: Configured logger instance
        """
        if SqlAgentLog._instance is None:
            return SqlAgentLog.setup(module_name=module_name)
        return SqlAgentLog._instance
