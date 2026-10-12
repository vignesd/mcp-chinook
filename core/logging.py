
import logging
import sys
from pathlib import Path

from core.config import PROJECT_ROOT, settings


def setup_logging() -> None:
    """Configure application logging once."""

    log_level = getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    )

    formatter = logging.Formatter(
        fmt=(
            "|%(asctime)s | %(levelname)s | "
            "%(filename)s:%(funcName)s:%(lineno)d | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid adding duplicate handlers if called more than once.
    if root_logger.handlers:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)
            handler.setLevel(log_level)
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

    if settings.log_to_file:
        log_path = Path(settings.log_file)

        if not log_path.is_absolute():
            log_path = PROJECT_ROOT / log_path

        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Prevent duplicate file handlers on repeated initialization.
        resolved_path = log_path.resolve()
        has_file_handler = any(
            isinstance(handler, logging.FileHandler)
            and Path(handler.baseFilename).resolve() == resolved_path
            for handler in root_logger.handlers
        )

        if not has_file_handler:
            file_handler = logging.FileHandler(
                resolved_path,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)

    # Keep routine SQLAlchemy engine logs under control.
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING
        if not settings.sqlalchemy_echo
        else log_level
    )


setup_logging()

logger = logging.getLogger("chinook-mcp-server")
