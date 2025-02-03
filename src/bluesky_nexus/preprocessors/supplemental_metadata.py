"""Module supplemental_metadata

Module for Managing and Injecting Supplemental Metadata in Bluesky Plans

This module provides utilities to manage, validate, and inject supplemental metadata into Bluesky plans. The primary feature is the SupplementalMetadata class, which extends the functionality of Bluesky's SupplementalData to dynamically generate and inject metadata based on device-specific attributes. It includes support for two types of metadata: device metadata (DEVICE_MD) and NeXus metadata (NEXUS_MD).

Key Features:

    Dynamically generate metadata for devices participating in a plan.
    Validate and filter devices based on their usage in the plan or baseline subscription.
    Support for placeholder resolution in NeXus metadata, handling missing data gracefully.
    Caching of plans to ensure non-exhaustible replayable plans.
    Utilities for metadata extraction, processing, and validation.

Classes:

    SupplementalMetadata: Extends SupplementalData to manage device metadata injection.
    PlanDeviceChecker: Utility to validate which devices in a dictionary are used in a plan.

Functions:

    create_device_md: Generates a device metadata dictionary using device attributes.
    create_nexus_md: Generates NeXus-compliant metadata with placeholder resolution.
    create_metadata: A generic function for extracting metadata using a provided extraction function.
    process_value_not_available: Removes keys with values marked as "NOT_AVAILABLE".
    resolve_pre_run_placeholders: Recursively resolves placeholders in metadata dictionaries.
    get_nested_dict_value: Fetches values from nested dictionaries using a key path.
    cache_plan: Caches Bluesky plan to make it replayable twice.

Dependencies:

    asyncio: For asynchronous operations during metadata resolution.
    bluesky.preprocessors: For plan manipulation and metadata injection.
    bluesky.run_engine.Msg: For working with Bluesky plans.
    enum: For defining metadata types as an enumeration.
    typing: For type hints (e.g., Callable, Dict).
    bluesky_nexus: Constants and device model utilities for NeXus metadata handling.
"""

import asyncio
from enum import Enum, auto
from itertools import tee
from typing import Any, Callable, Dict

from bluesky.preprocessors import SupplementalData, inject_md_wrapper, plan_mutator
from bluesky.run_engine import Msg

from bluesky_nexus.bluesky_nexus_const import (
    DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME,
    DEVICE_MD_KEY,
    NOT_AVAILABLE_LABEL,
    NX_MD_KEY,
    PRE_RUN_CPT_LABEL,
    PRE_RUN_MD_LABEL,
)
from bluesky_nexus.bluesky_nexus_device_model import assign_pydantic_model_instance
from bluesky_nexus.common.decorator_utils import measure_time
from bluesky_nexus.common.logging_utils import logger


class SupplementalMetadata(SupplementalData):
    """
    A class to manage and inject supplemental metadata into a Bluesky plan.

    This class checks the devices participating in the plan and generates
    metadata for the specified type (DEVICE_MD or NEXUS_MD). It ensures
    that devices in the 'devices_dictionary' are either used in the plan
    or are part of the baseline, and injects metadata accordingly.
    """

    class MetadataType(Enum):
        DEVICE_MD = auto()
        NEXUS_MD = auto()

    def __init__(self, *args, nx_schema_dir_path=None, **kwargs):
        """
        Initializes the SupplementalMetadata instance.

        This constructor accepts both positional and keyword arguments, passing them
        to the parent class constructor. Additionally, it allows for an optional
        `nx_schema_dir_path` parameter to specify the directory path for the NeXus schema.

        Args:
            *args: Positional arguments passed to the parent constructor.
            **kwargs: Keyword arguments passed to the parent constructor.
            nx_schema_dir_path (str, optional): The directory path to the NeXus schema.
                If not provided, the default value is `None`.

        Notes:
            - `nx_schema_dir_path` is an optional argument that can be used to specify
            the path to the directory where the NeXus schema is located.
        """

        super().__init__(*args, **kwargs)
        self.nx_schema_dir_path = nx_schema_dir_path

    def __call__(self, plan):
        """
        Delegates the call to the `inject_metadata_to_plan` function.
        """
        return (yield from self.inject_metadata_to_plan(plan))

    def inject_metadata_to_plan(self, plan):
        if not hasattr(self, "devices_dictionary"):
            raise AttributeError(
                "The 'devices_dictionary' attribute must be set before calling the instance."
            )

        if not hasattr(self, "baseline"):
            raise AttributeError(
                "The 'baseline' attribute must be set before calling the instance."
            )

        if not hasattr(self, "md_type"):
            raise AttributeError(
                "The 'md_type' attribute must be set before calling the instance."
            )

        # Dictionary to map MetadataType to their respective metadata creation functions
        metadata_functions = {
            self.MetadataType.DEVICE_MD: create_device_md,
            self.MetadataType.NEXUS_MD: create_nexus_md,
        }

        # Retrieve the correct function based on md_type
        create_metadata: callable = metadata_functions.get(self.md_type)
        if not create_metadata:
            raise ValueError(f"Invalid metadata type: {self.md_type}")

        # We have to cache the plan, otherwise the PlanDeviceChecker would exhaust the plan
        plan1, plan2 = cache_plan(plan)  # Create two identical plans plan1 and plan2 from the plan

        # Check if all devices of self.devices_dictionary are participating in the plan.
        checker = PlanDeviceChecker(self.devices_dictionary)
        checker_result = checker.validate_plan_devices(plan1)

        # Define a dictionary of devices taking part in the plan. (It includes devices not taking part in a run but subscribed to the baseline.)
        devices_in_plan: dict = {
            name: dev
            for name, dev in self.devices_dictionary.items()
            if dev not in checker_result["unused_devices"].values()
            or dev in self.baseline
        }

        # Assign to all the devices contained in 'devices_in_plan' instances of pydantic models
        if self.MetadataType.NEXUS_MD == self.md_type:
            assign_pydantic_model_instance(
                self.nx_schema_dir_path, devices_in_plan
            )

        # Create metadata and inject it into the plan
        metadata: dict = create_metadata(devices_in_plan)
        plan = inject_md_wrapper(plan2, metadata)
        return (yield from plan)


