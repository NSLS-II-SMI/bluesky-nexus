"""Module bluesky_nexus_const

This module defines a collection of constants used throughout the application. These constants serve as predefined values that facilitate the operation of the system, ensuring consistency and reducing the likelihood of errors due to hard-coded values. The constants in this module are primarily related to Nexus data files, metadata, device schemas, and other configuration-related information used in the system.

Constants:

    NOT_AVAILABLE_LABEL (str): Label representing unavailable data ("NotAvailable").
    PRE_RUN_CPT_LABEL (str): Label for pre-run component placeholders ("$pre-run-cpt").
    PRE_RUN_MD_LABEL (str): Label for pre-run metadata placeholders ("$pre-run-md").
    NX_MD_KEY (str): The key used for Nexus metadata ("nexus_md").
    DEVICE_MD_KEY (str): The key used for device metadata ("device_md").
    NX_FILE_EXTENSION (str): The file extension for Nexus files (".nxs").
    NX_SCHEMA_EXTENSIONS (list): List of valid file extensions for Nexus schema files ([".yml", ".yaml"]).
    NX_SCHEMA_MODEL_NAME_KEY (str): Key for the Nexus schema model name ("nx_model").
    DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME (str): Attribute name for the Nexus schema in the device class ("nx_schema").
    DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME (str): Attribute name for the Nexus model in the device instance ("nx_model").
    DEFAULT_NX_LOG_FORMAT (str): The default log format used by the logger.

Valid Data Types for Nexus Fields:

    VALID_NXFIELD_DTYPES (list): List of valid data types for Nexus fields, including numeric types (e.g., float32, int32), unsigned integers (e.g., uint8, uint16), and string types ("char", "str").
"""

NOT_AVAILABLE_LABEL: str = "NotAvailable"
PRE_RUN_CPT_LABEL: str = "$pre-run-cpt"
PRE_RUN_MD_LABEL: str = "$pre-run-md"

NX_MD_KEY: str = "nexus_md"
DEVICE_MD_KEY: str = "device_md"
NX_FILE_EXTENSION: str = ".nxs"
CALLBACK_FILE_EXTENSION: str = ".json"
NX_SCHEMA_EXTENSIONS = [".yml", ".yaml"]
NX_SCHEMA_MODEL_NAME_KEY: str = "nx_model"
DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME: str = "nx_schema"
DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME: str = "nx_model"
DEFAULT_NX_LOG_FORMAT: str = (
    "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s  %(message)s"
)

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
