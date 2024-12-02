"""
Module: nexusformat_models.py

This module defines Pydantic models for NeXus data structures, which are commonly used in scientific data formats
for representing hierarchical datasets. These models provide structure, validation, and utilities for NeXus objects,
fields, groups, links, and attributes.
"""

from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import numpy.typing as npt
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "Field",
    "NXattrModel",
    "NXfieldModel",
    "NXgroupModel",
    "NXobjectModel",
    "NXlinkModel",
    "NXlinkFieldModel",
    "NXlinkGroupModel",
    "NXdataModel",
    "NXentryModel",
    "NXfieldModelWithString",
    "NXfieldModelWithInt",
    "NXfieldModelWithFloat",
    "NXfieldModelWithArray",
    "NXattrModelWithString",
    "NXattrModelWithScalar",
    "NXattrModelWithArray",
]

# scalar type
Scalar = Union[str, float, int]
# array-like i.e. list, tuple, numpy.ndarray
ArrayLike = npt.ArrayLike
# numpy datatype
NPType = np.dtype
# numpy array
NPArray = npt.NDArray


class PrePostRunString(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, *args, **kwargs) -> "PrePostRunString":
        if not isinstance(value, str):
            raise ValueError("string required")
        if not (
            value.startswith("$pre-run-cpt")
            or value.startswith("$pre-run-md")
            or value.startswith("$post-run:events")
        ):
            raise ValueError(
                'string must start with "$pre-run-cpt" or $pre-run-md or "$post-run:events"'
            )
        return cls(value)


class NXattrModel(BaseModel):
    nxclass: Optional[str] = Field("NXattr", description="The class of the NXattr.")
    value: Union[PrePostRunString, str, Scalar, ArrayLike] = Field(
        ..., description="Value of the attribute."
    )
    dtype: Optional[str] = Field(None, description="Data type of the attribute.")
    shape: Optional[Union[list, Tuple[int]]] = Field(
        None, description="Shape of the " "attribute."
    )

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"


class NXFileModel(BaseModel):
    nxclass: str = Field("NXFile", description="The class of the NXFile.")
    name: str = Field(..., description="Name of the HDF5 file.")
    mode: str = Field("r", description="Read/write mode of the HDF5 file.")
    recursive: Optional[bool] = Field(
        None, description="If True, the file tree is loaded" " recursively."
    )
    kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword arguments for opening the " "h5py File object.",
    )

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"


class NXobjectModel(BaseModel):
    nxclass: Optional[str] = Field("NXobject", description="The class of the NXobject.")
    nxname: Optional[str] = Field(None, description="The name of the NXobject.")
    nxgroup: Optional["NXgroupModel"] = Field(
        None,
        description="The parent group containing"
        " this object within a "
        "NeXus tree.",
    )
    nxpath: Optional[str] = Field(
        None,
        description="The path to this object with respect to"
        " the root of the NeXus tree.",
    )
    nxroot: Optional["NXgroupModel"] = Field(
        None,
        description="The root object of the NeXus" " tree containing this " "object.",
    )
    nxfile: Optional["NXFileModel"] = Field(
        None,
        description="The file handle of the root"
        " object of the NeXus tree"
        " containing this object.",
    )
    nxfilename: Optional[str] = Field(
        None, description="The file name of NeXus object's " "tree file handle."
    )
    attrs: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="A dictionary of the NeXus object's" " attributes.",
    )
    # active: Optional[bool] = True  # New active field
    active: Optional[bool] = Field(
        None,
        description="Object is active or not. Not active object will be filtered by the NXobjectModel",
    )

    @model_validator(mode="before")
    def filter_inactive_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        ACTIVE_LABEL: str = "active"

        def recursively_filter_inactive(data: Dict[str, Any]) -> Dict[str, Any]:
            filtered_data = {}
            for key, value in data.items():
                if key == ACTIVE_LABEL:
                    continue  # Skip 'active' keys altogether

                # If value is a nested dictionary, check 'active' flag
                if isinstance(value, dict):
                    if value.get(ACTIVE_LABEL, True):  # Process only if active is True
                        filtered_value = recursively_filter_inactive(value)
                        filtered_data[key] = filtered_value
                else:
                    # If value is not a dictionary, add it directly
                    filtered_data[key] = value

            return filtered_data

        return recursively_filter_inactive(values)

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"