# Create device metadata
@measure_time
def create_device_md(devices_dictionary: dict) -> dict:
    """
    Generate a device metadata dictionary for a collection of device instances.

    This function extracts metadata from each device instance in `devices_dictionary` by calling
    the `get_attributes()` method on each device's `md` attribute. The extracted metadata is
    organized under a common metadata key.

    Args:
        devices_dictionary (dict): A dictionary where keys are device names or identifiers and
                                   values are device instances. Each device instance is expected
                                   to have an `md` attribute with a `get_attributes()` method
                                   for extracting its metadata.

    Returns:
        dict: A dictionary containing all device metadata under a top-level key specified by
              `metadata_key` ("device_md"). The structure is as follows:
              {
                  "device_md": {
                      device_name_1: metadata_from_device_1,
                      device_name_2: metadata_from_device_2,
                      ...
                  }
              }

    Example:
        devices = {
            "device1": device1_instance,
            "device2": device2_instance,
            ...
        }

        device_metadata = create_device_md(devices)
        # device_metadata would be structured with metadata from each device's `get_attributes()` method.

    Notes:
        - The function `create_metadata` is used to handle the metadata extraction and structuring.
        - This function assumes that `devices_dictionary` is well-formed, with each device having an
          `md` attribute and that `md` has a `get_attributes()` method.
    """

    # The extraction of the md dict from device instance made by means of the function: get_attributes().

    metadata_key: str = DEVICE_MD_KEY
    return create_metadata(
        devices_dictionary,
        lambda device: device.md.get_attributes(),
        metadata_key,
    )


# Create nexus metadata
@measure_time
def create_nexus_md(devices_dictionary: dict) -> dict:
    """
    Create a dictionary of metadata with resolved placeholders. If a placeholder cannot
    be resolved, the entire NXfield containing it is removed.

    Args:
        devices_dictionary (dict): A dictionary mapping device names to device instances.

    Returns:
        dict: The metadata dictionary with placeholders resolved.
    """

    metadata_key: str = NX_MD_KEY

    def get_nx_model_metadata(device):
        if not hasattr(device, DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME):
            raise AttributeError(
                f"Device {device.name} does not have {DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME} attribute."
            )
        return getattr(device, DEVICE_INSTANCE_NX_MODEL_ATTRIBUTE_NAME).model_dump(
            exclude_none=True
        )

    metadata: dict = create_metadata(
        devices_dictionary,
        lambda device: get_nx_model_metadata(device),
        metadata_key,
    )

    # Resolve placeholders in metadata
    resolve_pre_run_placeholders(metadata[metadata_key], devices_dictionary)

    # Remove parent keys of: "value":NOT_AVAILABLE_LABEL.
    # This is the case if component value could not be read.
    metadata = process_value_not_available(metadata)

    return metadata


