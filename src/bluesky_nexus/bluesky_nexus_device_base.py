"""
Module: bluesky_nexus_device_base
==================================

This module provides a base class `NXdevice` for defining device classes
that integrate with the Bluesky framework and adhere to NeXus (NX) schema
standards. The `NXdevice` class enforces the presence of a pydantic schema definition (`nx_schema`),
ensuring consistent and structured metadata for NeXus-based data handling.

Dependencies:
-------------
- `ophyd.Device`: The `NXdevice` class extends the `Device` class from the `ophyd` library.

Usage:
------
This module is intended to be used as a foundation for creating specific device
classes that implement the NeXus pydantic schema. Subclasses must provide a non-empty
`nx_schema` value.

Example:
--------
```python
from bluesky_nexus_device_base import NXdevice

class MyDevice(NXdevice):
    nx_schema = "my_schema"
    # Additional implementation for MyDevice
"""

from ophyd import Device


class NXdevice(Device):
    """
    Base class for NeXus-compliant device classes.

    This class extends `ophyd.Device` and introduces an additional requirement
    for subclasses to define a non-empty `nx_schema` attribute. The `nx_schema`
    specifies the NeXus schema associated with the device, ensuring consistency
    in data representation and adherence to NeXus standards.

    Attributes:
    -----------
    nx_schema : str
        A string representing the NeXus pydantic schema associated with the device.
        This attribute must be defined by subclasses and cannot be empty.

    Methods:
    --------
    __init__(*args, **kwargs):
        Initializes the device and validates that the `nx_schema` attribute
        is defined and non-empty.

    Raises:
    -------
    ValueError:
        If the `nx_schema` attribute is not defined or is an empty string.

    Example:
    --------
    ```python
    from bluesky_nexus_device_base import NXdevice

    class ExampleDevice(NXdevice):
        nx_schema = "example_schema"
        # Additional implementation for ExampleDevice
    ```
    """

    nx_schema = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.nx_schema == "":
            raise ValueError(
                f"The class {self.__class__.__name__} requires a non-empty nx_schema value. Check class definition."
            )
