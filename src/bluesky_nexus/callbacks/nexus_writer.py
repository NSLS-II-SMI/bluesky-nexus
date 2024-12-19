"""
NexusWriter Module
===================

This module provides a `NexusWriter` class for writing NeXus-format files, a standard format for scientific data.
The module integrates with the Bluesky framework and extends the `CollectThenCompute` callback. It captures
Bluesky start, descriptor, event, and stop documents and uses their metadata to produce NeXus files that comply
with the hierarchical structure and metadata standards of the NeXus format.

Classes:
--------
- NexusWriter:
    A Bluesky callback that writes NeXus files at the end of data acquisition. The class handles data extraction,
    transformation, and formatting of hierarchical data structures. It supports metadata placeholders to dynamically
    populate values based on events and descriptors in a run.

Functions:
----------
- process_nexus_md(nexus_md: dict, descriptors: dict, events: dict):
    Processes and populates NeXus metadata placeholders using data from Bluesky descriptors and events.

- extract_run_info(start: dict, stop: dict) -> dict:
    Extracts run-level metadata such as plan name, start/stop times, and other relevant details from the start and stop documents.

- create_nexus_file(file_path: str, data_dict: dict):
    Creates a NeXus-format HDF5 file based on a given hierarchical dictionary structure.

- create_nexus_group(parent_group: h5py.Group, name: str, data: dict, create_subgroup: bool):
    Recursively creates NeXus groups and datasets within an HDF5 file from hierarchical input data.

Key Features:
-------------
- Automatic NeXus file generation from Bluesky run metadata.
- Placeholder replacement with real-time data from events and descriptors.
- Hierarchical metadata handling for NeXus standards compliance.
- Supports user-defined or automatically generated file names.
- Handles time zone transformations for consistent time representation.

Dependencies:
-------------
- `h5py` for HDF5 file operations.
- `numpy` for efficient data handling.
- `pytz` for time zone support.
- `Bluesky` for integration with scientific data acquisition workflows.

"""

import copy
import os
import re
from collections import deque
from typing import Optional, Union

import h5py
import numpy as np
from bluesky.callbacks.core import CollectThenCompute
from h5py import Group

from bluesky_nexus.bluesky_nexus_const import (
    NX_FILE_EXTENSION,
    NX_MD_KEY,
    VALID_NXFIELD_DTYPES,
)
from bluesky_nexus.bluesky_nexus_def import _NX_FILE_DIR_PATH
from bluesky_nexus.common.decorator_utils import measure_time
from bluesky_nexus.transformation.symbolic_transformation import (
    apply_symbolic_transformation,
)


