"""Logging utility for Healthcare AI."""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get configured logger instance."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Set level
        logger.setLevel(getattr(logging, level.upper()))
        
        # File handler
        file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


class LoggerMixin:
    """Mixin to add logging capability to classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger