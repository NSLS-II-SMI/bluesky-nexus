import ast
import os
import h5py
import numpy as np
import pytest
import types
import unittest
from bluesky import RunEngine
from bluesky.plans import scan, count
from tests.devices.mono import Mono
from tests.devices.monoWithGratingCpt import MonoWithGratingCpt
from tests.devices.sim_motor import SimMotor
from ophyd.sim import motor
from tests.preprocessors.baseline import SupplementalDataBaseline
from typing import Any

from bluesky_nexus.bluesky_nexus_const import NX_FILE_EXTENSION, CALLBACK_FILE_EXTENSION
from bluesky_nexus.callbacks.nexus_writer import NexusWriter
from bluesky_nexus.preprocessors.supplemental_metadata import SupplementalMetadata
from tests.auxiliary.callbacks import WriteToFileFormattedCallback

# Constants: Define paths
NX_FILE_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "nx_file"))
CALLBACK_FILE_DIR_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "callback_file")
)

NX_SCHEMA_DIR_PATH = os.path.abspath(
    os.path.join(os.path.join(os.path.dirname(__file__), "devices"), "nx_schema")
)


# Fixture: Ensure the `nx_file` directory exists
@pytest.fixture
def create_nx_file_dir():
    """
    Creates the `nx_file` directory if it doesn't already exist and cleans up after the tests.
    """
    if not os.path.exists(NX_FILE_DIR_PATH):
        os.makedirs(NX_FILE_DIR_PATH)


# Fixture: Ensure the `callback_file` directory exists
@pytest.fixture
def create_callback_file_dir():
    """
    Creates the `callback_file` directory if it doesn't already exist and cleans up after the tests.
    """
    if not os.path.exists(CALLBACK_FILE_DIR_PATH):
        os.makedirs(CALLBACK_FILE_DIR_PATH)


# Fixture: Get the path to `nx_file` directory
@pytest.fixture
def nx_file_dir_path():
    """
    Returns the absolute path to the `nx_file` directory for storing output files.
    """
    return NX_FILE_DIR_PATH


# Fixture: Get the path to `callback_file` directory
@pytest.fixture
def callback_file_dir_path():
    """
    Returns the absolute path to the `callback_file` directory for storing callback files.
    """
    return CALLBACK_FILE_DIR_PATH


# Test: Example test that writes to `nx_file`
@pytest.mark.skip(reason="Temporarily disabling this test_write_to_nx_file_dir")
def test_write_to_nx_file_dir():
    test_file_path = os.path.join(NX_FILE_DIR_PATH, "test_output.txt")
    with open(test_file_path, "w") as f:
        f.write("This is a test file.")
    assert os.path.exists(test_file_path)


# Test: Ensure the `nx_schema` directory exists
def test_nx_schema_directory_exists():
    """
    Test to ensure that the `nx_schema` directory exists in the same parent directory as this test file.
    """
    assert os.path.isdir(
        NX_SCHEMA_DIR_PATH
    ), f"The directory `nx_schema` does not exist at {NX_SCHEMA_DIR_PATH}"


# Fixture: Get the path to `nx_schema`
@pytest.fixture
def nx_schema_dir_path():
    """
    Returns the absolute path to the `nx_schema` directory for storing schema files.
    """
    return NX_SCHEMA_DIR_PATH


# Constants for the expected files
EXPECTED_FILES = ["mono.py", "monoWithGratingCpt.py"]


# Test: Ensure specific files exist in the `nx_schema` directory
def test_expected_files_exist_in_nx_schema(nx_schema_dir_path):
    """
    Test to ensure that specific files exist in the `nx_schema` directory.

    Expected files:
    - mono.py
    - monoWithGratingCpt.py
    """
    missing_files = []
    for file_name in EXPECTED_FILES:
        file_path = os.path.join(nx_schema_dir_path, file_name)
        if not os.path.isfile(file_path):
            missing_files.append(file_name)

    assert (
        not missing_files
    ), f"The following expected files are missing in the `nx_schema` directory: {', '.join(missing_files)}"


# Fixture: Create a dictionary of devices for reuse in tests
@pytest.fixture
def devices_dictionary():
    """
    Fixture to create and return a dictionary of test devices.
    This includes monochromators with and without grating components.
    """
    mono = Mono(name="mono")
    mono_with_grating_cpt = MonoWithGratingCpt(name="mono_with_grating_cpt")
    sim_motor = SimMotor(name="sim_motor")
    return {
        "mono": mono,
        "mono_with_grating_cpt": mono_with_grating_cpt,
        "sim_motor": sim_motor,
    }


# Fixture: number of scan steps
@pytest.fixture
def scan_step_number():
    """
    Number of plan's steps
    """
    return 10


# Fixture: number of counts
@pytest.fixture
def counts_number():
    """
    Number of counts
    """
    return 10


# Fixture: Baseline configuration for test 1
@pytest.fixture
def baseline_1(devices_dictionary):
    """
    Baseline configuration with both 'mono' and 'mono_with_grating_cpt' devices.
    """

    return [devices_dictionary["mono"], devices_dictionary["mono_with_grating_cpt"]]


# Fixture: Baseline configuration for test 2
@pytest.fixture
def baseline_2(devices_dictionary):
    """
    Baseline configuration with 'mono' device only.
    """

    return [devices_dictionary["mono"]]


# Fixture: Baseline configuration for test 3
@pytest.fixture
def baseline_3(devices_dictionary):
    """
    Baseline configuration with 'mono_with_grating_cpt' device only.
    """

    return [devices_dictionary["mono_with_grating_cpt"]]


# Fixture: Baseline configuration for test 4. Empty baseline.
@pytest.fixture
def baseline_4():
    """
    Empty baseline configuration with no devices.
    """

    return []


# Fixture: Initialize a plain Bluesky RunEngine
@pytest.fixture
def run_engine():
    """
    Initializes and returns a plain Bluesky RunEngine.
    No subscriptions are added yet.
    """
    return RunEngine()


# Fixture: Subscribe NexusWriter callback to the RunEngine
@pytest.fixture
def RE(run_engine: RunEngine, nx_file_dir_path: str):
    """
    Subscribes the NexusWriter callback to a given RunEngine.
    Returns the configured RunEngine.
    """

    nexus_writer = NexusWriter(nx_file_dir_path=nx_file_dir_path)

    run_engine.subscribe(nexus_writer)
    return run_engine


# Fixture: Return ophyd sim motor
@pytest.fixture
def my_motor():
    return motor  # Return the motor object for use in tests


# Helper: Execute a scan plan on the RunEngine
def execute_scan_plan(
    RE: RunEngine,
    md: dict,
    detectors: list[object],
    motor: object,
    scan_step_number: int,
):
    """
    Helper function to define and execute a plan on the RunEngine.
    - Scans detectors over a motor's range with given metadata.
    """

    def scan_plan():
        plan = scan(
            detectors, motor, 1, 10, scan_step_number, md=md
        )  # Start, stop, steps
        assert isinstance(
            plan, types.GeneratorType
        ), "scan() is not returning a generator!"
        yield from plan

    RE(scan_plan())