class NexusWriter(CollectThenCompute):
    """
    A class responsible for writing NeXus files using information from start, stop, event, and descriptor documents.

    Methods:
        create_nx_file_path(dir_path: str, file_name: str) -> str:
            Creates and validates the file path for the NeXus file based on the directory path and file name.

        compute():
            Processes the input documents, extracts metadata, and creates a NeXus file.
    """

    def create_nx_file_path(self, dir_path: str, file_name: str) -> str:
        """
        Creates a valid file path for the NeXus file, ensuring the directory exists
        and the file name adheres to the expected format.

        Parameters:
            dir_path (str): The directory path where the NeXus file will be saved.
            file_name (str): The desired name of the NeXus file. If None or empty, a name will
                             be auto-generated using the UID from the start document.

        Returns:
            str: The complete file path for the NeXus file.

        Raises:
            ValueError: If the provided directory path is not a valid directory.

        Notes:
            - If the file name is not provided, it defaults to a generated name based on the UID
              in the start document with the proper NeXus file extension.
            - If the file name contains "{uid}", it is replaced with the UID from the start document.
        """

        # Check if 'dir_path' is pointing to existing directory
        if not os.path.isdir(dir_path):
            raise ValueError(
                f"Nexus dir path {dir_path} is not pointing to a directory."
            )
            return

        # Check if 'file_name' is not None or not empty string
        if file_name is None or not file_name.strip():
            file_name = self._start_doc["uid"]
            file_name = file_name + NX_FILE_EXTENSION
            print(
                f"WARNING_MSG: Nexus file name not defined by the user. Nexus file name automatically generated to {file_name}"
            )

        # Add extension to file name
        if not file_name.endswith(NX_FILE_EXTENSION):
            file_name = file_name + NX_FILE_EXTENSION

        # Add uid to file name if necessary
        if "{uid}" in file_name:
            file_name = file_name.format(uid=self._start_doc["uid"])

        # Define nexus file path
        file_path: str = os.path.join(dir_path, file_name)

        return file_path

    def compute(self):
        self.generate_nexus_file()

    @measure_time
    def generate_nexus_file(self):
        """
        Processes the NeXus metadata and writes a NeXus file based on the start, stop,
        event, and descriptor documents.

        Workflow:
            1. Checks if the start document contains the necessary NeXus metadata key.
            2. Retrieves the NeXus directory path from the environment.
            3. Generates the NeXus file path using the directory and file name.
            4. Extracts run information from the start and stop documents.
            5. Creates a deep copy of the start document to safely process placeholders.
            6. Processes the NeXus metadata by applying events and descriptors.
            7. Combines extracted instrument data and run information into a single dictionary.
            8. Creates a NeXus file with the combined data.

        Raises:
            Exception: If an error occurs during the deepcopy of the start document.

        Notes:
            - Logs errors or warnings if essential metadata is missing.
            - Uses environment variables for configuration, such as the NeXus directory path.
        """

        # Check if NEXUS_MD_KEY is contained in the start document
        if NX_MD_KEY not in self._start_doc:
            print(
                f"ERROR_MSG: The start document does not contain {NX_MD_KEY} dictionary."
            )
            return

        # Retrieve nexus dir path from env variable
        nx_dir_path: str = _NX_FILE_DIR_PATH

        # Retrieve nexus file name from start doc
        nx_file_name: str = self._start_doc.get("nx_file_name", None)

        # Create nexus file path
        nx_file_path: str = self.create_nx_file_path(nx_dir_path, nx_file_name)

        # Create 'run_info' dict by extraction of data from the start and stop document
        run_info_data: dict = extract_run_info(self._start_doc, self._stop_doc)

        # Copy the start document to be able to modify it. Reason: Documents are immutable.
        try:
            start_doc_cpy = copy.deepcopy(self._start_doc)
        except Exception as e:
            print(f"ERROR_MSG: Error during deepcopy of the start document: {e}")
            return

        # Process the placeholders of the nexus_md applying events and descriptors
        process_nexus_md(start_doc_cpy[NX_MD_KEY], self._descriptors, self._events)

        # Define dictionary: 'instrument_data'
        instrument_data: dict = start_doc_cpy[NX_MD_KEY]

        # Define 'data' dictionary consisting of: 'instrument_data' and 'run_info_data'
        data: dict = {"instrument": instrument_data, "run_info": run_info_data}

        # Create nexus file from the data
        create_nexus_file(nx_file_path, data)


