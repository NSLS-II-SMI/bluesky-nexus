"""Module bluesky_nexus_const

This module defines a collection of constants used throughout the application. These constants serve as predefined values that facilitate the operation of the system, ensuring consistency and reducing the likelihood of errors due to hard-coded values. The constants in this module are primarily related to Nexus data files, metadata, device schemas, and other configuration-related information used in the system.

Constants:

    NOT_AVAILABLE_LABEL (str): Label representing unavailable data ("NotAvailable").
    PRE_RUN_CPT_LABEL (str): Label for pre-run component placeholders ($pre-run-cpt).
    PRE_RUN_MD_LABEL (str): Label for pre-run metadata placeholders ($pre-run-md).
    NX_MD_KEY (str): The key used for Nexus metadata ("nexus_md").
    NX_FILE_EXTENSION (str): The file extension for Nexus files (".nxs").
    NX_SCHEMA_FILE_EXTENSIONS (list): List of valid file extensions for Nexus schema files (".yml", ".yaml").
    NX_SCHEMA_MODEL_NAME_KEY (str): Key for the Nexus schema model name ("nx_model").
    DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME (str): Attribute name for the Nexus schema in the device class ("nx_schema").
    DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME (str): Attribute name for the Nexus model in the device instance ("nx_model").
    TIME_ZONE (str): Default time zone used in the application ("Europe/Berlin").

Valid Data Types for Nexus Fields:

    VALID_NXFIELD_DTYPES (list): List of valid data types for Nexus fields, including numeric types (e.g., float32, int32) and string types ("char", "str").
"""

# ----------------------- CONSTANTS -----------------------
NOT_AVAILABLE_LABEL: str = "NotAvailable"
PRE_RUN_CPT_LABEL: str = "$pre-run-cpt"
PRE_RUN_MD_LABEL: str = "$pre-run-md"

NX_MD_KEY: str = "nexus_md"
NX_FILE_EXTENSION: str = ".nxs"
NX_SCHEMA_FILE_EXTENSIONS = [".yml", ".yaml"]
NX_SCHEMA_MODEL_NAME_KEY: str = "nx_model"
DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME: str = "nx_schema"
DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME: str = "nx_model"

TIME_ZONE: str = "Europe/Berlin"


VALID_NXFIELD_DTYPES = [
    "float32",
    "float64",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "char",
    "str",
]

# ----------------------- End of CONSTANTS ----------------
