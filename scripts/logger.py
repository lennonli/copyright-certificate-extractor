#!/usr/bin/env python3
"""
Centralized logging configuration for copyright certificate extractor.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console: Whether to output to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Format for log messages
    console_format = '%(levelname)s | %(name)s | %(message)s'
    file_format = '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'

    # Console handler with colors
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(ColoredFormatter(console_format))
        logger.addHandler(console_handler)

    # File handler (no colors)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(logging.Formatter(file_format))
        logger.addHandler(file_handler)

    return logger


def get_default_log_file() -> Path:
    """Get default log file path."""
    log_dir = Path.home() / '.copyright_extractor' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return log_dir / f'extractor_{timestamp}.log'


# Create default logger
default_logger = setup_logger('copyright_extractor', level=logging.INFO)


class ExtractionError(Exception):
    """Base exception for extraction errors."""
    pass


class OCRError(ExtractionError):
    """Exception raised when OCR fails."""
    pass


class ParsingError(ExtractionError):
    """Exception raised when parsing fails."""
    pass


class ValidationError(ExtractionError):
    """Exception raised when validation fails."""
    pass


class DependencyError(ExtractionError):
    """Exception raised when required dependencies are missing."""
    pass