# Define processing of the nexus md
def process_nexus_md(nexus_md: dict, descriptors: dict, events: dict):
    """
    Process the nexus metadata from the 'start' document by replacing placeholders with data
    from the 'events' and 'descriptors' documents. This function is used to fill in the values
    of placeholders ($post-run) with corresponding data from the events of the run.

    Args:
        nexus_md (dict): The dictionary representing the Nexus metadata, which may contain placeholders
                            for device values that need to be filled in with actual data.
        descriptors (dict): A dictionary or deque of descriptors, which contains metadata describing
                            the devices and their corresponding data keys.
        events (dict): A dictionary representing events, containing data associated with the run,
                        including the actual values for the placeholders.

    Returns:
        None: This function modifies the input `nexus_md` dictionary in place, replacing the placeholders
                with the corresponding data from the events.

    Notes:
        - The `$post-run` placeholders are replaced with data based on descriptors and events.
        - This function assumes that the descriptors contain metadata on the devices being used in the run.
    """

    def process_post_run():
        """
        Processes post-run placeholders within the Nexus metadata, replacing them with actual
        data from the event logs and descriptors.

        This inner function contains several helper functions to:
        - Select the appropriate descriptor based on the device name.
        - Extract the component name from the placeholder.
        - Replace the placeholders in the Nexus metadata with actual event data.
        """

        def select_descriptor(descriptors: deque, cpt_name: str) -> Optional[dict]:
            """
            Select an appropriate descriptor for the given component name 'cpt_name'
                - If cpt_name is found in any other descriptor than the 'baseline' descriptor read from this descriptor
                - elif cpt_name is found only in the 'baseline' descriptor read from 'baseline' descriptor
                - else raise exception
                This means taht each instantiated device whose schema contains '$post-run' placeholder has to be included into a baseline.
                Otherwise if such an instantiated device is not used in a plan, the descriptor will not be found and exception will be raised

            Args:
                descriptors (deque): The deque of descriptors.
                cpt_name (str): The component name to look for in the descriptors.

            Returns:
                dict: The selected descriptor.

            Raises:
                ValueError: If no descriptor with the specified component name is found.
            """

            # If the deque 'descriptors' is empty, raise an exception
            if not descriptors:
                raise ValueError("The deque 'descriptors' is empty")

            # Try to find a descriptor with the cpt_name and name not equal to 'baseline'
            for descriptor in descriptors:
                if (
                    cpt_name in descriptor["data_keys"]
                    and descriptor["name"] != "baseline"
                ):
                    return descriptor

            # If no such selector, try to find a baseline descriptor containing cpt_name
            for descriptor in descriptors:
                if (
                    cpt_name in descriptor["data_keys"]
                    and descriptor["name"] == "baseline"
                ):
                    return descriptor

            # No descriptor contains the cpt_name
            raise ValueError(f"No descriptor contains the 'data_key': {cpt_name}")

        # Define a few helper functions to parse the Nexus tree and replace values with data from the events of the run
        def get_cpt_name_from_placeholder(value: str) -> Optional[str]:
            """
            Extracts the component name from the placeholder string, typically in the form
            of `$post-run:events:<component_name>`.

            Args:
                value (str): The placeholder string, e.g., "$post-run:events:a_b_c".
                Pattern matches:
                    $post-run:events:a_b_c
                    $post-run:events:a-b-c-d
                    $post-run:events:a_b-c_d-e
                    $post-run:events:a
            Returns:
                str: The component name extracted from the placeholder (e.g., "a_b_c").
                None: If the placeholder does not match the expected pattern.
            """

            POST_RUN_LABEL: str = "$post-run"
            DELIMITER: str = ":"
            PATTERN: str = r"^\$post-run:events:[a-zA-Z0-9_-]+$"

            match = re.search(PATTERN, value)
            if match:
                cpt_name: str = value[
                    len(POST_RUN_LABEL + DELIMITER + "events" + DELIMITER) :
                ]
                return cpt_name
            else:
                return None  # Pattern does not match

        def replace_func(dev_name: str, obj: dict) -> dict:
            """
            Replace the placeholder in the given object with actual data from the events.

            This function looks for the `$post-run` placeholders within the object and replaces
            them with actual values extracted from the events and descriptors.

            Args:
                dev_name (str): The name of the device from the Nexus metadata.
                obj (dict): The object to replace the placeholder in.

            Returns:
                dict: The object with the placeholder replaced with the actual data.
            """

            if "value" in obj:
                placeholder: str = obj["value"]
                if not isinstance(placeholder, str):
                    return obj

                # Define component name
                cpt_name: str = get_cpt_name_from_placeholder(placeholder)
                if cpt_name is None:
                    return obj

                # Define object delimiter. It is expected that ophyd-async will use the same delimiter as ophyd
                obj_delimiter: str = "_"

                # Redefine component name as to be read from the blusky documents (with prefixed device name)
                cpt_name: str = dev_name + obj_delimiter + cpt_name

                # Select an appropriate descriptor for the 'cpt_name':
                descriptor: dict = select_descriptor(descriptors, cpt_name)

                # Extract the 'uid' of the descriptor
                descriptor_uid: str = descriptor["uid"]

                # Collect data from the events associated with the descriptor (by applying 'descriptor_uid')
                events_data: np.array = np.array(
                    [
                        evt["data"][cpt_name]
                        for evt in events
                        if evt["descriptor"] == descriptor_uid
                        and cpt_name in evt["data"]
                    ]
                )

                # Optional transformation
                if "transformation" in obj:
                    # Execute transformation on events_data
                    if "value" == obj["transformation"]["target"]:
                        expression: str = obj["transformation"]["expression"]
                        events_data = apply_symbolic_transformation(
                            events_data, expression
                        )

                # Assign the result to the object's value
                obj["value"] = events_data

                # Collect component timestamps from the events associated with the descriptor (by applying 'descriptor_uid')
                events_cpt_timestamps: np.array = np.array(
                    [
                        evt["timestamps"][cpt_name]
                        for evt in events
                        if evt["descriptor"] == descriptor_uid
                        and cpt_name in evt["timestamps"]
                    ]
                )
                # Assign the result to the object's value
                obj["events_cpt_timestamps"] = events_cpt_timestamps

                # Collect event timestamps from the events associated with the descriptor (by applying 'descriptor_uid')
                events_timestamps: np.array = np.array(
                    [
                        evt["time"]
                        for evt in events
                        if evt["descriptor"] == descriptor_uid
                    ]
                )
                # Assign the result to the object's value
                obj["events_timestamps"] = events_timestamps

                # Extract from the descriptor["data_keys"] the data describing the 'cpt_name'
                desc: dict = descriptor["data_keys"][cpt_name]

                # ----------- Assign to the 'obj' all abligatory keys -----------

                # Extract dtype (obligatory key), with fallback to defaults
                dtype = obj.get("dtype", desc.get("dtype", "unknown"))
                if dtype == "number":
                    dtype = "float64"
                elif dtype == "string":
                    dtype = "str"
                elif dtype == "array":
                    dtype = obj.get("attrs", {}).get(
                        "dtype", "float64"
                    )  # One lookup for dtype
                elif dtype == "object":
                    dtype = "str"  # Treat object as a string
                # Assign dtype to the object
                obj["dtype"] = dtype

                # Extract shape (obligatory key) and prepend the length of events
                obj["shape"] = [len(events_data)] + obj.get(
                    "shape", desc.get("shape", [])
                )

                # Ensure "attrs" key exists in obj
                obj.setdefault("attrs", {})

                # Extract and set source (obligatory key)
                obj["attrs"]["source"] = obj["attrs"].get(
                    "source", desc.get("source", "unknown")
                )

                # ----------- Assign to the 'obj' all optional keys -----------

                # Extract units (optional key)
                units = obj["attrs"].get("units", desc.get("units", None))
                if units is not None:
                    obj["attrs"]["units"] = units

                # Extract and set external (optional key)
                external = obj["attrs"].get("external", desc.get("external", None))
                if external is not None:
                    obj["attrs"]["external"] = external

                # Extract precision (optional key)
                precision = obj.get("precision", desc.get("precision", None))
                if precision is not None:
                    obj["precision"] = precision

                return obj
            else:
                return obj

        def replace_values(dev_name: str, tree: Union[dict, list], func: callable):
            """
            Recursively replace placeholders in a tree (dictionary or list) structure by applying the
            provided function.

            Args:
                dev_name (str): The name of the device.
                tree (dict or list): The tree structure containing placeholders to replace.
                func (callable): The function to apply for replacement.

            Returns:
                dict or list: The tree with placeholders replaced.
            """

            if isinstance(tree, dict):
                for key, value in tree.items():
                    if (
                        isinstance(value, dict)
                        and "nxclass" in value
                        and "value" in value
                    ):
                        tree[key] = func(dev_name, value)
                    tree[key] = replace_values(dev_name, value, func)
            elif isinstance(tree, list):
                tree = [replace_values(dev_name, item, func) for item in tree]
            return tree

        for dev_name in nexus_md.keys():
            nexus_md[dev_name] = replace_values(
                dev_name, nexus_md[dev_name], replace_func
            )

    # Process post-run placeholders by filling them with data provided by bluesky events
    process_post_run()


