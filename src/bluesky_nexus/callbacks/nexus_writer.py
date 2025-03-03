"""
Module for Creating and Writing NeXus Files

This module contains functions for generating NeXus files in the HDF5 format using a dictionary-based approach. The functions allow the creation of a hierarchical structure within the NeXus file, with special handling for specific NeXus groups such as 'instrument' and 'run_info'. The module supports various types of data, including simple values, lists, and more complex nested structures.

Functions provided in this module include:

- `extract_run_info(start: dict, stop: dict) -> dict`: Extracts relevant information from the start and stop documents and returns a dictionary containing the relevant data.
- `create_nexus_file(file_path, data_dict)`: Creates a NeXus file at the specified file path using the provided data dictionary, handling groups and datasets based on the NeXus standard.
- `add_group_or_field(group, data)`: Recursively adds groups or datasets to a NeXus file based on the provided data, supporting nested structures and various data types.
- `write_collection(group, data: dict)`: Recursively writes a collection of data (nested dictionaries, lists, and primitive values) to a given group in the NeXus file, handling different data types appropriately.

The module ensures that valid data types are used for fields and datasets, and it validates input to avoid errors in the NeXus file structure. It is intended for use cases where NeXus data needs to be programmatically created and stored in HDF5 format, with support for complex data types and nested hierarchies.

Example Usage:

    # Example of using the module to create a NeXus file
    data = {
        "instrument": {"mono": {"NX_class": "NXmonochromator", "value": 123.4}},
        "run_info": {"start_time": "2023-12-01T12:00:00"},
    }
    create_nexus_file("example.nxs", data)

Notes:
    - The module expects the provided data dictionary to be well-structured according to the NeXus format.
    - Special handling for fields like 'events_cpt_timestamps' and 'events_timestamps' is included.
    - Error handling is in place to manage invalid data types and unsupported structures.
"""

import copy
import os
import re
from collections import deque
from typing import Optional, Union, Any

import h5py
import numpy as np
from bluesky.callbacks.core import CollectThenCompute

from bluesky_nexus.bluesky_nexus_const import (
    NX_FILE_EXTENSION,
    NX_MD_KEY,
    VALID_NXFIELD_DTYPES,
    NX_DTYPE_MAP,
)
from bluesky_nexus.common.decorator_utils import measure_time
from bluesky_nexus.common.logging_utils import logger
from bluesky_nexus.transformation.symbolic_transformation import (
    apply_symbolic_transformation,
)


