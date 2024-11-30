"""Module:  bluesky_nexus_device_model
Module for:
- instantiation of the pydantic model
- assignment of the pydantic model to the 'nx_model' attribute of a device instance
"""

import os

from bluesky_nexus.bluesky_nexus_const import (
    DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME,
    DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME,
    NX_SCHEMA_FILE_EXTENSIONS,
    NX_SCHEMA_MODEL_NAME_KEY,
)
from bluesky_nexus.bluesky_nexus_def import _NX_SCHEMA_FILE_DIR_PATH
from bluesky_nexus.common.yaml_utils import read_yaml
from bluesky_nexus.models.nexusformat_models_hzb import *


def assign_pydantic_model_instance(devices_dictionary: dict):
    """
    For each device in devices_dictionary assign a pydantic model instance
    """

    for dev_instance in devices_dictionary.values():
        # Each device instance has a schema name that is assigned to it as a attribute 'nx_schema'
        schema_name = read_attribute(
            dev_instance, DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME
        )
        if schema_name is None:
            raise ValueError(
                f"Unknown schema name for the device: {dev_instance.name}. Check its class definition."
            )

        # Define schema file path
        if any(schema_name.endswith(ext) for ext in NX_SCHEMA_FILE_EXTENSIONS):
            file_path: str = os.path.join(_NX_SCHEMA_FILE_DIR_PATH, schema_name)
        else:
            file_path: str = os.path.join(
                _NX_SCHEMA_FILE_DIR_PATH, schema_name + NX_SCHEMA_FILE_EXTENSIONS[0]
            )

        # Read content of the schema file
        schema_content: dict = read_yaml(file_path)
        if schema_content is None:
            raise ValueError(
                "Read from pydantic schema file : {file_path} FAILED. Check the schema file content."
            )

        # Read model name from the schema content
        try:
            model_name = schema_content[NX_SCHEMA_MODEL_NAME_KEY]
        except KeyError:
            raise ValueError(
                f"The key: {NX_SCHEMA_MODEL_NAME_KEY} not found in a schema file: {file_path}"
            )

        # Create instance of the pydantic model
        model_instance: object = create_model_instance(model_name, schema_content)

        # Dynamically assign the attribute to the object
        setattr(dev_instance, DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME, model_instance)


def create_model_instance(model_name, schema_content) -> object:
    """
    Create a model instance based on the model_name and the content of the schema
    Return the model instance
    """

    # Check if the model_name corresponds to one of the classes in the mapping
    if model_name in MODEL_NAME_TO_CLASS_MAPPING:
        # Instantiate the model class.
        # **schema_content unpacks the dictionary schema_content and passes each key-value pair as keyword arguments to the constructor of the class.
        model_instance: object = MODEL_NAME_TO_CLASS_MAPPING[model_name](
            **schema_content
        )
        return model_instance
    else:
        raise ValueError(
            f"Class with name {model_name} not found in MODEL_NAME_TO_CLASS_MAPPING! Check the content of 'MODEL_NAME_TO_CLASS_MAPPING' in the file: 'bluesky_nexus.models.pydantic_models_hzb'"
        )


def read_attribute(device, attribute_name):
    """
    Reads the value of a specified attribute from a device instance.

    Parameters:
        device (object): The device instance.
        attribute_name (str): The name of the attribute to read.

    Returns:
        The value of the attribute if it exists, or None if the attribute does not exist.
    """
    try:
        # Attempt to retrieve the attribute's value
        value = getattr(device, attribute_name)
        return value
    except AttributeError as e:
        # Handle case where the attribute does not exist
        print(
            f"Error: Attribute '{attribute_name}' does not exist on the device {device.name}. Details: {e}"
        )
        return None