# Helper: Execute a count plan on the RunEngine
def execute_count_plan(
    RE: RunEngine,
    md: dict,
    detectors: list[object],
    counts_number: int,
):
    """
    Helper function to define and execute a count plan on the RunEngine.
    - Repeats reading the detectors `num_counts` times with provided metadata.
    """

    def count_plan():
        plan = count(detectors, num=counts_number, md=md)
        assert isinstance(
            plan, types.GeneratorType
        ), "count() is not returning a generator!"
        yield from plan

    RE(count_plan())


# Helper: Add preprocessors to the RunEngine for baseline and metadata
def add_preprocessors(RE: RunEngine, devices_dictionary: dict, baseline: list[object]):
    """
    Adds preprocessors to the RunEngine to handle:
    - Baseline devices.
    - Nexus metadata and device metadata for start documents.
    """
    # Append baseline devices
    sdd = SupplementalDataBaseline(baseline=baseline)
    RE.preprocessors.append(sdd)

    # Add Nexus metadata
    metadata = SupplementalMetadata()
    metadata.devices_dictionary = devices_dictionary
    metadata.baseline = baseline
    metadata.md_type = SupplementalMetadata.MetadataType.NEXUS_MD
    RE.preprocessors.append(metadata)

    # Add device metadata
    metadata = SupplementalMetadata()
    metadata.devices_dictionary = devices_dictionary
    metadata.baseline = baseline
    metadata.md_type = SupplementalMetadata.MetadataType.DEVICE_MD
    RE.preprocessors.append(metadata)


# Helper: Generate metadata for the start document
def generate_md(nx_file_name: str, title: str, definition: str, test_dict: dict):
    return {
        "nx_file_name": nx_file_name,  # Facultative
        "title": title,  # Facultative
        "definition": definition,  # Facultative
        "test_dict": test_dict,  # Facultative
    }


# Helper: to get file path to the nexus file
def get_nx_file_path(file_dir_path: str, file_name: str) -> str:
    # Add extension to file name
    if not file_name.endswith(NX_FILE_EXTENSION):
        file_name = file_name + NX_FILE_EXTENSION

    # Define nexus file path
    file_path: str = os.path.join(file_dir_path, file_name)
    return file_path


# Helper: to get file path to the callback file
def get_callback_file_path(file_dir_path: str, file_name: str) -> str:
    # Add extension to file name
    if not file_name.endswith(CALLBACK_FILE_EXTENSION):
        file_name = file_name + CALLBACK_FILE_EXTENSION

    # Define file path
    file_path: str = os.path.join(file_dir_path, file_name)
    return file_path


