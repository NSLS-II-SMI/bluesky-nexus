import copy
import os
import re
from collections import deque
from datetime import datetime
from functools import partial
from typing import Optional, Union

import h5py
import numpy as np
import pytz
from bluesky.callbacks.core import CollectThenCompute

from bluesky_nexus.bluesky_nexus_def import _NX_FILE_DIR_PATH

from bluesky_nexus.bluesky_nexus_const import (
    NX_FILE_EXTENSION,
    NX_MD_KEY,
    TIME_ZONE,
    VALID_NXFIELD_DTYPES,
)


class NexusWriter(CollectThenCompute):
    """
    DOC: TO BO DONE
    A callback that writes a Nexus file at the end of a run.
    The Nexus file is created from the start document, descriptors and events of the run.
    The 'nexus' key must be present in the start document.
    """

    def create_nx_file_path(self, dir_path: str, file_name: str) -> str:
        """
        DOCSTRING: TO BO DONE
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
        """
        DOCSTRING TO BO DONE
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
    DOCSTRING TO BO DONE
    Process nexus md from the start doc. I.e. fill all placeholders with data from the events and descriptors
    """

    def process_post_run():
        """
        DOCSTRING: TO BE DONE
        """

        def select_descriptor(descriptors: deque, cpt_name: str) -> Optional[dict]:
            """
            Select an appropriate descriptor for the 'cpt_name':
                - If cpt_name is found in any other descriptor than the 'baseline' descriptor read from this descriptor
                - elif cpt_name is found only in the 'baseline' descriptor read from 'baseline' descriptor
                - else raise exception
                This means taht each instantiated device whose schema contains '$post-run' placeholder has to be included into a baseline.
                Otherwise if such an instantiated device is not used in a plan, the descriptor will not be found and exception will be raised
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
            # Pattern matches
            # $post-run:events:a_b_c
            # $post-run:events:a-b-c-d
            # $post-run:events:a_b-c_d-e
            # $post-run:events:a
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
            DOCSTRING TO DO
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
                # Assign the result to the object's value
                obj["value"] = events_data

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
            if isinstance(tree, dict):
                for key, value in tree.items():
                    if (
                        isinstance(value, dict)
                        and "nxclass" in value
                        and value["nxclass"] == "NXfield"
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
    DOCSTRING: TO BE DONE
    Aux function:
    Get from the start and stop document some run info and return them as a dictionary
    """

    result: dict = {}

    def set(
        result: dict,
        doc: dict,
        doc_key: str,
        entry_key: str,
        transform_func=None,
        *args,
        **kwargs,
    ):
        """
        start: dict start document
        stop: dict stop document
        """

        try:
            value = doc[doc_key]  # Get the value from start dictionary
            if transform_func:
                value = transform_func(
                    value, *args, **kwargs
                )  # Apply the transformation with extra arguments
            result[entry_key] = value  # Assign to the entry
        except KeyError:
            if doc == start:  # Assuming 'start' is the start dictionary
                doc_name = "start"
            elif doc == stop:  # Assuming 'stop' is the stop dictionary
                doc_name = "stop"
            else:
                doc_name = "unknown"  # Fallback for unexpected cases

            print(
                f"WARNING_MSG: The key '{doc_key}' not found in the {doc_name} document."
            )
        except Exception as e:
            print(
                f"ERROR_MSG: An error occurred when processing the key '{doc_key}': {e}"
            )

    def transform_timestamp(timestamp, timezone_str):
        """
        Auxiliary time convertion function
        """
        # Convert the Unix timestamp to an ISO 8601 formatted string in the given timezone
        tz = pytz.timezone(timezone_str)
        return datetime.fromtimestamp(timestamp, tz=tz).isoformat()

    # ----------- Insert into the 'result' dictionary the selected data from the start document -----------

    # 'plan_name'
    key: str = "plan_name"
    set(result, start, key, key)

    # 'scan_id'
    key: str = "scan_id"
    set(result, start, key, key)

    # 'uid'
    start_key: str = "uid"
    entry_key: str = "start_uid"
    set(result, start, start_key, entry_key)

    # 'title'
    key: str = "title"
    set(result, start, key, key)

    # 'definition'
    key: str = "definition"
    set(result, start, key, key)

    # 'time'
    transform_func = partial(
        transform_timestamp, timezone_str=TIME_ZONE
    )  # Prepare a partial function with the required timezone as an argument
    start_key: str = "time"
    entry_key: str = "start_time"
    set(result, start, start_key, entry_key, transform_func=transform_func)

    # ----------- Insert into the 'result' dictionary the selected data from the stop document -----------

    # 'uid'
    stop_key: str = "uid"
    entry_key: str = "stop_uid"
    set(result, stop, stop_key, entry_key)

    # 'time'
    transform_func = partial(
        transform_timestamp, timezone_str=TIME_ZONE
    )  # Prepare a partial function with the required timezone as an argument
    stop_key: str = "time"
    entry_key: str = "stop_time"
    set(result, stop, stop_key, entry_key, transform_func=transform_func)

    # 'exit_status'
    key: str = "exit_status"
    set(result, stop, key, key)

    # 'reason'
    key: str = "reason"
    set(result, stop, key, key)

    return result


def create_nexus_file(file_path, data_dict):
    with h5py.File(file_path, "w") as f:
        f.attrs["default"] = "entry"  # File-level attribute

        # Create the NXentry group
        entry = f.create_group("entry")
        entry.attrs["NX_class"] = "NXentry"
        entry.attrs["default"] = "data"

        # Process data_dict
        for key, value in data_dict.items():
            if key in ["instrument"]:
                group = entry.create_group(key)
                group.attrs["NX_class"] = f"NX{key}"
                create_nexus_group(group, key, value, False)
            elif key == "run_info":
                group = entry.create_group(key)
                group.attrs["NX_class"] = "NXcollection"
                for subkey, subvalue in value.items():
                    group.create_dataset(subkey, data=subvalue)
            else:
                # Treat everything else as entry metadata
                if isinstance(value, (str, int, float)):
                    entry.create_dataset(key, data=value)
                elif isinstance(value, (list, np.ndarray)):
                    entry.create_dataset(key, data=np.array(value))

        print(f"NeXus file '{file_path}' created successfully.")


def create_nexus_group(parent_group, name, data, create_subgroup):
    if create_subgroup:
        subgroup = parent_group.create_group(name)
    else:
        subgroup = parent_group

    if "nxclass" in data:
        subgroup.attrs["NX_class"] = data["nxclass"]
    if "attrs" in data:
        for attr_key, attr_value in data["attrs"].items():
            subgroup.attrs[attr_key] = attr_value
    if "default" in data:
        subgroup.attrs["default"] = data["default"]["value"]

    for key, value in data.items():
        if isinstance(value, dict):
            if key not in ["attrs", "default"]:
                create_nexus_group(subgroup, key, value, True)
        elif key == "value":
            dtype = data.get("dtype", None)
            if dtype in VALID_NXFIELD_DTYPES:
                if "str" == dtype or "char" == dtype:
                    dtype = h5py.string_dtype(encoding="utf-8")
                ds = subgroup.create_dataset(name, data=value, dtype=dtype)
                if "units" in data.get("attrs", {}):
                    ds.attrs["units"] = data["attrs"]["units"]
            else:
                raise ValueError(
                    f"Invalid dtype: {dtype} detected in the subgroup: {subgroup.name}."
                )
        else:
            subgroup.attrs[key] = value
