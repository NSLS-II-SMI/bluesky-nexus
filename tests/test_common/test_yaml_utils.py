"""Module:              test_yaml_utils.py

Description:            Test functions from yaml_utils.py

Actions:
                        Test if data dir exists
                        Test if yaml-files exist
                        Test function:
                            - read_yaml()

Test data directory:    .data
Test files:
                        .data/not_empty.yml
                        .data/empty.yml
"""

import os

import pytest

from bluesky_nexus.common.yaml_utils import read_yaml

# Define path to data folder
data_folder: str = os.path.join(os.path.dirname(__file__), "data")

# Define path to non empty y(a)ml-file serving as "test data"
file_name: str = "not_empty.yml"
file_path: str = os.path.join(data_folder, file_name)

# Define path to empty y(a)ml-file serving as "test data"
file_name_empty_file: str = "empty.yml"
file_path_empty_file: str = os.path.join(data_folder, file_name_empty_file)


# Test if "data_folder" is pointing to a folder
def test_data_dir():
    assert os.path.isdir(data_folder)


# Test if "file_path" is pointing to a file
def test_not_empty_file_exists():
    assert os.path.isfile(file_path)


# Test if "file_path_empty_file" is pointing to a file
def test_empty_file_exists():
    assert os.path.isfile(file_path_empty_file)


# Test read_yaml if missing file path parameter
def test_read_yaml_no_path():
    with pytest.raises(TypeError):
        _: list | dict | None = read_yaml()


# Test read_yaml if empty file path parameter
def test_read_yaml_empty_path():
    with pytest.raises(FileNotFoundError):
        _: list | dict | None = read_yaml("")


# Test read_yaml if parameter is not a string
def test_read_yaml_wrong_param_type():
    with pytest.raises(OSError):
        _: list | dict | None = read_yaml(123)


# Test read_yaml if wrong number of paramters
def test_read_yaml_wrong_param_number():
    with pytest.raises(TypeError):
        _: list | dict | None = read_yaml(file_path, file_path)


# Test read_yaml if y(a)ml-file is empty
def test_read_yaml_empty_file():
    actual: list | dict | None = read_yaml(file_path_empty_file)
    assert actual is None


# Test read_yaml if y(a)ml-file is not empty
def test_read_yaml():
    actual: list | dict | None = read_yaml(file_path)
    expected = {
        "nx_model": "NXmonochromatorModel",
        "nx_schema": "nx_test_mono_schema",
        "energy": {
            "nxclass": "NX_FLOAT",
            "value": "$post-run:events:en",
            "dtype": "float64",
            "attrs": {"units": "eV"},
        },
        "grating": {
            "nxclass": "NXgrating",
            "diffraction_order": {
                "nxclass": "NX_INT",
                "value": "$pre-run-cpt:grating",
                "dtype": "int32",
            },
        },
    }
    assert actual == expected
