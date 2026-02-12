"""
Logging configuration for GAFreqTrade.

Provides structured logging with file rotation and console output.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class GALogger:
    """Custom logger for GAFreqTrade with file and console output."""
    
    def __init__(
        self,
        name: str = "GAFreqTrade",
        log_dir: str = "logs",
        log_file: Optional[str] = None,
        level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            log_file: Log file name (auto-generated if None)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate log file name if not provided
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"evolution_{timestamp}.log"
        
        self.log_file = self.log_dir / log_file
        self.level = getattr(logging, level.upper())
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def get_logger(self) -> logging.Logger:
        """Get the logger instance."""
        return self.logger
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, *args, **kwargs)


# Global logger instance
_global_logger: Optional[GALogger] = None


def setup_logger(
    name: str = "GAFreqTrade",
    log_dir: str = "logs",
    log_file: Optional[str] = None,
    level: str = "INFO"
) -> GALogger:
    """
    Setup and return global logger instance.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        log_file: Log file name
        level: Logging level
        
    Returns:
        GALogger instance
    """
    global _global_logger
    _global_logger = GALogger(name, log_dir, log_file, level)
    return _global_logger


def get_logger() -> logging.Logger:
    """
    Get global logger instance.
    
    Returns:
        Logger instance
        
    Raises:
        RuntimeError: If logger not initialized
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logger()
    return _global_logger.logger


if __name__ == "__main__":
    # Test logger
    logger = setup_logger(level="DEBUG")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    try:
        1 / 0
    except Exception:
        logger.exception("This is an exception message")
    
    print(f"\nLog file created at: {logger.log_file}")