def create_metadata(
    devices_dictionary: Dict[str, object],
    extract_fn: Callable,
    metadata_key: str,
) -> dict:
    """
    Generalized function to create metadata for devices using the provided extraction function.

    Args:
        devices_dictionary (dict): A dictionary mapping device instance names to device instances objects.
        extract_fn (function): A function to extract metadata from a device.
        metadata_key (str): The key to be used for storing the metadata in the dictionary.

    Returns:
        dict: A dictionary containing the metadata, structured as follows:
              {
                  metadata_key: {
                      "<device_name>": <metadata>,
                      ...
                  }
              }
    """

    metadata: dict = {metadata_key: {}}
    for device_name, device_obj in devices_dictionary.items():
        metadata[metadata_key][device_name] = extract_fn(device_obj)
    return metadata


def process_value_not_available(data: dict) -> dict:
    """
    Recursively remove parent dictionaries that contain 'value': NOT_AVAILABLE_LABEL.
    """
    # Iterate over a copy of the dictionary items
    for key in list(data.keys()):
        value = data[key]

        # If the current value is a dictionary, check its contents
        if isinstance(value, dict):
            # If 'value': NOT_AVAILABLE_LABEL is in this dictionary, mark the parent key for deletion
            if NOT_AVAILABLE_LABEL == value.get("value"):
                logger.warning(f"The key: '{key}' removed from nexus metadata.")
                del data[key]
            else:
                # Otherwise, recursively check deeper levels
                data[key] = process_value_not_available(value)
    return data


def resolve_pre_run_placeholders(metadata: dict, devices_dictionary: dict):
    """
    Recursively resolve all $pre-run placeholders in a metadata dictionary for each device.
    If a placeholder cannot be resolved, removes the entire NXfield containing it.

    Args:
        metadata (dict): A dictionary containing metadata for each device, with device instance
                         names as keys and sub-dictionaries containing metadata.
        devices_dictionary (dict): A dictionary mapping device instance names to device instances.
    """
    for device_name, device_metadata in metadata.items():
        # Get the device instance object by device name
        device_obj = devices_dictionary.get(device_name)

        # Recursively resolve placeholders in the device's metadata dictionary
        _resolve_pre_run_placeholders_for_device(device_metadata, device_obj)


def _resolve_pre_run_placeholders_for_device(device_metadata: dict, device_obj: object):
    """
    Helper function to recursively resolve $pre-run placeholders in the metadata dictionary
    for a specific device. If a placeholder cannot be resolved, removes the entire NXfield.

    Args:
        device_metadata (dict): Metadata dictionary for a specific device instance object.
        device_obj (object): The device instance object associated with the current metadata.
    """

    for key, value in device_metadata.items():
        if isinstance(value, dict):
            # Recursively process nested dictionaries
            _resolve_pre_run_placeholders_for_device(value, device_obj)
        elif isinstance(value, str) and (
            value.startswith(PRE_RUN_CPT_LABEL) or value.startswith(PRE_RUN_MD_LABEL)
        ):
            # Attempt to resolve the placeholder
            device_metadata[key] = resolve_pre_run_placeholder_value(value, device_obj)


def resolve_pre_run_placeholder_value(placeholder: str, device_obj: object) -> Any:
    """
    Resolve a $pre-run-cpt or $pre-run-md placeholder for a specific device by dynamically fetching a nested component value.

    Args:
        placeholder (str): The placeholder string, e.g. "$pre-run-cpt:obj1: ... objN-1:objN:component". This is a chain telling how to access a component of a device instance. Delimiter is ':'.
                                                        "$pre-run-md:key1: ... keyN-1:keyN". This is the chain telling how to access the key in a nested dictionary accessible over attribute md of the device instance. Delimiter is ':'.
        device_obj: The device instance to use for resolving the placeholder.

    Returns:
        The resolved value retrieved from the nested component path.

    Raises:
        AttributeError: If the component cannot be found or does not have a valid accessor.
    """

    placeholder_splitted: list = placeholder.split(":")
    prefix: str = placeholder_splitted[0]

    # Get the nested path, ignoring "$pre-run-cpt" or "$pre-run-md" prefix
    parts: list = placeholder_splitted[
        1:
    ]  # Ignore the "$pre-run-cpt" or "$pre-run-md" part

    # Resolve placeholder by asking device instance metadata for its value
    if PRE_RUN_MD_LABEL == prefix:
        if not parts:
            raise ValueError(f"Invalid placeholder format: {placeholder} detected in a schema yml file associated with the device instance: {device_obj.name}. Valid placeholder structure: '$pre-run-md:key1: ... keyN-1:keyN'")
        data: dict = device_obj.md.get_attributes()
        value = get_nested_dict_value(data, parts)
        if value is None:
            logger.warning(
                f"The key (key sequence) '{':'.join(parts)}' not found in the metadata of the device instance: '{device_obj.name}'. The associated NeXus metadata will be automatically removed."
            )
            return NOT_AVAILABLE_LABEL
        return value

    # Resolve placeholder by asking device instance component for its value
    elif PRE_RUN_CPT_LABEL == prefix:
        # Navigate through the component path within the device instance
        component = device_obj
        for attribute in parts:
            component = getattr(component, attribute, None)
            if component is None:
                logger.warning(
                    f"Attribute '{'.'.join(parts)}' not found in device instance '{device_obj.name}'. The associated NeXus metadata will be automatically removed."
                )
                return NOT_AVAILABLE_LABEL

        # Retrieve the final component value, assuming it has a `get()` or `get_value()` method
        if hasattr(component, "get"):
            return component.get()
        elif hasattr(component, "get_value"):
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(component.get_value())
        else:
            raise AttributeError(
                f"Attribute '{'.'.join(parts)}' of device '{device_obj.name}' does not have a method 'get_value()' or 'get()' to retrieve a value."
            )
    else:
        raise ValueError(
            f"Invalid prefix: '{prefix}' found in the placeholder: '{placeholder}'. Valid placeholder structure: '$pre-run-md:key1: ... keyN-1:keyN' or '$pre-run-cpt:obj1: ... objN-1:objN'"
        )


