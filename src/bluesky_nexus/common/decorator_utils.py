"""
decorator_utils.py

This module provides utility decorators for different reusable functionality.

Functions:
- measure_time: A decorator for measuring and printing the execution time of a function.
"""

import time


def measure_time(func):
    """
    A decorator that measures the execution time of the decorated function.

    This decorator uses time.perf_counter() to calculate the time elapsed
    during the execution of the function and prints the result in seconds
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

    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} executed in {elapsed_time:.6f} seconds")
        return result

    return wrapper
