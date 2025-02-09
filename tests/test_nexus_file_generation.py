import os

import h5py
import numpy as np
import pytest
import types
import unittest
from bluesky import RunEngine
from bluesky.plans import scan
from devices.monochromators import Mono, MonoWithGratingCpt, MonoWithStrCpt
from ophyd.sim import motor
from preprocessors.baseline import SupplementalDataBaseline

from bluesky_nexus.bluesky_nexus_const import NX_FILE_EXTENSION
from bluesky_nexus.callbacks.nexus_writer import NexusWriter
from bluesky_nexus.preprocessors.supplemental_metadata import SupplementalMetadata

# Constants: Define paths
NX_FILE_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "nx_file"))
NX_SCHEMA_DIR_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "nx_schema")
)


# Fixture: Ensure the `nx_file` directory exists
@pytest.fixture
def create_nx_file_dir():
    """
    Creates the `nx_file` directory if it doesn't already exist and cleans up after the tests.
    """
    if not os.path.exists(NX_FILE_DIR_PATH):
        os.makedirs(NX_FILE_DIR_PATH)


# Fixture: Get the path to `nx_file`
@pytest.fixture
def nx_file_dir_path():
    """
    Returns the absolute path to the `nx_file` directory for storing output files.
    """
    return NX_FILE_DIR_PATH


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
EXPECTED_FILES = ["nx_schema_mono.yml", "nx_schema_mono_with_grating_cpt.yml"]


# Test: Ensure specific files exist in the `nx_schema` directory
def test_expected_files_exist_in_nx_schema(nx_schema_dir_path):
    """
    Test to ensure that specific files exist in the `nx_schema` directory.

    Expected files:
    - nx_schema_mono.yml
    - nx_schema_mono_with_grating_cpt.yml
    """
    missing_files = []
    for file_name in EXPECTED_FILES:
        file_path = os.path.join(nx_schema_dir_path, file_name)
        if not os.path.isfile(file_path):
            missing_files.append(file_name)

    assert not missing_files, f"The following expected files are missing in the `nx_schema` directory: {', '.join(missing_files)}"


# Fixture: Create a dictionary of devices for reuse in tests
@pytest.fixture
def devices_dictionary():
    """
    Fixture to create and return a dictionary of test devices.
    This includes monochromators with and without grating components.
    """
    mono = Mono(name="mono")
    mono_with_grating_cpt = MonoWithGratingCpt(name="mono_with_grating_cpt")
    mono_with_str_cpt = MonoWithStrCpt(name="mono_with_str_cpt")
    return {"mono": mono, "mono_with_grating_cpt": mono_with_grating_cpt, "mono_with_str_cpt": mono_with_str_cpt}


# Fixture: number of plan's steps
@pytest.fixture
def plan_step_number():
    """
    Number of plan's steps
    """
    return 10


# Fixture: Baseline configuration for test 1
@pytest.fixture
def baseline_1(devices_dictionary):
    """
    Baseline configuration with both 'mono' and 'mono_with_grating_cpt' devices.
    """

    return [devices_dictionary["mono"], devices_dictionary["mono_with_grating_cpt"], devices_dictionary["mono_with_str_cpt"]]


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


# Helper: Execute a plan on the RunEngine
def execute_plan(RE: RunEngine, md: dict, detectors: list[object], motor: object, plan_step_number: int):
    """
    Helper function to define and execute a plan on the RunEngine.
    - Scans detectors over a motor's range with given metadata.
    """

    def scan_plan():
        plan = scan(detectors, motor, 1, 10, plan_step_number, md=md)  # Start, stop, steps
        assert isinstance(plan, types.GeneratorType), "scan() is not returning a generator!"
        yield from plan
        
    RE(scan_plan())


