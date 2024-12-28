"""
bluesky_nexus_paths.py

This module provides utility functions for retrieving NeXus-related directory paths
and other configuration paths (e.g., log file path) from environment variables. These paths
are essential for configuring the locations of NeXus files, schema definitions, and logs
in a containerized or environment-variable-driven setup.

Functions:
    get_nx_file_dir_path():
        Retrieves the directory path for storing NeXus files from the `_NX_FILE_DIR_PATH`
        environment variable. Raises an error if the variable is not set.

    get_nx_schema_dir_path():
        Retrieves the directory path for NeXus schema files from the `_NX_SCHEMA_DIR_PATH`
        environment variable. Raises an error if the variable is not set.

    get_log_file_path():
        Retrieves the log file path from the `_LOG_FILE_PATH` environment variable.
        Raises an error if the variable is not set.

Usage:
    This module is designed to be imported into other scripts or modules where NeXus
    file paths, schema paths, or log file paths need to be dynamically resolved from
    environment variables. Ensure that the relevant environment variables are set in the
    system configuration (e.g., `~/etc/environment`) before using these functions.

Example:
    from bluesky_nexus_paths import get_nx_file_dir_path, get_nx_schema_dir_path, get_log_file_path

    nexus_file_dir = get_nx_file_dir_path()
    nexus_schema_dir = get_nx_schema_dir_path()
    log_file_path = get_log_file_path()

Environment Variables:
    - `_NX_FILE_DIR_PATH`: The path to the directory where NeXus files will be stored.
    - `_NX_SCHEMA_DIR_PATH`: The path to the directory where NeXus schema files are located.
    - `_LOG_FILE_PATH`: The path to the log file used by the application.

Notes:
    - If the required environment variables are not set, the functions will raise a
      `ValueError` with a descriptive message.
    - This module is particularly suited for containerized environments where
      configuration is managed via environment variables.
"""

import os

from bluesky_nexus.common.logging_utils import logger


def get_nx_file_dir_path():
    """
    Retrieve the NeXus file directory path from the environment variable.

    This function checks the environment variable `_NX_FILE_DIR_PATH` to determine
    the directory path where NeXus files are to be stored. If the variable is not set,
    a `ValueError` is raised.

    Returns:
        str: The NeXus file directory path.

    Raises:
        ValueError: If the `_NX_FILE_DIR_PATH` environment variable is not defined.

    Notes:
        - The `_NX_FILE_DIR_PATH` variable must be set in the environment configuration file
          (e.g., `~/etc/environment`) for this function to work correctly.
        - This function is designed to be used in containerized environments where
          paths are configured via environment variables.
    """

    # Extract from env variable nexus file dir path (in container)
    _NX_FILE_DIR_PATH = os.environ.get("_NX_FILE_DIR_PATH")
    if _NX_FILE_DIR_PATH is None:
        logger.error(
            "Environment variable '_NX_FILE_DIR_PATH' is not set. Unable to retrieve NeXus file directory path."
        )
        raise ValueError(
            "_NX_FILE_DIR_PATH is None. Check content of ~/etc/environment."
        )
    logger.debug(f"Retrieved NeXus file directory path: {_NX_FILE_DIR_PATH}")
    return _NX_FILE_DIR_PATH


def get_nx_schema_dir_path():
    """
    Retrieve the NeXus schema directory path from the environment variable.

    This function checks the environment variable `_NX_SCHEMA_DIR_PATH` to determine
    the directory path where NeXus schema files are stored. If the variable is not set,
    a `ValueError` is raised.

    Returns:
        str: The NeXus schema directory path.

    Raises:
        ValueError: If the `_NX_SCHEMA_DIR_PATH` environment variable is not defined.

    Notes:
        - The `_NX_SCHEMA_DIR_PATH` variable must be set in the environment configuration file
          (e.g., `~/etc/environment`) for this function to work correctly.
        - This function is designed to be used in containerized environments where
          paths are configured via environment variables.
    """

    # Extract from env variable nexus schema file dir path (in container)
    _NX_SCHEMA_DIR_PATH = os.environ.get("_NX_SCHEMA_DIR_PATH")
    if _NX_SCHEMA_DIR_PATH is None:
        logger.error(
            "Environment variable '_NX_SCHEMA_DIR_PATH' is not set. Unable to retrieve NeXus schema directory path."
        )
        raise ValueError(
            "_NX_SCHEMA_DIR_PATH is None. Check content of ~/etc/environment."
        )
    logger.debug(f"Retrieved NeXus schema directory path: {_NX_SCHEMA_DIR_PATH}")
    return _NX_SCHEMA_DIR_PATH


def get_log_file_path():
    """
    Retrieve the log file path from the environment variable.

    This function checks the environment variable `_LOG_FILE_PATH` to determine
    the path to the application's log file. If the variable is not set, a `ValueError`
    is raised.

    Returns:
        str: The log file path.

    Raises:
        ValueError: If the `_LOG_FILE_PATH` environment variable is not defined.

    Notes:
        - The `_LOG_FILE_PATH` variable must be set in the environment configuration file
          (e.g., `~/etc/environment`) for this function to work correctly.
        - This function is designed for environments where paths are configured
          via environment variables, such as containerized setups.
    """

    # Extract from env variable log file path (in container)
    _LOG_FILE_PATH = os.environ.get("_LOG_FILE_PATH")
    if _LOG_FILE_PATH is None:
        logger.error(
            "Environment variable '_LOG_FILE_PATH' is not set. Unable to retrieve log file path."
        )
        raise ValueError("_LOG_FILE_PATH is None. Check content of ~/etc/environment.")
    logger.debug(f"Retrieved log file path: {_LOG_FILE_PATH}")
    return _LOG_FILE_PATH