# Helper: Remove a file
def clean_up(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
    print(f"Proc info: Clean up of file: {file_path} finished.")


# Helper: Verify NeXus file structure and contents
def verify_nexus_file(file_path: str, expected_structure: dict, expected_data: dict):
    """Verify the NeXus file structure and its data."""
    with h5py.File(file_path, "r") as f:

        ###
        ### Verify groups/datasets, i.e. their existence and existence of their attributes
        ###
        for item_path, item_attrs in expected_structure.items():

            # Verify existance of the group/dataset
            keys = item_path.split("/")
            current = f
            for key in keys:
                assert key in current, f"Missing group: {key} in path: {item_path}"
                current = current[key]

            # Verify group/dataset attributes
            for attr_key, attr_value in item_attrs.items():

                # print("attr_key:", attr_key) # Debug only
                # print("attr_value:", attr_value) # Debug only

                # Ckeck if attribute is contained in the group/dataset
                assert (
                    attr_key in current.attrs
                ), f"Missing attribute: {attr_key} in group: {item_path}"

                # Save under a more suitable name
                nexus_value: Any = current.attrs[attr_key]

                # Check value of the attribute
                if isinstance(nexus_value, str) and isinstance(attr_value, str):
                    assert (
                        nexus_value == attr_value
                    ), f"Mismatch in string: Expected {attr_value}, Found {nexus_value}"

                elif isinstance(nexus_value, (int, float)) and isinstance(
                    attr_value, (int, float)
                ):
                    assert np.isclose(
                        nexus_value, attr_value
                    ), f"Mismatch in float: Expected {attr_value}, Found {nexus_value}"

                elif isinstance(nexus_value, np.ndarray) or isinstance(
                    attr_value, list
                ):
                    # Convert lists to NumPy arrays for comparison
                    if isinstance(attr_value, list):
                        attr_value = np.array(attr_value)

                    # Ensure the arrays contain numerical data before using np.allclose
                    if np.issubdtype(nexus_value.dtype, np.number) and np.issubdtype(
                        attr_value.dtype, np.number
                    ):
                        assert np.allclose(
                            nexus_value, attr_value
                        ), f"Mismatch in array: Expected {attr_value}, Found {nexus_value}"
                    else:
                        assert np.array_equal(
                            nexus_value, attr_value
                        ), f"Mismatch in array: Expected {attr_value}, Found {nexus_value}"

                elif (
                    isinstance(nexus_value, str)
                    and nexus_value.startswith("{")
                    and nexus_value.endswith("}")
                ) or isinstance(attr_value, dict):
                    # Convert stringified dictionary to actual dictionary
                    try:
                        nexus_dict = (
                            ast.literal_eval(nexus_value)
                            if isinstance(nexus_value, str)
                            else nexus_value
                        )
                        attr_value_dict = (
                            ast.literal_eval(attr_value)
                            if isinstance(attr_value, str)
                            else attr_value
                        )
                    except (SyntaxError, ValueError):
                        raise ValueError(
                            f"Invalid dictionary format: nexus_value={nexus_value}, attr_value={attr_value}"
                        )

                    assert (
                        nexus_dict == attr_value_dict
                    ), f"Mismatch in dictionary: Expected {attr_value_dict}, Found {nexus_dict}"

                else:
                    assert (
                        nexus_value == attr_value
                    ), f"Mismatch in value: Expected {attr_value}, Found {nexus_value}"

        ###
        ### Verify datasets,i.e: value, dtype, shape
        ###
        for dataset_path, expected_value in expected_data.items():
            # Check if the expected_value is a dictionary (i.e., it may contain dtype, shape, and value)
            if isinstance(expected_value, dict):
                expected_data_value = expected_value.get("value")
                expected_dtype = expected_value.get("dtype")
                expected_shape = expected_value.get("shape")
            else:
                # If expected_value is not a dictionary, it represents just the value to check
                expected_data_value = expected_value
                expected_dtype = None
                expected_shape = None

            keys = dataset_path.split("/")
            current = f
            for key in keys:
                assert (
                    key in current
                ), f"Missing dataset key: {key} in dataset path: {dataset_path}"
                current = current[key]

            if isinstance(current, h5py.Dataset):
                actual_value = current[()]

                # If the dataset contains byte strings, handle them differently
                if isinstance(actual_value, bytes):
                    if expected_shape:
                        assert len(actual_value) == expected_shape[0], (
                            f"Mismatch in byte string shape for dataset: {dataset_path}: "
                            f"Expected {expected_shape}, Found {len(actual_value)}"
                        )
                    assert (
                        actual_value == expected_data_value
                    ), f"Mismatch in dataset: {dataset_path}: Expected {expected_data_value!r}, Found {actual_value!r}"

                else:
                    # Verify dtype
                    if expected_dtype:
                        assert actual_value.dtype == np.dtype(
                            expected_dtype
                        ), f"Mismatch in dtype for dataset: {dataset_path}: Expected {expected_dtype}, Found {actual_value.dtype}"
                    # Verify shape
                    if expected_shape:
                        assert (
                            actual_value.shape == expected_shape
                        ), f"Mismatch in shape for dataset: {dataset_path}: Expected {expected_shape}, Found {actual_value.shape}"
                    # Verify value
                    if expected_data_value:
                        if isinstance(actual_value, np.ndarray):
                            # Convert expected_data_value in np array
                            expected_data_value = np.array(expected_data_value)

                            ### ---------- DEBUG ONLY
                            # Print array info
                            # print_array_info(actual_value, "actual_value")
                            # print_array_info(expected_data_value, "expected_data_value")

                            # Print array comparison info
                            # print_arrays_comparison_info(
                            #     actual_value,
                            #     "actual_value",
                            #     expected_data_value,
                            #     "expected_data_value",
                            # )
                            ### ---------- END OF DEBUG ONLY

                            # Check if the array contains string values
                            if actual_value.dtype.kind == "U":
                                assert np.array_equal(
                                    actual_value,
                                    expected_data_value,
                                ), f"Mismatch in dataset: {dataset_path}: Expected {expected_data_value}, Found {actual_value}"

                            # Check if the array contains numeric values
                            elif (
                                actual_value.dtype.kind == "f"
                                or actual_value.dtype.kind == "i"
                            ):  # 'f' for float, 'i' for integer
                                assert np.allclose(
                                    actual_value,
                                    expected_data_value,
                                    atol=1e-8,  # Use tolerance of 1e-8 (adjust as needed)
                                ), f"Mismatch in dataset: {dataset_path}: Expected {expected_data_value}, Found {actual_value}"

                        else:
                            assert (
                                actual_value == expected_data_value
                            ), f"Mismatch in dataset: {dataset_path}: Expected {expected_data_value}, Found {actual_value}"

            else:
                raise TypeError(f"{dataset_path} is not a dataset")


# Test function
# @unittest.skip("Temporarily disabling this test_1")
def test_1(
    RE,
    devices_dictionary,
    baseline_1,
    my_motor,
    callback_file_dir_path,
    nx_file_dir_path,
    scan_step_number,
    request,
):
    """
    Integration test for generating and varyfing a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a plan and verifies the resulting Nexus file's structure and data.
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_1)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 1",
        "NX_abc",
        {"a": 1, "b": 2, "c": {"d": 3, "e": 4}},
    )

    # Define: callback_writer
    callback_file_path = get_callback_file_path(
        callback_file_dir_path, f"callback_file_{request.node.name}.json"
    )
    callback_writer = WriteToFileFormattedCallback(callback_file_path)
    RE.subscribe(callback_writer)

    # Execute the scan plan
    execute_scan_plan(
        RE, md, [devices_dictionary["mono"].en], my_motor, scan_step_number
    )

    # Close the callback_writer
    callback_writer.close()

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    ###
    ### Verify existence of the groups/fields and their attributes
    ###
    expected_structure: dict = {
        # ---
        # --- group: entry and its attributes ---
        # ---
        "entry": {
            "NX_class": "NXentry",
            "Application name": "bluesky_nexus",
            "Content": "'NXinstrument' group and 'NXcollection' group",
        },
        # ---
        # --- group: entry/instrument and its attributes---
        # ---
        "entry/instrument": {
            "NX_class": "NXinstrument",
            "description": "Instruments involved in the bluesky plan",
        },
        # ---
        # --- group: entry/instrument/mono and its attributes ---
        # ---
        "entry/instrument/mono": {
            "NX_class": "NXmonochromator",
            "nx_model": "NXmonochromatorModel",
            "attr_0": 3.1415,
            "attr_1": {"a": "2"},
            "attr_2": "{'b':'1'}",
            "attr_3": [1.02, 3.04, 5.06],
            "attr_4": [5, 6, 7],
            "attr_5": True,
            "default": "energy",
            "value": "3.1415",
        },
        # ---
        # --- field: entry/instrument/mono/energy and its attributes ---
        # ---
        "entry/instrument/mono/energy": {
            "NX_class": "NX_FLOAT",
            "PI": 3.1415,
            "days": ["Mo", "We"],
            "destination": '{"departement": "A23"}',
            "factors": [1.34, 2.78],
            "object_name": "mono_en",
            "precision": 3,
            "prices": "Euro",
            "shape": [10],
            "source": "SIM:mono_en",
            "transformation": "{'expression': '3 * x**2 + np.exp(np.log(5)) + 1', 'target': 'value'}",
            "units": "keV",
            "value": 12.34,
        },
        # ---
        # --- field: entry/instrument/mono/energy_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/energy_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the component: energy extracted from the events",
        },
        # ---
        # --- field: entry/instrument/mono/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the events",
        },
        # ---
        # --- field: entry/instrument/mono/someDataset and its attributes ---
        # ---
        "entry/instrument/mono/someDataset": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "precision": 3,
            "object_name": "mono_en",
            "source": "SIM:mono_en",
        },
        # ---
        # --- field: entry/instrument/mono/someDataset_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someDataset_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the component: someDataset extracted from the events",
        },
        # ---
        # --- group: entry/instrument/mono/GRATING and its attributes ---
        # ---
        "entry/instrument/mono/GRATING": {
            "NX_class": "NXgrating",
            "attr_0": "new",
            "default": "diffraction_order",
            "value": 167,
        },
        # ---
        # --- dataset: entry/instrument/mono/GRATING/diffraction_order and its attributes ---
        # ---
        "entry/instrument/mono/GRATING/diffraction_order": {
            "NX_class": "NX_INT",
            "at_0": 13.14,
            "at_1": [2.03, 4.05],
            "value": "some_value",
        },
        # ---
        # --- group: entry/instrument/mono/TRANSFORMATIONS and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS": {
            "NX_class": "NXtransformations",
            "attr_0": 3.1415,
            "attr_1": '{"a": "2"}',
            "attr_2": [1.01, 2.02],
            "default": "alpha",
            "value": "3.1",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha": {
            "NX_class": "NX_CHAR",
            "depends_on": "x",
            "equipment_component": "A.71",
            "offset": 34.56,
            "offset_units": "um",
            "units": "um",
            "value": 123,
            "vector": [0, 1, 0],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end": {
            "NX_class": "NX_FLOAT",
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: alpha_end extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set": {
            "NX_class": "NX_INT",
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: alpha_increment_set extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [10],
        },
        # ---
        # --- group: entry/instrument/mono/someGroup and its attributes ---
        # ---
        "entry/instrument/mono/someGroup": {
            "NX_class": "NXsomeClass",
            "attr_1": '{"a": "2"}',
            "attr_2": [5.06, 7.08],
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/energy": {
            "NX_class": "NX_FLOAT",
            "attr_1": "PI",
            "attr_2": 3.1415,
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/energy_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: energy extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [10],
        },
        # ---
        # --- group: entry/instrument/mono_with_grating_cpt and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt": {
            "NX_class": "NXmonochromator",
            "default": "energy",
            "nx_model": "NXmonochromatorModel",
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/energy/ and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy": {
            "NX_class": "NX_FLOAT",
            "currency": "Euro",
            "object_name": "mono_with_grating_cpt",
            "precision": 3,
            "shape": [2],
            "source": "SIM:mono_with_grating_cpt_engry",
            "units": "keV",
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/energy_timestamps and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: energy extracted from the events",
            "shape": [2],
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [2],
        },
        # ---
        # --- group: entry/instrument/mono_with_grating_cpt/GRATING and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING": {
            "NX_class": "NXgrating",
            "default": "diffraction_order",
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order": {
            "NX_class": "NX_INT",
            "object_name": "mono_with_grating_cpt",
            "shape": [2],
            "source": "SIM:mono_with_grating_cpt_grating_diffraction_order",
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order_timestamps and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: diffraction_order extracted from the events",
            "shape": [2],
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [2],
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/substrate_material and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/substrate_material": {
            "NX_class": "NX_CHAR",
        },
        # ---
        # --- group: entry/run_info ---
        # ---
        "entry/run_info": {
            "NX_class": "NXcollection",
            "description": "Copy of the start and stop document from the bluesky run",
        },
        # ---
        # --- groups of: entry/run_info/start ---
        # ---
        "entry/run_info/start": {},
        "entry/run_info/start/device_md/mono": {},
        "entry/run_info/start/device_md/mono_with_grating_cpt": {},
        "entry/run_info/start/hints": {},
        "entry/run_info/start/plan_args": {},
        "entry/run_info/start/plan_pattern_args": {},
        "entry/run_info/start/test_dict": {},
        "entry/run_info/start/versions": {},
        # ---
        # --- groups of: entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    ###
    ### Verify expected data in datasets. I.e. verify: value, dtype, shape
    ###
    expected_data: dict = {
        # ---
        # --- dataset: entry/instrument/mono/energy ---
        # ---
        "entry/instrument/mono/energy": {
            "value": [6.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/energy_timestamps ---
        # ---
        "entry/instrument/mono/energy_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/events_timestamps ---
        # ---
        "entry/instrument/mono/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someDataset ---
        # ---
        "entry/instrument/mono/someDataset": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someDataset_timestamps ---
        # ---
        "entry/instrument/mono/someDataset_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/GRATING/diffraction_order ---
        # ---
        "entry/instrument/mono/GRATING/diffraction_order": {
            "value": 0,
            "dtype": "int32",
            "shape": (),  # Scalar
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha": {
            "value": b"x",
            "shape": (1,),  # Scalar
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set": {
            "value": [0.0] * scan_step_number,
            "dtype": "int32",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/events_timestamps ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy ---
        # ---
        "entry/instrument/mono/someGroup/energy": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy_timestamps ---
        # ---
        "entry/instrument/mono/someGroup/energy_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/events_timestamps ---
        # ---
        "entry/instrument/mono/someGroup/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/description ---
        # ---
        "entry/instrument/mono_with_grating_cpt/description": {
            "value": b"I am the best mono with grating cpt at the bessyii facility",
            "shape": (59,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/energy ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy": {
            "value": [0.0] * 2,
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/energy_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy_timestamps": {
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/events_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/events_timestamps": {
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order": {
            "value": [0.0] * 2,
            "dtype": "int32",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order_timestamps": {
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps": {
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/substrate_material": {
            "value": b"leadless",
            "shape": (8,),
        },
        # ---
        # --- entry/run_info/start ---
        # ---
        "entry/run_info/start/definition": b"NX_abc",
        "entry/run_info/start/detectors": [b"mono_en"],
        "entry/run_info/start/device_md/mono/baseline": b"True",
        "entry/run_info/start/device_md/mono/grating_substrate_material": b"lead",
        "entry/run_info/start/device_md/mono/worldPosition/x": b"1.2000000000000003",
        "entry/run_info/start/device_md/mono/worldPosition/y": b"4.5000000000000006",
        "entry/run_info/start/device_md/mono/worldPosition/z": b"7.8000000000000009",
        "entry/run_info/start/device_md/mono_with_grating_cpt/baseline": b"True",
        "entry/run_info/start/device_md/mono_with_grating_cpt/grating_substrate_material": b"leadless",
        "entry/run_info/start/device_md/mono_with_grating_cpt/worldPosition/x": b"11.120000013",
        "entry/run_info/start/device_md/mono_with_grating_cpt/worldPosition/y": b"14.150000016",
        "entry/run_info/start/device_md/mono_with_grating_cpt/worldPosition/z": b"17.180000019",
        "entry/run_info/start/hints/dimensions": b"[(['motor'], 'primary')]",
        "entry/run_info/start/motors": [b"motor"],
        "entry/run_info/start/num_intervals": scan_step_number - 1,
        "entry/run_info/start/num_points": scan_step_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_args/detectors": [
            b"SynAxis(prefix='', name='mono_en', parent='mono', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])"
        ],
        "entry/run_info/start/plan_args/num": scan_step_number,
        "entry/run_info/start/plan_args/per_step": b"None",
        "entry/run_info/start/plan_name": b"scan",
        "entry/run_info/start/plan_pattern": b"inner_product",
        "entry/run_info/start/plan_pattern_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_pattern_args/num": scan_step_number,
        "entry/run_info/start/plan_pattern_module": b"bluesky.plan_patterns",
        "entry/run_info/start/plan_type": b"generator",
        "entry/run_info/start/scan_id": 1,
        "entry/run_info/start/test_dict/a": 1,
        "entry/run_info/start/test_dict/b": 2,
        "entry/run_info/start/test_dict/c/d": 3,
        "entry/run_info/start/test_dict/c/e": 4,
        "entry/run_info/start/title": b"bluesky run test 1",
        "entry/run_info/start/versions/bluesky": b"1.13",
        "entry/run_info/start/versions/ophyd": b"1.9.0",
        # ---
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop/exit_status": b"success",
        "entry/run_info/stop/num_events/baseline": 2,
        "entry/run_info/stop/num_events/primary": scan_step_number,
        "entry/run_info/stop/reason": b"",
    }

    # Verify file contents
    verify_nexus_file(nx_file_path, expected_structure, expected_data)
    # Remove the nexus file after successful validation
    clean_up(nx_file_path)
    # Remove the callback file after successful creation
    clean_up(callback_file_path)


# Test function
# @unittest.skip("Temporarily disabling this test_2")
def test_2(
    RE,
    devices_dictionary,
    baseline_2,
    my_motor,
    callback_file_dir_path,
    nx_file_dir_path,
    scan_step_number,
    request,
):
    """
    Integration test for generating and validating a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a plan and verifies the resulting Nexus file's structure and data.
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_2)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 2",
        "NX_def",
        {"a": 11, "b": 12, "c": {"d": 13, "e": 14}},
    )

    # Define: callback_writer
    callback_file_path = get_callback_file_path(
        callback_file_dir_path, f"callback_file_{request.node.name}.json"
    )
    callback_writer = WriteToFileFormattedCallback(callback_file_path)
    RE.subscribe(callback_writer)

    # Execute the scan plan
    execute_scan_plan(
        RE, md, [devices_dictionary["mono"].en], my_motor, scan_step_number
    )

    # Close the callback file
    callback_writer.close()

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    ###
    ### Verify existence of the groups/fields and their attributes
    ###
    expected_structure: dict = {
        # ---
        # --- group: entry and its attributes ---
        # ---
        "entry": {
            "NX_class": "NXentry",
            "Application name": "bluesky_nexus",
            "Content": "'NXinstrument' group and 'NXcollection' group",
        },
        # ---
        # --- group: entry/instrument and its attributes---
        # ---
        "entry/instrument": {
            "NX_class": "NXinstrument",
            "description": "Instruments involved in the bluesky plan",
        },
        # ---
        # --- group: entry/instrument/mono and its attributes ---
        # ---
        "entry/instrument/mono": {
            "NX_class": "NXmonochromator",
            "nx_model": "NXmonochromatorModel",
            "attr_0": 3.1415,
            "attr_1": {"a": "2"},
            "attr_2": "{'b':'1'}",
            "attr_3": [1.02, 3.04, 5.06],
            "attr_4": [5, 6, 7],
            "attr_5": True,
            "default": "energy",
            "value": "3.1415",
        },
        # ---
        # --- field: entry/instrument/mono/energy and its attributes ---
        # ---
        "entry/instrument/mono/energy": {
            "NX_class": "NX_FLOAT",
            "PI": 3.1415,
            "days": ["Mo", "We"],
            "destination": '{"departement": "A23"}',
            "factors": [1.34, 2.78],
            "object_name": "mono_en",
            "precision": 3,
            "prices": "Euro",
            "shape": [10],
            "source": "SIM:mono_en",
            "transformation": "{'expression': '3 * x**2 + np.exp(np.log(5)) + 1', 'target': 'value'}",
            "units": "keV",
            "value": 12.34,
        },
        # ---
        # --- field: entry/instrument/mono/energy_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/energy_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the component: energy extracted from the events",
        },
        # ---
        # --- field: entry/instrument/mono/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the events",
        },
        # ---
        # --- field: entry/instrument/mono/someDataset and its attributes ---
        # ---
        "entry/instrument/mono/someDataset": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "precision": 3,
            "object_name": "mono_en",
            "source": "SIM:mono_en",
        },
        # ---
        # --- field: entry/instrument/mono/someDataset_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someDataset_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the component: someDataset extracted from the events",
        },
        # ---
        # --- group: entry/instrument/mono/GRATING and its attributes ---
        # ---
        "entry/instrument/mono/GRATING": {
            "NX_class": "NXgrating",
            "attr_0": "new",
            "default": "diffraction_order",
            "value": 167,
        },
        # ---
        # --- dataset: entry/instrument/mono/GRATING/diffraction_order and its attributes ---
        # ---
        "entry/instrument/mono/GRATING/diffraction_order": {
            "NX_class": "NX_INT",
            "at_0": 13.14,
            "at_1": [2.03, 4.05],
            "value": "some_value",
        },
        # ---
        # --- group: entry/instrument/mono/TRANSFORMATIONS and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS": {
            "NX_class": "NXtransformations",
            "attr_0": 3.1415,
            "attr_1": '{"a": "2"}',
            "attr_2": [1.01, 2.02],
            "default": "alpha",
            "value": "3.1",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha": {
            "NX_class": "NX_CHAR",
            "depends_on": "x",
            "equipment_component": "A.71",
            "offset": 34.56,
            "offset_units": "um",
            "units": "um",
            "value": 123,
            "vector": [0, 1, 0],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end": {
            "NX_class": "NX_FLOAT",
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: alpha_end extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set": {
            "NX_class": "NX_INT",
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: alpha_increment_set extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [10],
        },
        # ---
        # --- group: entry/instrument/mono/someGroup and its attributes ---
        # ---
        "entry/instrument/mono/someGroup": {
            "NX_class": "NXsomeClass",
            "attr_1": '{"a": "2"}',
            "attr_2": [5.06, 7.08],
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/energy": {
            "NX_class": "NX_FLOAT",
            "attr_1": "PI",
            "attr_2": 3.1415,
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/energy_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: energy extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [10],
        },
        # ---
        # --- group: entry/run_info ---
        # ---
        "entry/run_info": {
            "NX_class": "NXcollection",
            "description": "Copy of the start and stop document from the bluesky run",
        },
        # ---
        # --- groups of: entry/run_info/start ---
        # ---
        "entry/run_info/start": {},
        "entry/run_info/start/device_md/mono": {},
        "entry/run_info/start/hints": {},
        "entry/run_info/start/plan_args": {},
        "entry/run_info/start/plan_pattern_args": {},
        "entry/run_info/start/test_dict": {},
        "entry/run_info/start/versions": {},
        # ---
        # --- groups of: entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    ###
    ### Verify expected data in datasets. I.e. verify: value, dtype, shape
    ###
    expected_data: dict = {
        # ---
        # --- dataset: entry/instrument/mono/energy ---
        # ---
        "entry/instrument/mono/energy": {
            "value": [6.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/energy_timestamps ---
        # ---
        "entry/instrument/mono/energy_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/events_timestamps ---
        # ---
        "entry/instrument/mono/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someDataset ---
        # ---
        "entry/instrument/mono/someDataset": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someDataset_timestamps ---
        # ---
        "entry/instrument/mono/someDataset_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/GRATING/diffraction_order ---
        # ---
        "entry/instrument/mono/GRATING/diffraction_order": {
            "value": 0,
            "dtype": "int32",
            "shape": (),  # Scalar
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha": {
            "value": b"x",
            "shape": (1,),  # Scalar
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set": {
            "value": [0.0] * scan_step_number,
            "dtype": "int32",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/events_timestamps ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy ---
        # ---
        "entry/instrument/mono/someGroup/energy": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy_timestamps ---
        # ---
        "entry/instrument/mono/someGroup/energy_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/events_timestamps ---
        # ---
        "entry/instrument/mono/someGroup/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- entry/run_info/start ---
        # ---
        "entry/run_info/start/definition": b"NX_def",
        "entry/run_info/start/detectors": [b"mono_en"],
        "entry/run_info/start/device_md/mono/baseline": b"True",
        "entry/run_info/start/device_md/mono/grating_substrate_material": b"lead",
        "entry/run_info/start/device_md/mono/worldPosition/x": b"1.2000000000000003",
        "entry/run_info/start/device_md/mono/worldPosition/y": b"4.5000000000000006",
        "entry/run_info/start/device_md/mono/worldPosition/z": b"7.8000000000000009",
        "entry/run_info/start/hints/dimensions": b"[(['motor'], 'primary')]",
        "entry/run_info/start/motors": [b"motor"],
        "entry/run_info/start/num_intervals": scan_step_number - 1,
        "entry/run_info/start/num_points": scan_step_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_args/detectors": [
            b"SynAxis(prefix='', name='mono_en', parent='mono', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])"
        ],
        "entry/run_info/start/plan_args/num": scan_step_number,
        "entry/run_info/start/plan_args/per_step": b"None",
        "entry/run_info/start/plan_name": b"scan",
        "entry/run_info/start/plan_pattern": b"inner_product",
        "entry/run_info/start/plan_pattern_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_pattern_args/num": scan_step_number,
        "entry/run_info/start/plan_pattern_module": b"bluesky.plan_patterns",
        "entry/run_info/start/plan_type": b"generator",
        "entry/run_info/start/scan_id": 1,
        "entry/run_info/start/test_dict/a": 11,
        "entry/run_info/start/test_dict/b": 12,
        "entry/run_info/start/test_dict/c/d": 13,
        "entry/run_info/start/test_dict/c/e": 14,
        "entry/run_info/start/title": b"bluesky run test 2",
        "entry/run_info/start/versions/bluesky": b"1.13",
        "entry/run_info/start/versions/ophyd": b"1.9.0",
        # ---
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop/exit_status": b"success",
        "entry/run_info/stop/num_events/baseline": 2,
        "entry/run_info/stop/num_events/primary": scan_step_number,
        "entry/run_info/stop/reason": b"",
    }

    # Verify file contents
    verify_nexus_file(nx_file_path, expected_structure, expected_data)
    # Remove the nexus file after successful validation
    clean_up(nx_file_path)
    # Remove the callback file after successful creation
    clean_up(callback_file_path)


# Test function
# @unittest.skip("Temporarily disabling this test_3")
def test_3(
    RE,
    devices_dictionary,
    baseline_3,
    my_motor,
    callback_file_dir_path,
    nx_file_dir_path,
    scan_step_number,
    request,
):
    """
    Integration test for generating and validating a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a plan and verifiess the resulting Nexus file's structure and data.
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_3)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 3",
        "NX_ghi",
        {"a": 21, "b": 22, "c": {"d": 23, "e": 24}},
    )

    # Define: callback_writer
    callback_file_path = get_callback_file_path(
        callback_file_dir_path, f"callback_file_{request.node.name}.json"
    )
    callback_writer = WriteToFileFormattedCallback(callback_file_path)
    RE.subscribe(callback_writer)

    # Execute the scan plan
    execute_scan_plan(
        RE, md, [devices_dictionary["mono"].en], my_motor, scan_step_number
    )

    # Close the callback file
    callback_writer.close()

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    ###
    ### Verify existence of the groups/fields and their attributes
    ###
    expected_structure: dict = {
        # ---
        # --- group: entry and its attributes ---
        # ---
        "entry": {
            "NX_class": "NXentry",
            "Application name": "bluesky_nexus",
            "Content": "'NXinstrument' group and 'NXcollection' group",
        },
        # ---
        # --- group: entry/instrument and its attributes---
        # ---
        "entry/instrument": {
            "NX_class": "NXinstrument",
            "description": "Instruments involved in the bluesky plan",
        },
        # ---
        # --- group: entry/instrument/mono_with_grating_cpt and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt": {
            "NX_class": "NXmonochromator",
            "default": "energy",
            "nx_model": "NXmonochromatorModel",
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/energy/ and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy": {
            "NX_class": "NX_FLOAT",
            "currency": "Euro",
            "object_name": "mono_with_grating_cpt",
            "precision": 3,
            "shape": [2],
            "source": "SIM:mono_with_grating_cpt_engry",
            "units": "keV",
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/energy_timestamps and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: energy extracted from the events",
            "shape": [2],
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [2],
        },
        # ---
        # --- group: entry/instrument/mono_with_grating_cpt/GRATING and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING": {
            "NX_class": "NXgrating",
            "default": "diffraction_order",
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order": {
            "NX_class": "NX_INT",
            "object_name": "mono_with_grating_cpt",
            "shape": [2],
            "source": "SIM:mono_with_grating_cpt_grating_diffraction_order",
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order_timestamps and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: diffraction_order extracted from the events",
            "shape": [2],
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [2],
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/substrate_material and its attributes ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/substrate_material": {
            "NX_class": "NX_CHAR",
        },
        # ---
        # --- group: entry/run_info ---
        # ---
        "entry/run_info": {
            "NX_class": "NXcollection",
            "description": "Copy of the start and stop document from the bluesky run",
        },
        # ---
        # --- groups of: entry/run_info/start ---
        # ---
        "entry/run_info/start": {},
        "entry/run_info/start/device_md/mono_with_grating_cpt": {},
        "entry/run_info/start/hints": {},
        "entry/run_info/start/plan_args": {},
        "entry/run_info/start/plan_pattern_args": {},
        "entry/run_info/start/test_dict": {},
        "entry/run_info/start/versions": {},
        # ---
        # --- groups of: entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    ###
    ### Verify expected data in datasets. I.e. verify: value, dtype, shape
    ###
    expected_data: dict = {
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/description ---
        # ---
        "entry/instrument/mono_with_grating_cpt/description": {
            "value": b"I am the best mono with grating cpt at the bessyii facility",
            "shape": (59,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/energy ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy": {
            "value": [0.0] * 2,
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/energy_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy_timestamps": {
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/events_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/events_timestamps": {
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order": {
            "value": [0.0] * 2,
            "dtype": "int32",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/diffraction_order_timestamps": {
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps": {
            "dtype": "float64",
            "shape": (2,),
        },
        # ---
        # --- dataset: entry/instrument/mono_with_grating_cpt/GRATING/events_timestamps ---
        # ---
        "entry/instrument/mono_with_grating_cpt/GRATING/substrate_material": {
            "value": b"leadless",
            "shape": (8,),
        },
        # ---
        # --- entry/run_info/start ---
        # ---
        "entry/run_info/start/definition": b"NX_ghi",
        "entry/run_info/start/device_md/mono_with_grating_cpt/baseline": b"True",
        "entry/run_info/start/device_md/mono_with_grating_cpt/grating_substrate_material": b"leadless",
        "entry/run_info/start/device_md/mono_with_grating_cpt/worldPosition/x": b"11.120000013",
        "entry/run_info/start/device_md/mono_with_grating_cpt/worldPosition/y": b"14.150000016",
        "entry/run_info/start/device_md/mono_with_grating_cpt/worldPosition/z": b"17.180000019",
        "entry/run_info/start/hints/dimensions": b"[(['motor'], 'primary')]",
        "entry/run_info/start/motors": [b"motor"],
        "entry/run_info/start/num_intervals": scan_step_number - 1,
        "entry/run_info/start/num_points": scan_step_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_args/detectors": [
            b"SynAxis(prefix='', name='mono_en', parent='mono', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])"
        ],
        "entry/run_info/start/plan_args/num": scan_step_number,
        "entry/run_info/start/plan_args/per_step": b"None",
        "entry/run_info/start/plan_name": b"scan",
        "entry/run_info/start/plan_pattern": b"inner_product",
        "entry/run_info/start/plan_pattern_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_pattern_args/num": scan_step_number,
        "entry/run_info/start/plan_pattern_module": b"bluesky.plan_patterns",
        "entry/run_info/start/plan_type": b"generator",
        "entry/run_info/start/scan_id": 1,
        "entry/run_info/start/test_dict/a": 21,
        "entry/run_info/start/test_dict/b": 22,
        "entry/run_info/start/test_dict/c/d": 23,
        "entry/run_info/start/test_dict/c/e": 24,
        "entry/run_info/start/title": b"bluesky run test 3",
        "entry/run_info/start/versions/bluesky": b"1.13",
        "entry/run_info/start/versions/ophyd": b"1.9.0",
        # ---
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop/exit_status": b"success",
        "entry/run_info/stop/num_events/baseline": 2,
        "entry/run_info/stop/num_events/primary": scan_step_number,
        "entry/run_info/stop/reason": b"",
    }

    # Verify file contents
    verify_nexus_file(nx_file_path, expected_structure, expected_data)
    # Remove the nexus file after successful validation
    clean_up(nx_file_path)
    # Remove the callback file after successful creation
    clean_up(callback_file_path)


# Test function
# @unittest.skip("Temporarily disabling this test_4")
def test_4(
    RE,
    devices_dictionary,
    baseline_4,
    my_motor,
    callback_file_dir_path,
    nx_file_dir_path,
    scan_step_number,
    request,
):
    """
    Integration test for generating and validating a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a plan and verfifies the resulting Nexus file's structure and data.
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_4)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 4",
        "NX_jkl",
        {"a": 31, "b": 32, "c": {"d": 33, "e": 34}},
    )

    # Define: callback_writer
    callback_file_path = get_callback_file_path(
        callback_file_dir_path, f"callback_file_{request.node.name}.json"
    )
    callback_writer = WriteToFileFormattedCallback(callback_file_path)
    RE.subscribe(callback_writer)

    # Execute the scan plan
    execute_scan_plan(
        RE, md, [devices_dictionary["mono"].en], my_motor, scan_step_number
    )

    # Close the callback file
    callback_writer.close()

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    ###
    ### Verify existence of the groups/fields and their attributes
    ###
    expected_structure: dict = {
        # ---
        # --- group: entry and its attributes ---
        # ---
        "entry": {
            "NX_class": "NXentry",
            "Application name": "bluesky_nexus",
            "Content": "'NXinstrument' group and 'NXcollection' group",
        },
        # ---
        # --- group: entry/instrument and its attributes---
        # ---
        "entry/instrument": {
            "NX_class": "NXinstrument",
            "description": "Instruments involved in the bluesky plan",
        },
        # ---
        # --- group: entry/instrument/mono and its attributes ---
        # ---
        "entry/instrument/mono": {
            "NX_class": "NXmonochromator",
            "nx_model": "NXmonochromatorModel",
            "attr_0": 3.1415,
            "attr_1": {"a": "2"},
            "attr_2": "{'b':'1'}",
            "attr_3": [1.02, 3.04, 5.06],
            "attr_4": [5, 6, 7],
            "attr_5": True,
            "default": "energy",
            "value": "3.1415",
        },
        # ---
        # --- field: entry/instrument/mono/energy and its attributes ---
        # ---
        "entry/instrument/mono/energy": {
            "NX_class": "NX_FLOAT",
            "PI": 3.1415,
            "days": ["Mo", "We"],
            "destination": '{"departement": "A23"}',
            "factors": [1.34, 2.78],
            "object_name": "mono_en",
            "precision": 3,
            "prices": "Euro",
            "shape": [10],
            "source": "SIM:mono_en",
            "transformation": "{'expression': '3 * x**2 + np.exp(np.log(5)) + 1', 'target': 'value'}",
            "units": "keV",
            "value": 12.34,
        },
        # ---
        # --- field: entry/instrument/mono/energy_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/energy_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the component: energy extracted from the events",
        },
        # ---
        # --- field: entry/instrument/mono/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the events",
        },
        # ---
        # --- field: entry/instrument/mono/someDataset and its attributes ---
        # ---
        "entry/instrument/mono/someDataset": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "precision": 3,
            "object_name": "mono_en",
            "source": "SIM:mono_en",
        },
        # ---
        # --- field: entry/instrument/mono/someDataset_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someDataset_timestamps": {
            "NX_class": "NX_FLOAT",
            "shape": [10],
            "description": "Timestamps of the component: someDataset extracted from the events",
        },
        # ---
        # --- group: entry/instrument/mono/GRATING and its attributes ---
        # ---
        "entry/instrument/mono/GRATING": {
            "NX_class": "NXgrating",
            "attr_0": "new",
            "default": "diffraction_order",
            "value": 167,
        },
        # ---
        # --- dataset: entry/instrument/mono/GRATING/diffraction_order and its attributes ---
        # ---
        "entry/instrument/mono/GRATING/diffraction_order": {
            "NX_class": "NX_INT",
            "at_0": 13.14,
            "at_1": [2.03, 4.05],
            "value": "some_value",
        },
        # ---
        # --- group: entry/instrument/mono/TRANSFORMATIONS and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS": {
            "NX_class": "NXtransformations",
            "attr_0": 3.1415,
            "attr_1": '{"a": "2"}',
            "attr_2": [1.01, 2.02],
            "default": "alpha",
            "value": "3.1",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha": {
            "NX_class": "NX_CHAR",
            "depends_on": "x",
            "equipment_component": "A.71",
            "offset": 34.56,
            "offset_units": "um",
            "units": "um",
            "value": 123,
            "vector": [0, 1, 0],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end": {
            "NX_class": "NX_FLOAT",
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: alpha_end extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set": {
            "NX_class": "NX_INT",
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: alpha_increment_set extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [10],
        },
        # ---
        # --- group: entry/instrument/mono/someGroup and its attributes ---
        # ---
        "entry/instrument/mono/someGroup": {
            "NX_class": "NXsomeClass",
            "attr_1": '{"a": "2"}',
            "attr_2": [5.06, 7.08],
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/energy": {
            "NX_class": "NX_FLOAT",
            "attr_1": "PI",
            "attr_2": 3.1415,
            "object_name": "mono_en",
            "precision": 3,
            "shape": [10],
            "source": "SIM:mono_en",
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/energy_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the component: energy extracted from the events",
            "shape": [10],
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/events_timestamps and its attributes ---
        # ---
        "entry/instrument/mono/someGroup/events_timestamps": {
            "NX_class": "NX_FLOAT",
            "description": "Timestamps of the events",
            "shape": [10],
        },
        # ---
        # --- group: entry/run_info ---
        # ---
        "entry/run_info": {
            "NX_class": "NXcollection",
            "description": "Copy of the start and stop document from the bluesky run",
        },
        # ---
        # --- groups of: entry/run_info/start ---
        # ---
        "entry/run_info/start": {},
        "entry/run_info/start/device_md/mono": {},
        "entry/run_info/start/hints": {},
        "entry/run_info/start/plan_args": {},
        "entry/run_info/start/plan_pattern_args": {},
        "entry/run_info/start/test_dict": {},
        "entry/run_info/start/versions": {},
        # ---
        # --- groups of: entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    ###
    ### Verify expected data in datasets. I.e. verify: value, dtype, shape
    ###
    expected_data: dict = {
        # ---
        # --- dataset: entry/instrument/mono/energy ---
        # ---
        "entry/instrument/mono/energy": {
            "value": [6.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/energy_timestamps ---
        # ---
        "entry/instrument/mono/energy_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/events_timestamps ---
        # ---
        "entry/instrument/mono/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someDataset ---
        # ---
        "entry/instrument/mono/someDataset": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someDataset_timestamps ---
        # ---
        "entry/instrument/mono/someDataset_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/GRATING/diffraction_order ---
        # ---
        "entry/instrument/mono/GRATING/diffraction_order": {
            "value": 0,
            "dtype": "int32",
            "shape": (),  # Scalar
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha": {
            "value": b"x",
            "shape": (1,),  # Scalar
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_end ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_end_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set": {
            "value": [0.0] * scan_step_number,
            "dtype": "int32",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/alpha_increment_set_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/TRANSFORMATIONS/events_timestamps ---
        # ---
        "entry/instrument/mono/TRANSFORMATIONS/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy ---
        # ---
        "entry/instrument/mono/someGroup/energy": {
            "value": [0.0] * scan_step_number,
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/energy_timestamps ---
        # ---
        "entry/instrument/mono/someGroup/energy_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- dataset: entry/instrument/mono/someGroup/events_timestamps ---
        # ---
        "entry/instrument/mono/someGroup/events_timestamps": {
            "dtype": "float64",
            "shape": (scan_step_number,),
        },
        # ---
        # --- entry/run_info/start ---
        # ---
        "entry/run_info/start/definition": b"NX_jkl",
        "entry/run_info/start/detectors": [b"mono_en"],
        "entry/run_info/start/device_md/mono/baseline": b"True",
        "entry/run_info/start/device_md/mono/grating_substrate_material": b"lead",
        "entry/run_info/start/device_md/mono/worldPosition/x": b"1.2000000000000003",
        "entry/run_info/start/device_md/mono/worldPosition/y": b"4.5000000000000006",
        "entry/run_info/start/device_md/mono/worldPosition/z": b"7.8000000000000009",
        "entry/run_info/start/hints/dimensions": b"[(['motor'], 'primary')]",
        "entry/run_info/start/motors": [b"motor"],
        "entry/run_info/start/num_intervals": scan_step_number - 1,
        "entry/run_info/start/num_points": scan_step_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_args/detectors": [
            b"SynAxis(prefix='', name='mono_en', parent='mono', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])"
        ],
        "entry/run_info/start/plan_args/num": scan_step_number,
        "entry/run_info/start/plan_args/per_step": b"None",
        "entry/run_info/start/plan_name": b"scan",
        "entry/run_info/start/plan_pattern": b"inner_product",
        "entry/run_info/start/plan_pattern_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_pattern_args/num": scan_step_number,
        "entry/run_info/start/plan_pattern_module": b"bluesky.plan_patterns",
        "entry/run_info/start/plan_type": b"generator",
        "entry/run_info/start/scan_id": 1,
        "entry/run_info/start/test_dict/a": 31,
        "entry/run_info/start/test_dict/b": 32,
        "entry/run_info/start/test_dict/c/d": 33,
        "entry/run_info/start/test_dict/c/e": 34,
        "entry/run_info/start/title": b"bluesky run test 4",
        "entry/run_info/start/versions/bluesky": b"1.13",
        "entry/run_info/start/versions/ophyd": b"1.9.0",
        # ---
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop/exit_status": b"success",
        "entry/run_info/stop/num_events/primary": scan_step_number,
        "entry/run_info/stop/reason": b"",
    }

    # Verify file contents
    verify_nexus_file(nx_file_path, expected_structure, expected_data)
    # Remove the nexus file after successful validation
    clean_up(nx_file_path)
    # Remove the callback file after successful creation
    clean_up(callback_file_path)


# Test function
# @unittest.skip("Temporarily disabling this test_5")
def test_5(
    RE,
    devices_dictionary,
    baseline_4,
    callback_file_dir_path,
    nx_file_dir_path,
    counts_number,
    request,
):
    """
    Integration test for generating and validating a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a count plan for a simulated ophyd motor.readback and verfifies the resulting Nexus file's structure and data.
    - sim_motor has deliberately no nx_schema assigned by means of decorator to its class definition
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_4)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 5",
        "NX_mno",
        {"a": 35, "b": 36, "c": {"d": 37, "e": 38}},
    )

    # Define: callback_writer
    callback_file_path = get_callback_file_path(
        callback_file_dir_path, f"callback_file_{request.node.name}.json"
    )
    callback_writer = WriteToFileFormattedCallback(callback_file_path)
    RE.subscribe(callback_writer)

    # Execute the plan
    execute_count_plan(
        RE, md, [devices_dictionary["sim_motor"].readback], counts_number
    )

    # Close the callback file
    callback_writer.close()

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    ###
    ### Verify existence of the groups/fields and their attributes
    ###
    expected_structure: dict = {
        # ---
        # --- group: entry and its attributes ---
        # ---
        "entry": {
            "NX_class": "NXentry",
            "Application name": "bluesky_nexus",
            "Content": "'NXinstrument' group and 'NXcollection' group",
        },
        # ---
        # --- group: entry/instrument and its attributes---
        # ---
        "entry/instrument": {
            "NX_class": "NXinstrument",
            "description": "Instruments involved in the bluesky plan",
        },
        # ---
        # --- group: entry/instrument/mono and its attributes ---
        # ---
        "entry/instrument/sim_motor": {
            "NX_class": "NXsimmotor",
            "nx_model": "NXgeneralModel",
        },
        # ---
        # --- group: entry/run_info ---
        # ---
        "entry/run_info": {
            "NX_class": "NXcollection",
            "description": "Copy of the start and stop document from the bluesky run",
        },
        # ---
        # --- groups of: entry/run_info/start ---
        # ---
        "entry/run_info/start": {},
        "entry/run_info/start/device_md/sim_motor": {},
        "entry/run_info/start/hints": {},
        "entry/run_info/start/plan_args": {},
        "entry/run_info/start/test_dict": {},
        "entry/run_info/start/versions": {},
        # ---
        # --- groups of: entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    ###
    ### Verify expected data in datasets. I.e. verify: value, dtype, shape
    ###
    expected_data: dict = {
        # ---
        # --- entry/run_info/start ---
        # ---
        "entry/run_info/start/detectors": [b"sim_motor"],
        "entry/run_info/start/device_md/sim_motor/baseline": True,
        "entry/run_info/start/device_md/sim_motor/worldPosition/x": b"1.2000000000000003",
        "entry/run_info/start/device_md/sim_motor/worldPosition/y": b"4.5000000000000006",
        "entry/run_info/start/device_md/sim_motor/worldPosition/z": b"7.8000000000000009",
        "entry/run_info/start/hints/dimensions": b"[(('time',), 'primary')]",
        "entry/run_info/start/detectors": [b"sim_motor"],
        "entry/run_info/start/num_intervals": counts_number - 1,
        "entry/run_info/start/num_points": counts_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/num": counts_number,
        "entry/run_info/start/plan_name": b"count",
        "entry/run_info/start/plan_type": b"generator",
        "entry/run_info/start/scan_id": 1,
        "entry/run_info/start/test_dict/a": 35,
        "entry/run_info/start/test_dict/b": 36,
        "entry/run_info/start/test_dict/c/d": 37,
        "entry/run_info/start/test_dict/c/e": 38,
        "entry/run_info/start/title": b"bluesky run test 5",
        "entry/run_info/start/versions/bluesky": b"1.13",
        "entry/run_info/start/versions/ophyd": b"1.9.0",
        # ---
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop/exit_status": b"success",
        "entry/run_info/stop/num_events/primary": counts_number,
        "entry/run_info/stop/reason": b"",
    }

    # Verify file contents
    verify_nexus_file(nx_file_path, expected_structure, expected_data)
    # Remove the nexus file after successful validation
    clean_up(nx_file_path)
    # Remove the callback file after successful creation
    clean_up(callback_file_path)


# ---------- DEBUG ONLY
# Aux function
def print_array_info(arr: np.ndarray, arr_name: str):
    print(f"{arr_name} dtype: {arr.dtype}")
    print(f"{arr_name} value: {arr}")


# Aux function
def print_arrays_comparison_info(
    arr1: np.ndarray, arr1_name: str, arr2: np.ndarray, arr2_name: str
):
    print(f"Is {arr1_name} equal to {arr2_name}: {np.array_equal(arr1, arr2)}")
    print(f"Is {arr1_name} close to {arr2_name}: {np.allclose(arr1, arr2, atol=1e-8)}")


# ---------- END OF DEBUG ONLY

if __name__ == "__main__":
    # Execute all test cases in the script when run directly.
    import pytest

    pytest.main([__file__])