# Helper: Add preprocessors to the RunEngine for baseline and metadata
def add_preprocessors(
    RE: RunEngine,
    devices_dictionary: dict,
    baseline: list[object],
    nx_schema_dir_path: str,
):
    """
    Adds preprocessors to the RunEngine to handle:
    - Baseline devices.
    - Nexus metadata and device metadata for start documents.
    """
    # Append baseline devices
    sdd = SupplementalDataBaseline(baseline=baseline)
    RE.preprocessors.append(sdd)

    # Add Nexus metadata
    metadata = SupplementalMetadata(nx_schema_dir_path=nx_schema_dir_path)
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
def get_nx_file_path(nx_file_dir_path: str, nx_file_name: str) -> str:
    # Add extension to file name
    if not nx_file_name.endswith(NX_FILE_EXTENSION):
        nx_file_name = nx_file_name + NX_FILE_EXTENSION

    # Define nexus file path
    file_path: str = os.path.join(nx_file_dir_path, nx_file_name)
    return file_path


# Helper: Remove a file
def clean_up(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
    print(f"Proc info: Clean up of file: {file_path} finished.")


# Helper: Validate Nexus file structure and contents
def validate_nexus_file(file_path: str, expected_structure: dict, expected_data: dict):
    """Validate the Nexus file structure and its data."""
    with h5py.File(file_path, "r") as f:
        # Validate structure
        for group_path, group_attrs in expected_structure.items():
            keys = group_path.split("/")
            current = f
            for key in keys:
                assert key in current, f"Missing group: {key} in path: {group_path}"
                current = current[key]

            # Validate group attributes
            for attr_key, attr_value in group_attrs.items():
                assert (
                    attr_key in current.attrs
                ), f"Missing attribute: {attr_key} in group: {group_path}"

                # Convert to str since e.g. expected transformation
                # is a dictionary and transformation read from nxs file is a string
                assert str(current.attrs[attr_key]) == str(attr_value), (
                    f"Mismatch in attribute: {attr_key} in group: {group_path}: "
                    f"Expected {attr_value}, Found {current.attrs[attr_key]}"
                )

        # Validate datasets
        for dataset_path, expected_value in expected_data.items():
            # Check if the expected_value is a dictionary (i.e., it may contain dtype, shape, and value)
            if isinstance(expected_value, dict):
                expected_data_value = expected_value.get("value")
                expected_dtype = expected_value.get("dtype")
                expected_shape = expected_value.get("shape")
                expected_attrs = expected_value.get("attrs", {})
            else:
                # If expected_value is not a dictionary, it represents just the value to check
                expected_data_value = expected_value
                expected_dtype = None
                expected_shape = None
                expected_attrs = {}

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
                    ), f"Mismatch in dataset: {dataset_path}: Expected {expected_data_value}, Found {actual_value}"

                else:
                    # Validate dtype
                    if expected_dtype:
                        assert (
                            actual_value.dtype == np.dtype(expected_dtype)
                        ), f"Mismatch in dtype for dataset: {dataset_path}: Expected {expected_dtype}, Found {actual_value.dtype}"
                    # Validate shape
                    if expected_shape:
                        assert (
                            actual_value.shape == expected_shape
                        ), f"Mismatch in shape for dataset: {dataset_path}: Expected {expected_shape}, Found {actual_value.shape}"
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
                            actual_value.dtype.kind == "fi"
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

                # Validate attributes
                for attr_name, expected_attr_value in expected_attrs.items():
                    assert (
                        attr_name in current.attrs
                    ), f"Missing attribute: {attr_name} in dataset {dataset_path}"
                    assert current.attrs[attr_name] == expected_attr_value, (
                        f"Mismatch in attribute: {attr_name} for {dataset_path}: "
                        f"Expected {expected_attr_value}, Found {current.attrs[attr_name]}"
                    )

            else:
                raise TypeError(f"{dataset_path} is not a dataset")


