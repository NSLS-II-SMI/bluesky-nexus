"""Module:      yaml_utils.py

Description:    Support of reading/writing from/to y(a)ml file.

Usage:
                For reading: Import whole module or read_yaml function from the module
                For writing: Import whole module or write_yaml function from the module

Advice:         If you use any static type checking tool in your IDE: install types-PyYAML
                (to ensure existance of library/type/hint stubs for the yaml package)
"""

import yaml


def read_yaml(file_path: str) -> list[dict] | dict | None:
    """Read from an y(a)ml file.

    Parameters
    ----------
    file_path : str
        Path to an y(a)ml file

    Returns
    -------
    list[dict] | dict | None
        Content of the file. Returns None for empty y(a)ml-file
    """

    with open(file_path, "r") as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as error:
            print(f"Read from Y(A)ML file: {file_path} FAILED. Error msg: {error}")
            return None
        else:
            return data


def write_yaml(file_path: str, data: list | dict) -> None:
    """Write to an y(a)ml file

    Parameters
    ----------
    file_path : str
        Path to an y(aml) file
    data : list | dict
    """

    with open(file_path, "w") as file:
        try:
            yaml.dump(data, file)
        except yaml.YAMLError as error:
            print(f"Write to Y(A)ML file: {file_path} FAILED. Error msg: {error}")
