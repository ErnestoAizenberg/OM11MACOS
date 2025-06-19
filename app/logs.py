import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Dict, Any

# Color codes
COLORS: Dict[str, str] = {
    "RESET": "\x1b[0m",
    "BLACK": "\x1b[30m",
    "RED": "\x1b[31m",
    "GREEN": "\x1b[32m",
    "YELLOW": "\x1b[33m",
    "BLUE": "\x1b[34m",
    "MAGENTA": "\x1b[35m",
    "CYAN": "\x1b[36m",
    "WHITE": "\x1b[37m",
}

LOG_LEVEL_COLORS: Dict[str, str] = {
    "DEBUG": COLORS["BLUE"],
    "INFO": COLORS["GREEN"],
    "WARNING": COLORS["YELLOW"],
    "ERROR": COLORS["RED"],
    "CRITICAL": COLORS["MAGENTA"],
}


class ColoredFormatter(logging.Formatter):
    """Enhanced log formatter with colors and additional context information."""
    
    def __init__(self, fmt: str, datefmt: str = None):
        super().__init__(fmt, datefmt)
        self._fmt = fmt
        
    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record with colors."""
        color = LOG_LEVEL_COLORS.get(record.levelname, COLORS["RESET"])
        record.levelname = f"{color}{record.levelname}{COLORS['RESET']}"
        record.msg = f"{color}{record.msg}{COLORS['RESET']}"
        
        # Include filename and line number for debug purposes
        if record.levelno >= logging.WARNING:
            record.msg = f"{record.msg} | {record.filename}:{record.lineno}"
            
        return super().format(record)


def setup_logger(
    name: str = __name__,
    level: int = logging.DEBUG,
    log_file: str = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """Configure and return a logger with enhanced features.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Path to log file (optional)
        max_bytes: Max log file size before rotation
        backup_count: Number of backup logs to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation if log file is specified
    if log_file:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

logger = setup_logger(log_file="app.log")

# Example usage
if __name__ == "__main__":
    logger = setup_logger(log_file="app.log")
    
    logger.debug("Debug message for detailed information")
    logger.info("System is running normally")
    logger.warning("Potential issue detected")
    logger.error("Failed to process request", extra={"user_id": 123})
    logger.critical("System crash imminent!")
    
    try:
        1 / 0
    except Exception as e:
        logger.exception("An error occurred: %s", str(e))