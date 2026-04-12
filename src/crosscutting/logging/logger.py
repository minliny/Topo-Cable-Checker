"""
P0-4: Enhanced Logger with File Handler + Rotation

Features:
- RotatingFileHandler: writes to logs/app.log
- Max file size: 5MB, keeps 3 backup files
- Dual output: console (StreamHandler) + file (RotatingFileHandler)
- Format includes timestamp, logger name, level, and message
- Lazy initialization: log directory created on first use
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from src.crosscutting.config.settings import settings

LOG_DIR = os.path.join(settings.BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
MAX_BYTES = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with both console and rotating file handlers.
    
    - Console handler: INFO level, for real-time monitoring
    - File handler: INFO level, for persistent audit trail
    - Rotation: 5MB per file, keeps 3 backups (total ~20MB max)
    """
    logger = logging.getLogger(name)
    
    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, still keep console logging working
        logger.warning(f"Failed to set up file logging: {e}. Console-only mode.")

    return logger
