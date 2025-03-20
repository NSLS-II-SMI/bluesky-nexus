"""Module: bluesky_nexus_device_model

This module is responsible for instantiating Pydantic models and assigning them to device instances within the Bluesky Nexus framework. The module facilitates the dynamic creation of Pydantic model instances based on schema files, and assigns the resulting model instances to the 'nx_model' attribute of device objects.

Functions:
    - assign_pydantic_model_instance(devices_dictionary: dict): For each device in the provided dictionary, this function assigns a Pydantic model instance based on the pydantic schema associated with the device.
    - create_model_instance(model_name: str, schema_content: dict) -> object: This function creates a Pydantic model instance based on the given model name and schema content associated with the device. The model is instantiated by mapping the model name to the appropriate Pydantic class and passing the schema content as initialization arguments.
    - read_attribute(device, attribute_name: str): This function retrieves the value of a specified attribute from a device instance. If the attribute does not exist, it returns None and logs an error message.

Modules and Constants:

    Imports various utilities, constants, and models related to the Nexus schema and device management, such as DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME, and Pydantic models.

Error Handling:

    Raises ValueError for missing or invalid schema files, missing keys in the schema, or unrecognized model names in the schema content.
"""

import os

from bluesky_nexus.bluesky_nexus_const import (
    DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME,
    DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME,
    NX_SCHEMA_MODEL_NAME_KEY,
)
from bluesky_nexus.common.yaml_utils import read_yaml
from bluesky_nexus.common.logging_utils import logger
from bluesky_nexus.models.nx_models import *


def assign_pydantic_model_instance(devices_dictionary: dict):
    """
    For each device in devices_dictionary assign a pydantic model instance to it
    """

    for dev_instance in devices_dictionary.values():
        # Each device instance has a schema content that is assigned to it as a attribute 'nx_schema'
        schema_content: dict = read_attribute(
            dev_instance, DEVICE_CLASS_NX_SCHEMA_ATTRIBUTE_NAME
        )

        if schema_content is None:
            raise ValueError(
                f"Pydantic nexus schema content associated with the device: {dev_instance.name} is None. Check the device class definition for correct nexus schema assignment."
            )
        if not schema_content:
            raise ValueError(
                f"Pydantic nexus  schema content associated with the device: {dev_instance.name} is empty. Check the device class definition for correct nexus schema assignment."
            )

        # Read model name from the schema content
        try:
            model_name = schema_content[NX_SCHEMA_MODEL_NAME_KEY]
        except KeyError:
            raise ValueError(
                f"The key: {NX_SCHEMA_MODEL_NAME_KEY} not found in a schema file associated with the device: {dev_instance.name}"
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
        logger.exception(
            f"Error: Attribute '{attribute_name}' does not exist on the device {device.name}. Details: {e}"
        )
        return None