class NXfieldModel(NXobjectModel):
    inherits_from: Optional[str] = Field(
        "NXobject", description="Base class of the object."
    )
    nxclass: Optional[str] = Field("NXfield", description="The class of the NXfield.")
    value: Optional[Union[PrePostRunString, int, float, ArrayLike, str]] = Field(
        ..., description="Value of" " the field" "."
    )
    shape: Optional[Union[list, Tuple[int]]] = Field(
        None, description="Shape of the field."
    )
    dtype: Optional[Union[str, np.dtype]] = Field(
        None, description="Data type of the field."
    )

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"


class NXgroupModel(NXobjectModel):
    nxclass: Optional[str] = Field("NXgroup", description="The class of the NXgroup.")
    inherits_from: Optional[str] = Field(
        "NXobject", description="Base class of the object."
    )

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


class NXlinkModel(NXobjectModel):
    target: Optional[str] = Field(None, description="The target of the link.")
    file: Optional[str] = Field(
        None, description="The file containing the target of" " the link."
    )
    name: Optional[str] = Field(None, description="The name of the link.")
    group: Optional["NXgroupModel"] = Field(
        None,
        description="The parent group"
        " containing this "
        "link within a NeXus"
        " tree.",
    )
    abspath: Optional[str] = Field(
        None, description="The absolute path to the" " target of the link."
    )
    soft: Optional[bool] = Field(None, description="If True, the link is a soft link.")

    class Config:
        extra = "forbid"

    @property
    def nxclass(self) -> str:
        return "NXlink"


class NXlinkFieldModel(NXlinkModel):
    @property
    def nxclass(self) -> str:
        return "NXlink"

    @property
    def value(self) -> Optional[Union[int, float, str, list, tuple]]:
        return self.target.value if isinstance(self.target, NXfieldModel) else None


class NXlinkGroupModel(NXlinkModel):
    @property
    def nxclass(self) -> str:
        return "NXlink"

    @property
    def entries(self) -> Optional[Dict[str, Union[NXfieldModel, NXgroupModel]]]:
        return self.target.entries if isinstance(self.target, NXgroupModel) else None


class NXdataModel(NXgroupModel):
    signal: Optional[NXfieldModel] = Field(
        None, description="Field defining the data to be" " plotted"
    )
    axes: Optional[Tuple[NXfieldModel, ...]] = Field(
        None,
        description="Tuple of" " one-dimensional" " fields defining " "the plot axes",
    )
    errors: Optional[NXfieldModel] = Field(
        None,
        description="Field containing the "
        "standard deviations of the"
        " signal values",
    )
    weights: Optional[NXfieldModel] = Field(
        None, description="Field containing signal value" " weights"
    )

    @property
    def nxclass(self) -> str:
        return "NXdata"

    class Config:
        extra = "forbid"


class NXentryModel(NXgroupModel):
    def __add__(self, other: "NXentryModel") -> "NXentryModel":
        # Implement the addition logic here
        pass

    def __sub__(self, other: "NXentryModel") -> "NXentryModel":
        # Implement the subtraction logic here
        pass

    def set_default(self, over: bool = False):
        # Implement the set_default logic here
        pass

    @property
    def plottable_data(self):
        # Implement the plottable_data logic here
        pass

    @property
    def nxclass(self) -> str:
        return "NXentry"

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"


class NXattrModelWithString(NXattrModel):
    value: Union[PrePostRunString, str] = Field(
        ..., description="Value of the attribute."
    )


class NXattrModelWithScalar(NXattrModel):
    value: Union[Scalar, PrePostRunString] = Field(
        ..., description="Value of the attribute."
    )


class NXattrModelWithArray(NXattrModel):
    value: Union[ArrayLike, PrePostRunString] = Field(
        ..., description="Value of the attribute."
    )


class NXfieldModelWithString(NXfieldModel):
    value: Union[str, PrePostRunString] = Field(
        ..., description="NX data field with string type"
    )


class NXfieldModelWithInt(NXfieldModel):
    value: Union[int, PrePostRunString] = Field(
        ..., description="NX data field with int type"
    )


class NXfieldModelWithFloat(NXfieldModel):
    value: Union[float, PrePostRunString] = Field(
        ..., description="NX data field with float type"
    )


class NXfieldModelWithArray(NXfieldModel):
    value: Union[ArrayLike, PrePostRunString] = Field(
        ..., description="NX data field with array-like type"
    )
