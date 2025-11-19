"""Progress monitoring utilities for scripts."""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def log_step(step_name: str, message: str) -> None:
    """
    Log a step in the process.
    
    Args:
        step_name: Name of the step
        message: Step message
    """
    logger.info(f"[{step_name}] {message}")


def log_success(message: str) -> None:
    """
    Log a success message.
    
    Args:
        message: Success message
    """
    logger.info(f"✓ {message}")


def log_error(message: str, error: Any = None) -> None:
    """
    Log an error message.
    
    Args:
        message: Error message
        error: Optional error object
    """
    if error:
        logger.error(f"✗ {message}: {error}")
    else:
        logger.error(f"✗ {message}")