# Test function
# @unittest.skip("Temporarily disabling this test_1")
def test_1(
    RE,
    devices_dictionary,
    baseline_1,
    my_motor,
    nx_file_dir_path,
    nx_schema_dir_path,
    plan_step_number,
    request,
):
    """
    Integration test for generating and validating a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a plan and validates the resulting Nexus file's structure and data.
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_1, nx_schema_dir_path)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 1",
        "NX_abc",
        {"a": 1, "b": 2, "c": {"d": 3, "e": 4}},
    )

    # Execute the plan
    execute_plan(RE, md, [devices_dictionary["mono"].en], my_motor, plan_step_number)

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    # Expected structure
    expected_structure: dict = {
        # ---
        # --- entry/instrument ---
        # ---
        "entry": {"NX_class": "NXentry"},
        "entry/instrument": {"NX_class": "NXinstrument"},
        # ---
        # --- entry/instrument/mono ---
        # ---
        "entry/instrument/mono": {"NX_class": "NXmonochromator"},
        "entry/instrument/mono/energy": {
            "nxclass": "NX_FLOAT",
            "description": "Energy value",
            "transformation": {
                "expression": "3 * x**2 + np.exp(np.log(5)) + 1",
                "target": "value",
                "description": "Transformation configuration that applies a symbolic operation to the target data array.",
            },
        },
        "entry/instrument/mono/energy_timestamps": {"nxclass": "NX_FLOAT"},
        "entry/instrument/mono/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono/grating": {
            "NX_class": "NXgrating",
            "description": "Grating",
        },
        "entry/instrument/mono/grating/diffraction_order": {
            "nxclass": "NX_INT",
            "description": "Diffraction order value",
        },
        # ---
        # --- entry/instrument/mono_with_grating_cpt ---
        # ---
        "entry/instrument/mono_with_grating_cpt": {"NX_class": "NXmonochromator"},
        "entry/instrument/mono_with_grating_cpt/energy": {
            "nxclass": "NX_FLOAT",
            "description": "Energy value",
        },
        "entry/instrument/mono_with_grating_cpt/energy_timestamps": {
            "nxclass": "NX_FLOAT"
        },
        "entry/instrument/mono_with_grating_cpt/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono_with_grating_cpt/grating": {"NX_class": "NXgrating"},
        "entry/instrument/mono_with_grating_cpt/grating/diffraction_order": {
            "nxclass": "NX_INT"
        },
        "entry/instrument/mono_with_grating_cpt/grating/diffraction_order_timestamps": {
            "nxclass": "NX_FLOAT"
        },
        "entry/instrument/mono_with_grating_cpt/grating/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono_with_grating_cpt/grating/substrate_material": {
            "nxclass": "NX_CHAR",
            "description": "Substrate material type",
        },
        # ---
        # --- entry/instrument/mono_with_str_cpt ---
        # ---
        "entry/instrument/mono_with_str_cpt": {"NX_class": "NXmonochromator"},
        "entry/instrument/mono_with_str_cpt/energy": {
            "nxclass": "NX_FLOAT",
            "description": "Energy value",
        },
        "entry/instrument/mono_with_str_cpt/energy_timestamps": {
            "nxclass": "NX_FLOAT"
        },
        "entry/instrument/mono_with_str_cpt/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono_with_str_cpt/grating": {"NX_class": "NXgrating"},
        "entry/instrument/mono_with_str_cpt/grating/diffraction_order": {
            "nxclass": "NX_INT"
        },
        "entry/instrument/mono_with_str_cpt/grating/diffraction_order_timestamps": {
            "nxclass": "NX_FLOAT"
        },
        "entry/instrument/mono_with_str_cpt/grating/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono_with_str_cpt/grating/substrate_material": {
            "nxclass": "NX_CHAR",
            "description": "Substrate material type",
        },
        # ---
        # --- entry/run_info ---
        # ---
        "entry/run_info": {"NX_class": "NXcollection"},
        # ---
        # --- entry/run_info/start ---
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
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    # Expected data
    expected_data: dict = {
        # ---
        # --- entry/instrument/mono ---
        # ---
        "entry/instrument/mono/energy": {
            "value": [6.0] * plan_step_number,
            "dtype": "float64",
            "shape": (plan_step_number,),
            "attrs": {
                "units": "keV",  # Expected units
            },
        },
        "entry/instrument/mono/grating/diffraction_order": {
            "value": 0,
            "dtype": "int32",
            "shape": (),  # Scalar
        },
        # ---
        # --- entry/instrument/mono_with_grating_cpt ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy": {
            "value": [0, 0],
            "dtype": "float64",
            "shape": (2,),
        },
        "entry/instrument/mono_with_grating_cpt/grating/diffraction_order": {
            "value": [0, 0],
            "dtype": "int32",
            "shape": (2,),
        },
        "entry/instrument/mono_with_grating_cpt/grating/substrate_material": {
            "value": b"leadless",
            "shape": (8,),  # Adjust the shape to match the actual string length
        },
        # ---
        # --- entry/instrument/mono_with_str_cpt ---
        # ---
        "entry/instrument/mono_with_str_cpt/energy": {
            "value": [6.0, 6.0],
            "dtype": "float64",
            "shape": (2,),
        },
        "entry/instrument/mono_with_str_cpt/grating/diffraction_order": {
            "value": [0, 0],
            "dtype": "int32",
            "shape": (2,),
        },
        "entry/instrument/mono_with_str_cpt/grating/substrate_material": {
            "value": b"leadless",
            "shape": (8,),  # Adjust the shape to match the actual string length
        },
        "entry/instrument/mono_with_str_cpt/slit": {
            "value": b"default_value",
            "shape": (13,),  # Adjust the shape to match the actual string length
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
        "entry/run_info/start/num_intervals": plan_step_number - 1,
        "entry/run_info/start/num_points": plan_step_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_args/detectors": [
            b"SynAxis(prefix='', name='mono_en', parent='mono', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])"
        ],
        "entry/run_info/start/plan_args/num": plan_step_number,
        "entry/run_info/start/plan_args/per_step": b"None",
        "entry/run_info/start/plan_name": b"scan",
        "entry/run_info/start/plan_pattern": b"inner_product",
        "entry/run_info/start/plan_pattern_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_pattern_args/num": plan_step_number,
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
        "entry/run_info/stop/num_events/primary": plan_step_number,
        "entry/run_info/stop/reason": b"",
    }

    # Validate file contents
    validate_nexus_file(nx_file_path, expected_structure, expected_data)

    # Remove the nexus file after successful validation
    clean_up(nx_file_path)


# Test function
# @unittest.skip("Temporarily disabling this test_2")
def test_2(
    RE,
    devices_dictionary,
    baseline_2,
    my_motor,
    nx_file_dir_path,
    nx_schema_dir_path,
    plan_step_number,
    request,
):
    """
    Integration test for generating and validating a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a plan and validates the resulting Nexus file's structure and data.
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_2, nx_schema_dir_path)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 2",
        "NX_def",
        {"a": 11, "b": 12, "c": {"d": 13, "e": 14}},
    )

    # Execute the plan
    execute_plan(RE, md, [devices_dictionary["mono"].en], my_motor, plan_step_number)

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    # Expected structure
    expected_structure: dict = {
        # ---
        # --- entry/instrument ---
        # ---
        "entry": {"NX_class": "NXentry"},
        "entry/instrument": {"NX_class": "NXinstrument"},
        # ---
        # --- entry/instrument/mono ---
        # ---
        "entry/instrument/mono": {"NX_class": "NXmonochromator"},
        "entry/instrument/mono/energy": {
            "nxclass": "NX_FLOAT",
            "description": "Energy value",
            "transformation": {
                "expression": "3 * x**2 + np.exp(np.log(5)) + 1",
                "target": "value",
                "description": "Transformation configuration that applies a symbolic operation to the target data array.",
            },
        },
        "entry/instrument/mono/energy_timestamps": {"nxclass": "NX_FLOAT"},
        "entry/instrument/mono/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono/grating": {
            "NX_class": "NXgrating",
            "description": "Grating",
        },
        "entry/instrument/mono/grating/diffraction_order": {
            "nxclass": "NX_INT",
            "description": "Diffraction order value",
        },
        # ---
        # --- entry/run_info ---
        # ---
        "entry/run_info": {"NX_class": "NXcollection"},
        # ---
        # --- entry/run_info/start ---
        # ---
        "entry/run_info/start": {},
        "entry/run_info/start/device_md/mono": {},
        "entry/run_info/start/hints": {},
        "entry/run_info/start/plan_args": {},
        "entry/run_info/start/plan_pattern_args": {},
        "entry/run_info/start/test_dict": {},
        "entry/run_info/start/versions": {},
        # ---
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    # Expected data
    expected_data: dict = {
        # ---
        # --- entry/instrument/mono ---
        # ---
        "entry/instrument/mono/energy": {
            "value": [6.0] * plan_step_number,
            "dtype": "float64",
            "shape": (plan_step_number,),
            "attrs": {
                "units": "keV",  # Expected units
            },
        },
        "entry/instrument/mono/grating/diffraction_order": {
            "value": 0,
            "dtype": "int32",
            "shape": (),  # Scalar
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
        "entry/run_info/start/num_intervals": plan_step_number - 1,
        "entry/run_info/start/num_points": plan_step_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_args/detectors": [
            b"SynAxis(prefix='', name='mono_en', parent='mono', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])"
        ],
        "entry/run_info/start/plan_args/num": plan_step_number,
        "entry/run_info/start/plan_args/per_step": b"None",
        "entry/run_info/start/plan_name": b"scan",
        "entry/run_info/start/plan_pattern": b"inner_product",
        "entry/run_info/start/plan_pattern_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_pattern_args/num": plan_step_number,
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
        "entry/run_info/stop/num_events/primary": plan_step_number,
        "entry/run_info/stop/reason": b"",
    }

    # Validate file contents
    validate_nexus_file(nx_file_path, expected_structure, expected_data)

    # Remove the nexus file after successful validation
    clean_up(nx_file_path)


# Test function
# @unittest.skip("Temporarily disabling this test_3")
def test_3(
    RE,
    devices_dictionary,
    baseline_3,
    my_motor,
    nx_file_dir_path,
    nx_schema_dir_path,
    plan_step_number,
    request,
):
    """
    Integration test for generating and validating a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a plan and validates the resulting Nexus file's structure and data.
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_3, nx_schema_dir_path)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 3",
        "NX_ghi",
        {"a": 21, "b": 22, "c": {"d": 23, "e": 24}},
    )

    # Execute the plan
    execute_plan(RE, md, [devices_dictionary["mono"].en], my_motor, plan_step_number)

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    # Expected structure
    expected_structure: dict = {
        # ---
        # --- entry/instrument ---
        # ---
        "entry": {"NX_class": "NXentry"},
        "entry/instrument": {"NX_class": "NXinstrument"},
        # ---
        # --- entry/instrument/mono ---
        # ---
        "entry/instrument/mono": {"NX_class": "NXmonochromator"},
        "entry/instrument/mono/energy": {
            "nxclass": "NX_FLOAT",
            "description": "Energy value",
            "transformation": {
                "expression": "3 * x**2 + np.exp(np.log(5)) + 1",
                "target": "value",
                "description": "Transformation configuration that applies a symbolic operation to the target data array.",
            },
        },
        "entry/instrument/mono/energy_timestamps": {"nxclass": "NX_FLOAT"},
        "entry/instrument/mono/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono/grating": {
            "NX_class": "NXgrating",
            "description": "Grating",
        },
        "entry/instrument/mono/grating/diffraction_order": {
            "nxclass": "NX_INT",
            "description": "Diffraction order value",
        },
        # ---
        # --- entry/instrument/mono_with_grating_cpt ---
        # ---
        "entry/instrument/mono_with_grating_cpt": {"NX_class": "NXmonochromator"},
        "entry/instrument/mono_with_grating_cpt/energy": {"nxclass": "NX_FLOAT"},
        "entry/instrument/mono_with_grating_cpt/energy_timestamps": {
            "nxclass": "NX_FLOAT"
        },
        "entry/instrument/mono_with_grating_cpt/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono_with_grating_cpt/grating": {"NX_class": "NXgrating"},
        "entry/instrument/mono_with_grating_cpt/grating/diffraction_order": {
            "nxclass": "NX_INT"
        },
        "entry/instrument/mono_with_grating_cpt/grating/diffraction_order_timestamps": {
            "nxclass": "NX_FLOAT"
        },
        "entry/instrument/mono_with_grating_cpt/grating/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono_with_grating_cpt/grating/substrate_material": {
            "nxclass": "NX_CHAR",
            "description": "Substrate material type",
        },
        # ---
        # --- entry/run_info ---
        # ---
        "entry/run_info": {"NX_class": "NXcollection"},
        # ---
        # --- entry/run_info/start ---
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
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    # Expected data
    expected_data: dict = {
        # ---
        # --- entry/instrument/mono ---
        # ---
        "entry/instrument/mono/energy": {
            "value": [6.0] * plan_step_number,
            "dtype": "float64",
            "shape": (plan_step_number,),
            "attrs": {
                "units": "keV",  # Expected units
            },
        },
        "entry/instrument/mono/grating/diffraction_order": {
            "value": 0,
            "dtype": "int32",
            "shape": (),  # Scalar
        },
        # ---
        # --- entry/instrument/mono_with_grating_cpt ---
        # ---
        "entry/instrument/mono_with_grating_cpt/energy": {
            "value": [0, 0],
            "dtype": "float64",
            "shape": (2,),
        },
        "entry/instrument/mono_with_grating_cpt/grating/diffraction_order": {
            "value": [0, 0],
            "dtype": "int32",
            "shape": (2,),
        },
        "entry/instrument/mono_with_grating_cpt/grating/substrate_material": {
            "value": b"leadless",
            "shape": (8,),  # Adjust the shape to match the actual string length
        },
        # ---
        # --- entry/run_info/start ---
        # ---
        "entry/run_info/start/definition": b"NX_ghi",
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
        "entry/run_info/start/num_intervals": plan_step_number - 1,
        "entry/run_info/start/num_points": plan_step_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_args/detectors": [
            b"SynAxis(prefix='', name='mono_en', parent='mono', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])"
        ],
        "entry/run_info/start/plan_args/num": plan_step_number,
        "entry/run_info/start/plan_args/per_step": b"None",
        "entry/run_info/start/plan_name": b"scan",
        "entry/run_info/start/plan_pattern": b"inner_product",
        "entry/run_info/start/plan_pattern_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_pattern_args/num": plan_step_number,
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
        "entry/run_info/stop/num_events/primary": plan_step_number,
        "entry/run_info/stop/reason": b"",
    }

    # Validate file contents
    validate_nexus_file(nx_file_path, expected_structure, expected_data)

    # Remove the nexus file after successful validation
    clean_up(nx_file_path)


# Test function
# @unittest.skip("Temporarily disabling this test_4")
def test_4(
    RE,
    devices_dictionary,
    baseline_4,
    my_motor,
    nx_file_dir_path,
    nx_schema_dir_path,
    plan_step_number,
    request,
):
    """
    Integration test for generating and validating a Nexus file.
    - Configures metadata and baseline devices.
    - Executes a plan and validates the resulting Nexus file's structure and data.
    """

    # Add preprocessors to the RunEngine
    add_preprocessors(RE, devices_dictionary, baseline_4, nx_schema_dir_path)

    # Generate metadata
    nx_file_name: str = f"hzb_nexus_file_{request.node.name}"
    md: dict = generate_md(
        nx_file_name,
        "bluesky run test 4",
        "NX_jkl",
        {"a": 31, "b": 32, "c": {"d": 33, "e": 34}},
    )

    # Execute the plan
    execute_plan(RE, md, [devices_dictionary["mono"].en], my_motor, plan_step_number)

    # Define Nexus file path
    nx_file_path: str = get_nx_file_path(nx_file_dir_path, nx_file_name)

    # Assert file creation
    assert os.path.exists(
        nx_file_path
    ), f"Nexus file: {nx_file_path} was not created while executing test: {request.node.name}."

    # Expected structure
    expected_structure: dict = {
        # ---
        # --- entry/instrument ---
        # ---
        "entry": {"NX_class": "NXentry"},
        "entry/instrument": {"NX_class": "NXinstrument"},
        # ---
        # --- entry/instrument/mono ---
        # ---
        "entry/instrument/mono": {"NX_class": "NXmonochromator"},
        "entry/instrument/mono/energy": {
            "nxclass": "NX_FLOAT",
            "description": "Energy value",
            "transformation": {
                "expression": "3 * x**2 + np.exp(np.log(5)) + 1",
                "target": "value",
                "description": "Transformation configuration that applies a symbolic operation to the target data array.",
            },
        },
        "entry/instrument/mono/energy_timestamps": {"nxclass": "NX_FLOAT"},
        "entry/instrument/mono/events_timestamps": {
            "nxclass": "NX_FLOAT",
            "description": "Timestamps of the events",
        },
        "entry/instrument/mono/grating": {
            "NX_class": "NXgrating",
            "description": "Grating",
        },
        "entry/instrument/mono/grating/diffraction_order": {
            "nxclass": "NX_INT",
            "description": "Diffraction order value",
        },
        # ---
        # --- entry/run_info ---
        # ---
        "entry/run_info": {"NX_class": "NXcollection"},
        # ---
        # --- entry/run_info/start ---
        # ---
        "entry/run_info/start": {},
        "entry/run_info/start/device_md/mono": {},
        "entry/run_info/start/hints": {},
        "entry/run_info/start/plan_args": {},
        "entry/run_info/start/plan_pattern_args": {},
        "entry/run_info/start/test_dict": {},
        "entry/run_info/start/versions": {},
        # ---
        # --- entry/run_info/stop ---
        # ---
        "entry/run_info/stop": {},
        "entry/run_info/stop/num_events": {},
    }

    # Expected data
    expected_data: dict = {
        # ---
        # --- entry/instrument/mono ---
        # ---
        "entry/instrument/mono/energy": {
            "value": [6.0] * plan_step_number,
            "dtype": "float64",
            "shape": (plan_step_number,),
            "attrs": {
                "units": "keV",  # Expected units
            },
        },
        "entry/instrument/mono/grating/diffraction_order": {
            "value": 0,
            "dtype": "int32",
            "shape": (),  # Scalar
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
        "entry/run_info/start/num_intervals": plan_step_number - 1,
        "entry/run_info/start/num_points": plan_step_number,
        "entry/run_info/start/nx_file_name": nx_file_name.encode(),  # Encode to obtain byte string since byte string is a value returned from nexus file
        "entry/run_info/start/plan_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_args/detectors": [
            b"SynAxis(prefix='', name='mono_en', parent='mono', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])"
        ],
        "entry/run_info/start/plan_args/num": plan_step_number,
        "entry/run_info/start/plan_args/per_step": b"None",
        "entry/run_info/start/plan_name": b"scan",
        "entry/run_info/start/plan_pattern": b"inner_product",
        "entry/run_info/start/plan_pattern_args/args": [
            b"SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
            b"1",
            b"10",
        ],
        "entry/run_info/start/plan_pattern_args/num": plan_step_number,
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
        "entry/run_info/stop/num_events/primary": plan_step_number,
        "entry/run_info/stop/reason": b"",
    }

    # Validate file contents
    validate_nexus_file(nx_file_path, expected_structure, expected_data)

    # Remove the nexus file after successful validation
    clean_up(nx_file_path)


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
