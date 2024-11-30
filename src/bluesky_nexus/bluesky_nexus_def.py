"""Definitions

DIR PATHS
------
    Matched to a directory tree structure of the machine (docker container)
    letting run this application:

        _NX_FILE_DIR_PATH : str
        _NX_SCHEMA_FILE_DIR_PATH : str
"""

import os

# ------------------------------------------------- DIR PATHS  --------------------------------
# Extract from env variable nexus file dir path (in container)
_NX_FILE_DIR_PATH = os.environ.get("_NX_FILE_DIR_PATH")
if _NX_FILE_DIR_PATH is None:
    raise ValueError(
        "_NX_FILE_DIR_PATH is None. Check content of ~/.bluesky_config file."
    )

# Extract from env variable nexus schema file dir path (in container)
_NX_SCHEMA_FILE_DIR_PATH = os.environ.get("_NX_SCHEMA_FILE_DIR_PATH")
if _NX_SCHEMA_FILE_DIR_PATH is None:
    raise ValueError(
        "_NX_SCHEMA_FILE_DIR_PATH is None. Check content of ~/.bluesky_config file."
    )
# ------------------------------------------------- END OF DIR PATHS  --------------------------------
