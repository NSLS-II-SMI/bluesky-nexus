"""Constants
------

"""

# ------------------------------------------------- CONSTANTS -----------------------
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

# ------------------------------------------------- End of CONSTANTS ----------------