def get_nested_dict_value(data: dict, key_path: list):
    """
    Retrieve the value of a nested dictionary based on a list of keys representing the path.

    Args:
        data (dict): The nested dictionary to search.
        key_path (list): A list of keys representing the path to the desired value.
                         Each key corresponds to a level in the nested dictionary.

    Returns:
        The value associated with the final key in `key_path` if the path is valid, or `None` if any key is missing.

    Example:
        data = {
            "a": {
                "b": {
                    "c": 42
                }
            }
        }

        key_path = ["a", "b", "c"]
        result = get_nested_value(data, key_path)  # Returns 42
    """
    current_level = data
    for key in key_path:
        if isinstance(current_level, dict) and key in current_level:
            current_level = current_level[key]
        else:
            return None  # Return None if the path is invalid
    return current_level


class PlanDeviceChecker:
    """ "
    Check which of the devices listed in devices_dictionary participate in the plan
    Returns:
        - all_devices_used: bool
        - unused_devices: dict
        - used_devices: dict
    """

    def __init__(self, devices_dictionary):
        self.devices_dictionary = devices_dictionary

    @measure_time
    def validate_plan_devices(self, plan) -> dict:
        """
        Check which devices from self.devices_dictionary are used in the plan.
        Optimized to stop iterating once all devices have been found.

        Returns:
            dict: {
                "all_devices_used": bool,  # True if all devices in self.devices_dictionary are used
                "unused_devices": dict,    # Devices in self.devices_dictionary that are NOT used
                "used_devices": dict       # Devices in self.devices_dictionary that are used
            }
        """
        used_devices: dict = {}
        remaining_devices = set(self.devices_dictionary.keys())  # Track missing devices

        def collect_devices(msg):
            # Check if the object in the message is one of the devices
            if msg.obj and msg.obj.name in remaining_devices:
                used_devices[msg.obj.name] = self.devices_dictionary[msg.obj.name]
                remaining_devices.remove(msg.obj.name)  # Remove from remaining devices

                # Stop iterating if all devices have been found
                if not remaining_devices:
                    return None, None

            return None, None  # No modifications to the plan

        # Iterate through the plan
        # Make sure plan_mutator properly handles the StopIteration exception:
        try:
            list(plan_mutator(plan, collect_devices)) # Trigger the iteration process
        except StopIteration:
            pass  # Gracefully handle the StopIteration without causing a RuntimeError

        # Find unused devices
        unused_devices = {name: self.devices_dictionary[name] for name in remaining_devices}

        return {
            "all_devices_used": not unused_devices,  # True if all devices were used
            "unused_devices": unused_devices,
            "used_devices": used_devices,
        }


@measure_time
def cache_plan(plan):
    """
    Efficiently create two independent iterators from a Bluesky plan while preserving generator behavior.
    
    Args:
        plan (generator): The original Bluesky plan.
    
    Returns:
        tuple: Two independent generators over the plan.
    """
    plan1, plan2 = tee(plan, 2)  # Create two independent iterators

    # Convert iterators back into generators to support `.send()`
    def wrap_generator(it):
        for msg in it:
            yield msg  # Ensures it works like a generator

    return wrap_generator(plan1), wrap_generator(plan2)
