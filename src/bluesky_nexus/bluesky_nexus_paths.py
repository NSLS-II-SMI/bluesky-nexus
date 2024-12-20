"""
bluesky_nexus_paths.py

This module provides utility functions for retrieving NeXus-related directory paths
from environment variables. These paths are essential for configuring the locations
of NeXus files and schema definitions in a containerized or environment-variable-driven
setup.

Functions:
    get_nx_file_dir_path():
        Retrieves the directory path for storing NeXus files from the `_NX_FILE_DIR_PATH`
        environment variable. Raises an error if the variable is not set.

    get_nx_schema_dir_path():
        Retrieves the directory path for NeXus schema files from the `_NX_SCHEMA_DIR_PATH`
        environment variable. Raises an error if the variable is not set.

Usage:
    This module is designed to be imported into other scripts or modules where NeXus
    file and schema paths need to be dynamically resolved from environment variables.
    Ensure that the relevant environment variables are set in the system configuration
    (e.g., `~/etc/environment`) before using these functions.

Example:
    from bluesky_nexus_paths import get_nx_file_dir_path, get_nx_schema_dir_path

    nexus_file_dir = get_nx_file_dir_path()
    nexus_schema_dir = get_nx_schema_dir_path()

Environment Variables:
    - `_NX_FILE_DIR_PATH`: The path to the directory where NeXus files will be stored.
    - `_NX_SCHEMA_DIR_PATH`: The path to the directory where NeXus schema files are located.

Notes:
    - If the required environment variables are not set, the functions will raise a
      `ValueError` with a descriptive message.
    - This module is particularly suited for containerized environments where
      configuration is managed via environment variables.
"""

import os


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
        raise ValueError(
            "_NX_FILE_DIR_PATH is None. Check content of ~/etc/environment."
        )
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
        raise ValueError(
            "_NX_SCHEMA_DIR_PATH is None. Check content of ~/etc/environment."
        )
    return _NX_SCHEMA_DIR_PATH