# Define extraction of run info
def extract_run_info(start: dict, stop: dict) -> dict:
    """
    Extract relevant information from the 'start' and 'stop' documents and return a dictionary
    with the extracted data.

    Args:
        start (dict): A dictionary representing the start document containing metadata for a run.
        stop (dict): A dictionary representing the stop document containing metadata for a run.

    Returns:
        dict: A dictionary with two keys, 'start' and 'stop', each containing the relevant data.
            The 'start' key will include data from the start document, excluding the 'nexus_md'
            and 'device_md' keys. The 'stop' key will include the entire stop document.

    Notes:
        - The 'nexus_md' and 'device_md' keys are intentionally excluded from the 'start' document
            in the resulting dictionary.
    """

    START_LABEL: str = "start"
    STOP_LABEL: str = "stop"

    # Define result dictionary
    result: dict = {START_LABEL: dict(), STOP_LABEL: dict()}

    # Insert into the 'result[START_LABEL]' dictionary the data from the start document but not 'nexus_md'
    for key in start.keys():
        if (
            NX_MD_KEY == key
        ):  # Do not add subdictionary of the key 'nexus_md'. Do not add subdictionary of the key 'nexus_md'
            continue
        result[START_LABEL][key] = start[key]

    # Insert into the 'result[STOP_LABEL]' dictionary all the data from the stop document
    result[STOP_LABEL] = stop

    # Return the result
    return result


