"""
logging_utils.py

This module provides utilities for setting up and managing logging for the `bluesky_nexus` package.
It supports both console-based logging and file-based logging with automatic log rotation.
The module is designed to simplify logging configuration and ensure robust log management
in both development and production environments.

Features:
    - A pre-configured logger (`bluesky_nexus`) with a default `NullHandler` to prevent accidental log output.
    - The `setup_nx_logger` function to configure logging with:
        - Customizable logging levels.
        - Console and file logging.
        - Automatic file naming and log rotation for file-based logging.
    - The `remove_all_handlers` function to clean up existing logger handlers.

File-based Logging:
    - Log files are created in a specified directory.
    - Filenames are automatically generated based on timestamps (e.g., `log_20241228_103045.log`).
    - Log rotation is handled automatically when files exceed a specified size.
    - A fixed number of backup log files are retained to manage storage efficiently.

Usage:
    Import the module and use the `setup_nx_logger` function to configure the logging for the application.
    Use the `logger` instance to log messages throughout your codebase.

Example:
    >>> from logging_utils import setup_nx_logger, logger
    >>> setup_nx_logger(level=logging.INFO, log_file_dir_path="/var/log/bluesky")
    >>> logger.info("Application started.")
    >>> logger.debug("Debug information logged.")

Attributes:
    logger_name (str): The name of the logger for the package (`"bluesky_nexus"`).
    logger (logging.Logger): The logger instance for the package, pre-configured with a `NullHandler`.

Functions:
    setup_nx_logger(level=logging.DEBUG, log_file_dir_path=None, log_format=None, max_file_size=10 * 1024 * 1024, backup_count=5) -> None:
        Configures the logger for the package, setting up console and file-based logging with rotation.

    remove_all_handlers(logger: logging.Logger) -> None:
        Removes all handlers from the given logger to avoid duplicate or conflicting outputs.

Notes:
    - The default log format can be customized via the `log_format` parameter in `setup_nx_logger`.
    - Ensure that the specified log directory (`log_file_dir_path`) exists or can be created by the application.
    - Rotating file logs helps prevent log files from growing too large and consuming excessive disk space.

This module is suitable for applications running in containerized environments, local development, or production setups where log management is crucial.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from bluesky_nexus.bluesky_nexus_const import DEFAULT_NX_LOG_FORMAT

# Create a custom logger for the package
logger_name: str = "bluesky_nexus"
logger: logging.Logger = logging.getLogger(logger_name)
logger.addHandler(logging.NullHandler())  # Add a NullHandler by default


def setup_nx_logger(
    level=logging.DEBUG,
    log_file_dir_path=None,
    log_format=None,
    max_file_size=10 * 1024 * 1024,
    backup_count=5,
) -> None:
    """
    Configures the logger for the package, setting up handlers for console and optional file logging with rotation.

    Parameters:
        level (int, optional): The logging level for the logger. Defaults to `logging.DEBUG`.
        log_file_dir_path (str, optional): Directory path where log files will be stored. Defaults to None (no file logging).
        log_format (str, optional): Format for log messages. Defaults to DEFAULT_NX_LOG_FORMAT.
        max_file_size (int, optional): Maximum size of a log file in bytes before rotation occurs. Defaults to 10 MB.
        backup_count (int, optional): Number of backup log files to keep. Defaults to 5.

    Returns:
        None
    """
    log_format: str = log_format or DEFAULT_NX_LOG_FORMAT
    formatter = logging.Formatter(log_format)

    # Set logger's level
    logger.setLevel(level)

    # Remove all existing handlers before configuring new handlers
    remove_all_handlers(logger)

    # Configure file logging if log_file_dir_path is provided
    if log_file_dir_path:
        # Ensure the directory exists
        os.makedirs(log_file_dir_path, exist_ok=True)

        # Use a consistent log file name
        log_file_path = os.path.join(log_file_dir_path, "nx_log.log")

        # Create a RotatingFileHandler for log rotation
        file_handler = RotatingFileHandler(
            log_file_path,
            mode="a",
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Configure console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Setup logger complete.")


def remove_all_handlers(logger: logging.Logger) -> None:
    """
    Removes all handlers from the given logger.

    This function iterates over all handlers currently attached to the specified logger and removes them.
    It is particularly useful when reconfiguring a logger to avoid duplicate logging outputs.

    Parameters:
        logger (logging.Logger): The logger from which to remove all handlers.

    Returns:
        None

    Example:
    >>> from logging_utils import logger, remove_all_handlers
    >>> remove_all_handlers(logger)
    >>> # Now the logger has no handlers.
    """
    for handler in logger.handlers[
        :
    ]:  # Use a copy of the handlers list to avoid modification during iteration
        logger.removeHandler(handler)
        handler.close()  # Close the handler to release any associated resources