class NexusWriter(CollectThenCompute):
    """
    A class responsible for writing NeXus files based on the start, stop, event, and descriptor documents.

    This class handles the extraction of relevant metadata from the documents, processes it, and creates
    a NeXus file in HDF5 format. It is designed to be part of a larger system that interacts with a RunEngine
    and manages data collection, processing, and file writing.

    Inherited Methods:
        - `__init__(nx_file_dir_path=None)`: Initializes the class and optionally sets a directory for saving NeXus files.
        - `__call__(name, doc)`: Handles incoming documents from the RunEngine, processing them based on their type ('start', 'stop', etc.).

    Methods:
        - `create_nx_file_path(dir_path: str, file_name: str) -> str`:
            Creates and validates the file path for the NeXus file based on the directory path and file name.
        - `compute()`:
            Processes the input documents, extracts metadata, and creates a NeXus file.
    """

    def __init__(self, nx_file_dir_path=None):
        super().__init__()  # Initialize the parent class
        self.nx_file_dir_path = nx_file_dir_path

    def __call__(self, name, doc):
        """
        Handle documents from the RunEngine and delegate them to
        the appropriate methods based on the document type.

        Parameters:
            name (str): The type of the document (e.g., 'start', 'stop', 'descriptor', 'event').
            doc (dict): The content of the document, which is passed to the corresponding method
                        for processing (e.g., start document, event data, etc.).

        Notes:
            - The method ensures that documents are processed in the correct sequence (start -> descriptor -> event -> stop).
            - This method delegates the responsibility of handling each document type to specific class methods.
        """
        if name == "start":
            self.start(doc)
        elif name == "descriptor":
            self.descriptor(doc)
        elif name == "event":
            self.event(doc)
        elif name == "stop":
            self.stop(doc)

    def create_nx_file_path(self, dir_path: str, file_name: str) -> str:
        """
        Creates a valid file path for the NeXus file, ensuring the directory exists
        and the file name adheres to the expected format.

        Parameters:
            dir_path (str): The directory path where the NeXus file will be saved.
            file_name (str): The desired name of the NeXus file. If None or empty,
                            a name will be auto-generated using the UID from the start document.

        Returns:
            str: The complete file path for the NeXus file.

        Raises:
            ValueError: If the provided directory path is not a valid directory.

        Notes:
            - If the file name is not provided, it defaults to a generated name based on the UID
            in the start document with the proper NeXus file extension.
            - If the file name contains "{uid}", it is replaced with the UID from the start document.
            - The file name will always have the NeXus file extension appended if not already present.
        """

        # Check if 'dir_path' is pointing to existing directory
        if not os.path.isdir(dir_path):
            raise ValueError(
                f"Nexus dir path {dir_path} is not pointing to a directory."
            )

        # Check if 'file_name' is not None or not empty string
        if file_name is None or not file_name.strip():
            file_name = self._start_doc["uid"]
            file_name = file_name + NX_FILE_EXTENSION
            logger.warning(
                f"Nexus file name not defined by the user. Nexus file name automatically generated to {file_name}"
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
        """
        Triggers the process of generating the NeXus file by calling `generate_nexus_file()`.

        This method acts as a simple entry point for processing the metadata and writing the NeXus file.
        """
        self.generate_nexus_file()

    @measure_time
    def generate_nexus_file(self):
        """
        Processes the NeXus metadata and writes a NeXus file based on the start, stop,
        event, and descriptor documents.

        The workflow includes:
            1. Verifying the presence of necessary metadata in the start document.
            2. Retrieving configuration from the environment, such as the NeXus directory path.
            3. Generating the NeXus file path using the directory and file name.
            4. Extracting run information from the start and stop documents.
            5. Safely creating a deepcopy of the start document for processing.
            6. Handling placeholders in the metadata using event and descriptor data.
            7. Combining instrument metadata with run information.
            8. Writing the NeXus file with the combined data.

        Raises:
            Exception: If an error occurs during the deepcopy of the start document.

        Notes:
            - If required metadata is missing from the start document, an error message is logged.
            - The method processes placeholders within the NeXus metadata using the associated events and descriptors.
        """

        # Check if NEXUS_MD_KEY is contained in the start document
        if NX_MD_KEY not in self._start_doc:
            logger.error(f"The start document does not contain {NX_MD_KEY} dictionary.")
            return

        # Define nexus file dir path
        nx_dir_path: str = self.nx_file_dir_path

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
            logger.exception(f"Error during deepcopy of the start document: {e}")
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
def process_nexus_md(nexus_md: dict, descriptors: dict, events: deque):
    """
    Process the Nexus metadata by replacing placeholders with actual data from events and descriptors.
    """

    if not nexus_md:
        raise ValueError("The dict 'nexus_md' is empty")
    if not descriptors:
        raise ValueError("The deque 'descriptors' is empty")
    if not events:
        raise ValueError("The deque 'events' is empty")

    def process_post_run():
        """
        Processes post-run placeholders within the Nexus metadata, replacing them with actual
        data from the event logs and descriptors.

        This inner function contains several helper functions to:
        - Select the appropriate descriptor based on the device name.
        - Extract the component name from the placeholder.
        - Replace the placeholders in the Nexus metadata with actual event data.
        """

        def get_data_from_descriptor(descriptor: dict, cpt_name: str) -> Optional[dict]:
            """Retrieve data from descriptor configuration"""
            config = descriptor.get('configuration', {})
            for device_name, device_data in config.items():
                data_keys, data, timestamps = map(device_data.get, ['data_keys', 'data', 'timestamps'])
                if data_keys and cpt_name in data_keys:
                    logger.debug(f"Data for component: '{cpt_name}' found in configuration of descriptor: '{descriptor['name']}'")

                    value = data.get(cpt_name)
                    timestamp = timestamps.get(cpt_name)
                    
                    # Determine dtype dynamically for value
                    if isinstance(value, str):
                        value_array = np.array(value, dtype=object)  # Single string, keep object dtype
                    elif isinstance(value, list):
                        # Use object dtype if list contains any strings; otherwise, let NumPy infer
                        dtype = object if any(isinstance(v, str) for v in value) else None
                        value_array = np.array(value, dtype=dtype)
                    else:
                        value_array = np.array(value)  # Let NumPy infer the best dtype
                    
                    # Determine dtype dynamically for timestamp
                    if isinstance(timestamp, str):
                        timestamp_array = np.array(timestamp, dtype=object)
                    elif isinstance(timestamp, list):
                        # Use object dtype if list contains any strings; otherwise, let NumPy infer
                        dtype = object if any(isinstance(t, str) for t in timestamp) else None
                        timestamp_array = np.array(timestamp, dtype=dtype)
                    else:
                        timestamp_array = np.array(timestamp) # Let NumPy infer the best dtype
                    
                    return {
                        'description': data_keys[cpt_name],
                        'data': value_array,
                        'descriptor_cpt_timestamp': timestamp_array
                    }
            return None


        def get_data_from_events(descriptor: dict, events, cpt_name: str) -> Optional[dict]:
            """Retrieve data from events based on descriptor UID."""
            if cpt_name not in descriptor['data_keys']:
                return None

            descriptor_uid = descriptor['uid']
            filtered_events = [evt for evt in events if evt['descriptor'] == descriptor_uid]

            values: list = [evt['data'][cpt_name] for evt in filtered_events if cpt_name in evt['data']]
            timestamps: list = [evt['timestamps'][cpt_name] for evt in filtered_events if cpt_name in evt['timestamps']]
            event_times: list = [evt['time'] for evt in filtered_events]

            # Determine dtype dynamically for values
            if any(isinstance(v, str) for v in values):
                values_array = np.array(values, dtype=object)  # Contains strings → use object
            else:
                values_array = np.array(values)  # Only numbers → NumPy infers dtype

            # Determine dtype dynamically for timestamps
            if any(isinstance(t, str) for t in timestamps):
                timestamps_array = np.array(timestamps, dtype=object)  # Contains strings → use object
            else:
                timestamps_array = np.array(timestamps)  # Only numbers → NumPy infers dtype

            # Determine dtype dynamically for event_times
            if any(isinstance(t, str) for t in event_times):
                event_times_array = np.array(event_times, dtype=object)  # Contains strings → use object
            else:
                event_times_array = np.array(event_times)  # Only numbers → NumPy infers dtype

            # Define data to be returned
            data: dict =  {
                'description': descriptor['data_keys'][cpt_name],
                'data': values_array,
                'events_cpt_timestamps': timestamps_array,
                'events_timestamps': event_times_array
            }
            logger.debug(f"Data for component: '{cpt_name}' found in {len(data['data'])} event(s) of the descriptor: '{descriptor['name']}'")
            return data


        # Define a few helper functions to parse the Nexus tree and replace values with data from the events of the run
        def get_cpt_name_from_placeholder(value: str) -> Optional[str]:
            """
            Extracts the component name from the placeholder string, typically in the form
            of `$post-run:<component_name>`.

            Args:
                value (str): The placeholder string, e.g., "$post-run:a_b_c".
                Pattern matches:
                    $post-run:a_b_c
                    $post-run:a-b-c-d
                    $post-run:a_b-c_d-e
                    $post-run:a
                    $post-run
            Returns:
                str: The component name extracted from the placeholder (e.g., "a_b_c").
                None: If the placeholder does not match the expected pattern.
            """

            POST_RUN_LABEL: str = "$post-run:"
            PATTERN: str = r"^\$post-run(:[a-zA-Z0-9_-]+)?$"

            match = re.search(PATTERN, value)
            if match:
                if len(POST_RUN_LABEL) < len(value):
                    cpt_name: str = value[len(POST_RUN_LABEL):]
                    return cpt_name
                else:
                    return str("")  # Return empty string
            else:
                return None  # Pattern does not match

        def extract_data(descriptors, events, cpt_name) -> dict:
            """Extract data for cpt_name from descriptors, prioritizing non-baseline first."""
            
            def find_data(descriptor) -> Optional[dict]:
                return get_data_from_events(descriptor, events, cpt_name) or get_data_from_descriptor(descriptor, cpt_name)

            # Prioritize non-baseline descriptors
            for descriptor in descriptors:
                if descriptor["name"] != "baseline":
                    if data := find_data(descriptor):
                        return data

            # Check baseline descriptor if no data found so far
            for descriptor in descriptors:
                if descriptor["name"] == "baseline":
                    if data := find_data(descriptor):
                        return data

            # No data found
            raise ValueError(f"No descriptor contains data for the 'cpt_name': {cpt_name}")

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
                cpt_name: Optional[str] = get_cpt_name_from_placeholder(placeholder)
                if cpt_name is None:
                    return obj

                # Define object delimiter. It is expected that ophyd-async will use the same delimiter as ophyd
                obj_delimiter: str = "_"

                # Redefine component name as to be read from the blusky documents (with prefixed device name)
                if str("") == cpt_name:  # The case when there is not cpt_name in the placeholder
                    cpt_name = dev_name
                else:
                    cpt_name: str = dev_name + obj_delimiter + cpt_name

                # Extract data from descriptor for the component
                cpt_data: dict = extract_data(descriptors, events, cpt_name)

                # Component data from descriptor
                data: np.ndarray = cpt_data['data']
                # Component description from descriptor
                desc: dict = cpt_data["description"]

                # Optional transformation on data of data
                if "transformation" in obj:
                    # Execute transformation on events_data
                    if "value" == obj["transformation"]["target"]:
                        expression: str = obj["transformation"]["expression"]
                        data = apply_symbolic_transformation(
                            data, expression
                        )

                # Assign 'data'
                obj["value"] = data

                # Assign 'events_cpt_timestamps'
                if 'events_cpt_timestamps' in cpt_data:
                    obj["events_cpt_timestamps"] = cpt_data["events_cpt_timestamps"]

                # Assign 'events_timestamps'
                if 'events_timestamps' in cpt_data:
                    obj["events_timestamps"] = cpt_data["events_timestamps"]

                # Assign 'descriptor_cpt_timestamp'
                if 'descriptor_cpt_timestamp' in cpt_data:
                    obj["descriptor_cpt_timestamp"] = cpt_data["descriptor_cpt_timestamp"]

                # ----------- Assign all abligatory keys -----------

                # Extract dtype (obligatory key), with fallback to defaults
                dtype = obj.get("dtype", desc.get("dtype", "unknown"))
                if dtype == "number":
                    dtype = "float64"
                elif dtype == "integer":
                    dtype = "int64"
                elif dtype == "string":
                    dtype = "str"
                elif dtype == "array":
                    dtype = obj.get("attrs", {}).get(
                        "dtype", "float64"
                    )  # One lookup for dtype
                elif dtype == "object":
                    dtype = "str"  # Treat object as a string
                # Assign dtype
                obj["dtype"] = dtype

                # Assign shape (obligatory key)
                obj["shape"] = list(data.shape)

                # Ensure "attrs" key exists in obj
                obj.setdefault("attrs", {})

                # Extract and set source (obligatory key)
                obj["attrs"]["source"] = obj["attrs"].get(
                    "source", desc.get("source", "unknown")
                )

                # ----------- Assign all optional keys -----------

                # Extract units (optional key)
                units = obj["attrs"].get("units", desc.get("units", None))
                if units is not None:
                    obj["attrs"]["units"] = units

                # Extract and set external (optional key)
                external = obj["attrs"].get("external", desc.get("external", None))
                if external is not None:
                    obj["attrs"]["external"] = external

                # Extract precision (optional key)
                precision = obj["attrs"].get("precision", desc.get("precision", None))
                if precision is not None:
                    obj["attrs"]["precision"] = precision

                # Extract and set lower_ctrl_limit (optional key)
                lower_ctrl_limit = obj["attrs"].get("lower_ctrl_limit", desc.get("lower_ctrl_limit", None))
                if lower_ctrl_limit is not None:
                    obj["attrs"]["lower_ctrl_limit"] = lower_ctrl_limit

                # Extract and set upper_ctrl_limit (optional key)
                upper_ctrl_limit = obj["attrs"].get("upper_ctrl_limit", desc.get("upper_ctrl_limit", None))
                if upper_ctrl_limit is not None:
                    obj["attrs"]["upper_ctrl_limit"] = upper_ctrl_limit

                # Extract and set enum_strs (optional key)
                enum_strs = obj["attrs"].get("enum_strs", desc.get("enum_strs", None))
                if enum_strs is not None:
                    obj["attrs"]["enum_strs"] = enum_strs

                # Extract and set object_name (optional key)
                object_name = obj["attrs"].get("object_name", desc.get("object_name", None))
                if object_name is not None:
                    obj["attrs"]["object_name"] = object_name

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
                    #if (isinstance(value, dict) and "value" in value and "dtype" in value):
                    if (isinstance(value, dict) and "value" in value):
                        tree[key] = func(dev_name, value)
                    tree[key] = replace_values(dev_name, value, func)
            elif isinstance(tree, list):
                tree = [replace_values(dev_name, item, func) for item in tree]
            return tree

        for dev_name in nexus_md.keys():
            nexus_md[dev_name] = replace_values(dev_name, nexus_md[dev_name], replace_func)

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
            "instrument": {"mono": {"NX_class": "NXmonochromator", "value": 123.4}},
            "run_info": {"start_time": "2023-12-01T12:00:00"},
        }
        create_nexus_file("example.nxs", data)
    """

    with h5py.File(file_path, "w") as f:
        # Create file level attribute
        f.attrs["default"] = "entry"

        # Create the NXentry group
        entry = f.create_group("entry")
        entry.attrs["NX_class"] = "NXentry"
        entry.attrs["Application name"] = "bluesky_nexus"
        entry.attrs["Application version"] = "v1.0.0"
        entry.attrs["Content"] = "'NXinstrument' group and 'NXcollection' group"

        for key, value in data_dict.items():
            # Create instrument group under 'entry' group
            if "instrument" == key:
                # Create instrument group
                instrument_group = entry.create_group(key)
                # Add attribute
                instrument_group.attrs["NX_class"] = "NXinstrument"
                instrument_group.attrs["description"] = "Instruments involved in the bluesky plan"

                # Add group or fieled to instrument_group
                add_group_or_field(instrument_group, value)

            # Create run_info group under 'entry' group
            elif "run_info" == key:
                # Create run_info group
                run_info_group = entry.create_group(key)
                # Add attribute
                run_info_group.attrs["NX_class"] = "NXcollection"
                run_info_group.attrs["description"] = "Copy of the start and stop document from the bluesky run"
                # Write data to the run_info_group
                write_collection(run_info_group, value)

            # Treat everything else as entry metadata
            else:
                if isinstance(value, (str, int, float)):
                    entry.create_dataset(key, data=value)
                elif isinstance(value, (list, np.ndarray)):
                    entry.create_dataset(key, data=np.array(value))

        logger.info(f"NeXus file '{file_path}' created successfully.")


def add_group_or_field(group, data):
    """
    Recursively adds groups or datasets to a NeXus file based on the provided data.

    Parameters:
        group (h5py.Group): The parent group to which fields or subgroups will be added.
        data (dict): A dictionary describing the NeXus structure. Keys represent names
                     of groups or fields, and values provide detailed metadata such as
                     `NX_class`, `value`, `dtype`, and attributes.

    Raises:
        ValueError: If invalid `dtype` is encountered for a dataset.

    Example:
        data = {
            "mono": {
                "NX_class": "NXmonochromator",
                "value": 123.4,
                "dtype": "float64",
                "attrs": {"units": "keV"}
            }
        }
        add_group_or_field(parent_group, data)
    """

    def add_attrs(dataset: h5py.Dataset, attrs: dict) -> None:
        """
        Adds attributes to an h5py dataset, automatically determining their type.

        Parameters:
        - dataset (h5py.Dataset): The dataset to which attributes should be added.
        - attrs (dict): A dictionary where keys are attribute names and values are attribute values.
        """
        for key, value in attrs.items():
            # Automatically determine the type and convert accordingly
            
            if isinstance(value, dict):
                dataset.attrs[key] = str(value)  # Convert dict to str
            
            elif isinstance(value, str):
                dataset.attrs[key] = value  # Save string directly
            
            elif isinstance(value, (int, np.integer)):
                dataset.attrs[key] = np.int64(value)  # Store as int64 (safe for large numbers)
            
            elif isinstance(value, (float, np.floating)):
                dataset.attrs[key] = np.float64(value)  # Store as float64 for precision
            
            elif isinstance(value, bool):
                dataset.attrs[key] = np.bool_(value)  # Store as a NumPy boolean
            
            elif isinstance(value, (list, tuple, np.ndarray)):
                # Convert to NumPy array to ensure consistent storage
                value = np.array(value)
                if value.dtype.kind in {'i', 'u'}:  # Integer types
                    dataset.attrs[key] = value.astype(np.int64)
                elif value.dtype.kind == 'f':  # Floating point types
                    dataset.attrs[key] = value.astype(np.float64)
                elif value.dtype.kind == 'b':  # Boolean array
                    dataset.attrs[key] = value.astype(np.bool_)
                elif value.dtype.kind == 'U' or value.dtype.kind == 'O':  # Strings
                    dataset.attrs[key] = np.array(value, dtype=h5py.special_dtype(vlen=str))
                else:
                    raise ValueError(f"Unsupported array data type for attribute '{key}': {value.dtype}")

            else:
                raise ValueError(f"Unsupported attribute type for '{key}': {type(value)}")

    def add_attributes(target: Union[h5py.Dataset, h5py.Group], attributes: dict) -> None:
        """
        Adds attributes to an HDF5 dataset or group, enforcing dtype if specified.

        Parameters:
        - target Union[h5py.Dataset, h5py.Group]: The dataset or group to which attributes should be added.
        - attributes (dict): A dictionary of attributes to add, each with 'value' and 'dtype' keys.
        """

        for attr_name, attr_data in attributes.items():
            value: Any = attr_data["value"]  # Mandatory, guaranteed by NXfieldModelForAttribute
            dtype_str: str = attr_data["dtype"]  # Expected as a string, facultative for post-run placeholders otherwise mandatory
            
            if dtype_str not in NX_DTYPE_MAP:
                raise ValueError(
                    f"Invalid dtype: {dtype_str} detected while processing {target.name}.{attr_name}."
                )

            try:
                dtype = NX_DTYPE_MAP[dtype_str]

                # Handle strings explicitly
                if dtype in {h5py.string_dtype(encoding="utf-8")}:
                    if isinstance(value, str):
                        value = np.array(value, dtype=dtype)  # Convert scalar string to numpy array
                    elif isinstance(value, (list, tuple, np.ndarray)):
                        value = np.array(value, dtype=dtype)  # Convert list of strings to numpy array
                    else:
                        raise TypeError(f"Unexpected type {type(value)} for string attribute {attr_name}")

                # Handle booleans explicitly
                elif dtype == np.uint8 and isinstance(value, (bool, np.bool_)):
                    value = np.uint8(value)  # Convert single bool to uint8

                # Convert numpy arrays correctly
                elif isinstance(value, np.ndarray):
                    value = value.astype(dtype)

                # Convert scalar values correctly
                else:
                    value = np.array(value, dtype=dtype)

                # Save the attribute
                target.attrs[attr_name] = value

            except Exception as e:
                raise TypeError(f"Failed to convert {value} to dtype {dtype_str}: {e}")

    for key, value in data.items():
        if isinstance(value, dict):

            ###
            ### Handle NeXus fields
            ### value["value"] is in "post-run" case always numpy array
            if "value" in value:
                dtype = value.get("dtype", None)

                if dtype in VALID_NXFIELD_DTYPES:
                    # Handle strings and object dtype explicitly
                    if isinstance(value["value"], np.ndarray) and value["value"].dtype == object:
                        # Check if the array is not 0-dimensional (i.e., scalar)
                        if value["value"].ndim > 0:
                            # Convert np.str_ elements to native Python strings (if any)
                            value["value"] = np.array([str(item) if isinstance(item, np.str_) else item 
                                                       for item in value["value"]], dtype='str')
                        else:
                            # For 0-dimensional arrays, convert np.str_ to a native Python string
                            if isinstance(value["value"], np.str_):
                                value["value"] = str(value["value"])

                    # Handle strings explicitly: encoding="utf-8"
                    if dtype in {"str", "char"} or (
                        isinstance(value["value"], np.ndarray) and
                        value["value"].dtype == object and
                        all(isinstance(item, str) for item in value["value"])
                    ):
                        dtype = h5py.string_dtype(encoding="utf-8")

                        # Extract single string from an ndarray with shape (1,)
                        if isinstance(value["value"], np.ndarray) and value["value"].size == 1:
                            value["value"] = value["value"].item()  # Extracts the scalar string

                    ### Create dataset for 'value'
                    dataset = group.create_dataset(
                        key, data=value["value"], dtype=dtype
                    )

                    # Add attributes to the dataset
                    # In the schema file, attributes of a field are introduced by the word "attributes"
                    # Each attribute has a value and dtype
                    # Attribute of dataset can be: scalar or array
                    # Attribute of dataset can be of type: defined under VALID_NXFIELD_DTYPES
                    if "attributes" in value:
                        add_attributes(dataset, value["attributes"])

                    # Add attribute shape (obligatory)
                    if "shape" in value:
                        dataset.attrs["shape"] = value["shape"]

                    # Add optionally "NX_class" attribute that is not expected by nexus convention for datasets
                    if "nxclass" in value:
                        dataset.attrs["NX_class"] = value["nxclass"]

                    # Add attribute transformation (optional)
                    if "transformation" in value:
                        dataset.attrs["transformation"] = str(value["transformation"]) # convert dict to  string

                    # Add all attributes defined in 'attrs'
                    if "attrs" in value:
                        add_attrs(dataset, value['attrs'])

                    ### Create dataset for 'events_cpt_timestamps'
                    if "events_cpt_timestamps" in value:
                        dataset = group.create_dataset(
                            key + "_timestamps",
                            data=value["events_cpt_timestamps"],
                            dtype=value["events_cpt_timestamps"].dtype,
                        )
                        dataset.attrs["NX_class"] = "NX_FLOAT"
                        dataset.attrs["shape"] = list(value["events_cpt_timestamps"].shape)
                        dataset.attrs["description"] = (
                            f"Timestamps of the component: {key} extracted from the events"
                        )

                    ### Create dataset for 'descriptor_cpt_timestamp'
                    if "descriptor_cpt_timestamp" in value:
                        dataset = group.create_dataset(
                            key + "_timestamp",
                            data=value["descriptor_cpt_timestamp"],
                            dtype=value["descriptor_cpt_timestamp"].dtype,
                        )
                        dataset.attrs["NX_class"] = "NX_FLOAT"
                        dataset.attrs["shape"] = list(value["descriptor_cpt_timestamp"].shape)
                        dataset.attrs["description"] = (
                            f"Timestamp of the component: {key} extracted from the descriptor"
                        )

                    ### Create dataset for 'events_timestamp'
                    if "events_timestamps" in value:
                        # Check if the dataset already exists
                        if "events_timestamps" in group:
                            pass
                        else:
                            # Create the dataset if it does not exist
                            dataset = group.create_dataset(
                                "events_timestamps",
                                data=value["events_timestamps"],
                                dtype=value["events_timestamps"].dtype,
                            )
                            # Add attributes to the dataset
                            dataset.attrs["NX_class"] = "NX_FLOAT"
                            dataset.attrs["shape"] = list(value["events_timestamps"].shape)
                            dataset.attrs["description"] = "Timestamps of the events"

                else:
                    raise ValueError(
                        f"Invalid dtype: {dtype} detected while processing the group: {group.name} and the key: {key}. Check evtl. one of the schema files."
                    )

            ###
            ### Handle NeXus groups
            ###
            elif "nxclass" in value:

                # Create group
                subgroup = group.create_group(key)

                # Add "NX_class" attribute expected by nexus convention for groups
                subgroup.attrs["NX_class"] = value["nxclass"]

                # Add "default" attribute expected by nexus convention for groups if defined for the group
                if "default" in value:
                    subgroup.attrs["default"] = value["default"]["value"] # Presence of “value” in the “default” guaranteed by NXattrModel.

                # Add attributes to the group defined in the schema
                # In the schema file, attributes of a group are introduced by the word "attributes"
                # Each attribute has a value and dtype
                # Attribute of a group can be: integer, float, string, bool, array
                # Attribute of a group can be of type: str, int32, int64, float32, float64, bool
                if "attributes" in value:
                    add_attributes(subgroup, value["attributes"])

                # Add all attributes defined in 'attrs'
                if "attrs" in value:
                    add_attrs(subgroup, value['attrs'])

                # Recursively add fields or subgroups
                add_group_or_field(
                    subgroup,
                    {
                        k: v
                        for k, v in value.items()
                        if k != "nxclass" and k != "default" and k != "attributes" and k != "attrs"
                    },
                )

        else:
            # Handle as attribute of the group
            group.attrs[key] = value
            #print(f"Assign to group attr named {key} the value: {value}") # Debug only

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
            logger.error(f"Unsupported type {type(value)} for key '{key}'")
            raise TypeError(f"ERROR: Unsupported type {type(value)} for key '{key}'")