def create_nexus_file(file_path, data_dict):
    """
    Creates a NeXus file at the specified file path using the provided data dictionary.

    Parameters:
        file_path (str): The path where the NeXus file will be created.
        data_dict (dict): A dictionary containing the data to populate the NeXus file.
                          Keys represent group or dataset names, and values represent
                          their corresponding data or attributes. Special keys like
                          "instrument" or "run_info" are treated as specific NeXus groups.

    Raises:
        ValueError: If invalid data types are detected for certain groups or fields.

    Example:
        data = {
            "instrument": {"mono": {"nxclass": "NXmonochromator", "value": 123.4}},
            "run_info": {"start_time": "2023-12-01T12:00:00"},
        }
        create_nexus_file("example.nxs", data)
    """

    with h5py.File(file_path, "w") as f:
        # Create file level attribute
        f.attrs["default"] = "entry"

        # Create the NXentry group
        entry: Group = f.create_group("entry")
        entry.attrs["NX_class"] = "NXentry"
        entry.attrs["default"] = "data"

        for key, value in data_dict.items():
            # Create instrument group under 'entry' group
            if "instrument" == key:
                # Create instrument group
                instrument_group: Group = entry.create_group(key)
                # Add attribute
                instrument_group.attrs["NX_class"] = "NXinstrument"

                # Add group or fieled to instrument_group
                add_group_or_field(instrument_group, value)

            # Create run_info group under 'entry' group
            elif "run_info" == key:
                # Create run_info group
                run_info_group = entry.create_group(key)
                # Add attribute
                run_info_group.attrs["NX_class"] = "NXcollection"
                # Write data to the run_info_group
                write_collection(run_info_group, value)

            # Treat everything else as entry metadata
            else:
                if isinstance(value, (str, int, float)):
                    entry.create_dataset(key, data=value)
                elif isinstance(value, (list, np.ndarray)):
                    entry.create_dataset(key, data=np.array(value))

        print(f"NeXus file '{file_path}' created successfully.")


