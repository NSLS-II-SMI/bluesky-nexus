"""Module: bluesky_nexus_def

This module is responsible for retrieving directory paths related to Nexus files and schemas from environment variables.
It ensures that the necessary paths are available in the environment by extracting them from the system's environment variables
and raising an error if they are missing.

Directory Paths:
    _NX_FILE_DIR_PATH:          Extracted from the environment variable _NX_FILE_DIR_PATH, this variable stores the path to the Nexus file directory.
                                If the environment variable is not set, a ValueError is raised with a message indicating that the content
                                of the ~/.bluesky_config file should be checked.

    _NX_SCHEMA_DIR_PATH:   Extracted from the environment variable _NX_SCHEMA_DIR_PATH, this variable stores the path to
                                the Nexus schema file directory. If the environment variable is not set, a ValueError is raised with a message indicating
                                that the content of the ~/.bluesky_config file should be checked.

Error Handling:
    If either of the required environment variables is missing, a ValueError is raised with an appropriate message to guide the user in configuring their environment.
"""

import os

# -------------------------------- DIR PATHS  --------------------------------
# Extract from env variable nexus file dir path (in container)
_NX_FILE_DIR_PATH = os.environ.get("_NX_FILE_DIR_PATH")
if _NX_FILE_DIR_PATH is None:
    raise ValueError("_NX_FILE_DIR_PATH is None. Check content of ~/etc/environment.")

# Extract from env variable nexus schema file dir path (in container)
_NX_SCHEMA_DIR_PATH = os.environ.get("_NX_SCHEMA_DIR_PATH")
if _NX_SCHEMA_DIR_PATH is None:
    raise ValueError("_NX_SCHEMA_DIR_PATH is None. Check content of ~/etc/environment.")
# -------------------------------- END OF DIR PATHS  --------------------------------
