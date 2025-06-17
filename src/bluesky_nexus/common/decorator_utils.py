"""
# Module: decorator_utils.py
# ==========================

This module provides utility decorators for different reusable functionality.

Functions/decorators:
- measure_time: A decorator for measuring and logging the execution time of a function.
- NxSchemaLoader: Parses a YAML string and attaches the resulting dictionary to the decorated class as an attribute named `nx_schema`
"""

import time
import yaml
import os

from bluesky_nexus.common.logging_utils import logger


def measure_time(func):
    """
    A decorator that measures the execution time of the decorated function.

    This decorator uses time.perf_counter() to calculate the time elapsed
    during the execution of the function and logs the result in seconds
    with six decimal places of precision.

    Args:
        func (callable): The function whose execution time is to be measured.

    Returns:
        callable: A wrapper function that measures execution time and calls
                  the original function.

    Example:
        >>> @measure_time
        >>> def example_function():
        >>>     time.sleep(1)
        >>> example_function()
        example_function executed in 1.000123 seconds
    """

    def measure_time_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.debug(f"{func.__name__} executed in {elapsed_time:.6f} seconds")
        return result

    return measure_time_wrapper

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

    if os.path.isfile(yaml_string):
        # If the input is a file path, read the content of the file
        try:
            with open(yaml_string, 'r') as file:
                yaml_string = file.read()
        except Exception as e:
            raise ValueError(f"Error reading YAML file `{yaml_string}`: {e}")

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