def add_group_or_field(group, data):
    """
    Recursively adds groups or datasets to a NeXus file based on the provided data.

    Parameters:
        group (h5py.Group): The parent group to which fields or subgroups will be added.
        data (dict): A dictionary describing the NeXus structure. Keys represent names
                     of groups or fields, and values provide detailed metadata such as
                     `nxclass`, `value`, `dtype`, and attributes.

    Raises:
        ValueError: If invalid `dtype` is encountered for a dataset.

    Example:
        data = {
            "mono": {
                "nxclass": "NXmonochromator",
                "value": 123.4,
                "dtype": "float64",
                "attrs": {"units": "keV"}
            }
        }
        add_group_or_field(parent_group, data)
    """
    for key, value in data.items():
        if isinstance(value, dict):
            ###
            ### Handle NeXus fields
            ###
            if "nxclass" in value and "value" in value:
                dtype = value.get("dtype", None)

                if dtype in VALID_NXFIELD_DTYPES:
                    if "str" == dtype or "char" == dtype:
                        dtype = h5py.string_dtype(encoding="utf-8")

                    ### Create dataset for 'value'
                    dataset = group.create_dataset(
                        key, data=value["value"], dtype=dtype
                    )
                    dataset.attrs["nxclass"] = value["nxclass"]

                    # Add attributes to the dataset
                    for attr_name, attr_value in value.get("attrs", {}).items():
                        # Convert non-compatible types to strings
                        if isinstance(attr_value, (dict, list)):
                            attr_value = str(attr_value)
                        dataset.attrs[attr_name] = attr_value

                    if "shape" in value.keys():
                        dataset.attrs["shape"] = value["shape"]

                    # Handle any additional keys in the dictionary as attributes
                    for extra_key, extra_value in value.items():
                        if extra_key not in {
                            "value",
                            "dtype",
                            "attrs",
                            "nxclass",
                            "shape",
                            "events_cpt_timestamps",
                            "events_timestamps",
                        }:
                            # Convert non-compatible types to strings
                            if isinstance(extra_value, (dict, list)):
                                extra_value = str(extra_value)
                            dataset.attrs[extra_key] = extra_value

                    ### Create dataset for 'events_cpt_timestamps'
                    if "events_cpt_timestamps" in value:
                        dataset = group.create_dataset(
                            key + "_timestamps",
                            data=value["events_cpt_timestamps"],
                            dtype="float64",
                        )
                        dataset.attrs["nxclass"] = "NX_FLOAT"
                        dataset.attrs["shape"] = [len(value["events_cpt_timestamps"])]
                        dataset.attrs["description"] = (
                            f"Timestamps of the component: {key}"
                        )

                    ### Create dataset for 'events_timestamp'
                    if "events_timestamps" in value:
                        dataset = group.create_dataset(
                            "events_timestamps",
                            data=value["events_timestamps"],
                            dtype="float64",
                        )
                        dataset.attrs["nxclass"] = "NX_FLOAT"
                        dataset.attrs["shape"] = [len(value["events_timestamps"])]
                        dataset.attrs["description"] = "Timestamps of the events"

                else:
                    raise ValueError(
                        f"Invalid dtype: {dtype} detected in one of the schema files while processing the group: {group.name}."
                    )

            ###
            ### Handle NeXus groups
            ###
            elif "nxclass" in value:
                subgroup = group.create_group(key)

                subgroup.attrs["NX_class"] = value["nxclass"]

                if "default" in value:
                    subgroup.attrs["default"] = value["default"]["value"]

                if "attrs" in value:
                    for attr_key, attr_value in value["attrs"].items():
                        subgroup.attrs[attr_key] = attr_value

                # Recursively add fields or subgroups
                add_group_or_field(
                    subgroup,
                    {
                        k: v
                        for k, v in value.items()
                        if k != "nxclass" and k != "default" and k != "attrs"
                    },
                )

        else:
            # Handle as attribute of the group
            group.attrs[key] = value


def write_collection(group, data: dict):
    """
    Recursively writes a collection of data (nested dictionaries, lists, and primitive values)
    to a given group in a hierarchical storage structure.

    The function processes the input data dictionary and handles different types of data as follows:
    - Nested dictionaries are stored as subgroups.
    - Primitive values (int, float, str, bool) are directly stored as datasets.
    - Lists or tuples are stored as datasets, with special handling for nested structures or strings within the list.

    Args:
        group (h5py.Group): The group where the data will be stored. It could represent a group in an HDF5 file or any similar hierarchical storage.
        data (dict): The data dictionary to be written. It can contain nested dictionaries, lists, tuples, or primitive values.

    Raises:
        TypeError: If the function encounters an unsupported data type during processing.

    Notes:
        - Nested dictionaries are recursively written as subgroups.
        - Non-nested lists or tuples containing primitive values are converted into datasets with appropriate types.
        - Lists or tuples containing other lists or tuples are serialized into strings.
    """

    for key, value in data.items():
        if isinstance(value, dict):
            # Create a subgroup for nested data dictionaries
            subgroup = group.create_group(key)
            write_collection(subgroup, value)

        elif isinstance(value, (float, int, str, bool)):
            group.create_dataset(key, data=value)

        elif isinstance(value, (list, tuple)):
            # Check for nested lists/tuples
            if any(isinstance(item, (list, tuple)) for item in value):
                # Serialize nested structure into a single string
                serialized_value = str(value)  # Convert entire list/tuple to string
                group.create_dataset(key, data=serialized_value)
            else:
                # Non-nested lists
                if any(
                    isinstance(item, str) for item in value
                ):  # Check if there is a str inside of the list or tuple
                    normalized_value = [str(item) for item in value]
                    group.create_dataset(
                        key, data=np.array(normalized_value, dtype="S")
                    )
                else:
                    normalized_value = list(value)
                    group.create_dataset(key, data=np.array(normalized_value))
        else:
            print(f"Unsupported type {type(value)} for key '{key}'")
            raise TypeError(f"ERROR: Unsupported type {type(value)} for key '{key}'")
