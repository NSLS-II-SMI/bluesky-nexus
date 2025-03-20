"""
# Module: bluesky_nexus_device_decorators
# ==================================

Module for device-related decorators.

This module defines decorators that can be used to enhance device classes with additional
attributes and functionality.

Currently Available Decorators:
- `NxSchemaLoader`: Parses a YAML string and attaches the resulting dictionary to the
  decorated class as an attribute named `nx_schema`. Attribute used by the package "bluesky_nexus".

"""

import yaml


def NxSchemaLoader(yaml_string):
    """
    Decorator that parses a YAML string and adds it as a dictionary attribute to the decorated class.

    This decorator extracts key-value pairs from the provided YAML string and assigns the resulting
    dictionary to a class attribute named `nx_schema`. This attribute can then be accessed by instances
    or other parts of the program to facilitate Nexus file generation.

    Args:
        yaml_string (str): A string containing YAML-formatted data.

    Returns:
        function: A class decorator that attaches the parsed YAML data to the class.

    Validation:
    - The `yaml_string` argument must be a **non-empty string**.
    - If `yaml_string` is `None`, a number, a list, a dictionary, or any other type, a `ValueError` is raised.
    - If `yaml_string` consists only of whitespace (e.g., `"   "`, `"\n\n"`), a `ValueError` is raised.

    Special Cases:
    - If `yaml_string` is empty, contains only whitespace, or only comments, `nx_schema` will be `{}`.
    - If `yaml_string` contains only `null` (explicitly or implicitly), `nx_schema` will be `{}`.
    - If `yaml_string` is malformed, an exception will be raised instead of assigning `{}`.

    Example:
        @NxSchemaLoader('''
        name: ExampleDevice
        properties:
            field1: value1
            field2: value2
        ''')
        class ExampleDevice:
            pass

        print(ExampleDevice.nx_schema)  # Access the parsed YAML schema
    """

    if not isinstance(yaml_string, str) or not yaml_string.strip():
        raise ValueError(
            f"Provided YAML string must be a non-empty string.  Received: {repr(yaml_string[:30])}..."
        )

    def decorator(cls):
        try:
            parsed_data: dict = yaml.safe_load(yaml_string) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing error in class `{cls.__name__}`: {e}")
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error in class `{cls.__name__}` during YAML parsing: {e}"
            )

        setattr(cls, "nx_schema", parsed_data)
        return cls

    return decorator
