"""
Module: nx_core_models.py

This module defines Pydantic models for representing NeXus data structures, 
which are commonly used in scientific data formats to organize hierarchical datasets. 
These models provide structure, validation, and utilities for handling NeXus objects, 
fields, groups, links, and attributes.

### Features:
- **Structured Data Representation**: Provides a consistent model for NeXus components.
- **Validation**: Ensures data integrity using Pydantic's validation mechanisms.
- **Flexibility**: Supports scalar values, arrays, and hierarchical relationships.
- **Integration with HDF5**: Can be used to interact with NeXus files based on HDF5.

### Main Models:
- `NXattrModel`: Represents NeXus attributes.
- `NXFileModel`: Represents a NeXus file.
- `NXobjectModel`: Base model for NeXus objects.
- `NXgroupModel`: Represents a NeXus group.
- `NXfieldModel`: Represents a NeXus field.
- `NXfieldModelForAttribute`: A specialized field model for attributes.
- `PrePostRunString`: Custom string type for handling pre- and post-run metadata.

This module is designed to facilitate working with NeXus data structures in Python applications, 
ensuring consistency and correctness when handling scientific datasets.
"""

from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import numpy.typing as npt
from pydantic import BaseModel, ConfigDict, Field, model_validator
# from pydantic.core import PydanticSchema  # To be activated for pydantic V3

__all__ = [
    "BaseModel",
    "Scalar",
    "Number",
    "Field",
    "NXattrModel",
    "NXfieldModel",
    "NXfieldModelWithPrePostRunString",
    "NXgroupModel",
    "NXobjectModel",
]

# scalar type
Scalar = Union[str, float, int]

# number type
Number = Union[float, int]

# array-like i.e. list, tuple, numpy.ndarray
ArrayLike = npt.ArrayLike

class PrePostRunString(str):
    """
    Custom string type representing pre- and post-run strings in NeXus metadata.

    This ensures that values must start with one of the following prefixes:
    - "$pre-run-cpt"
    - "$pre-run-md"
    - "$post-run"
    """

    # To be removed in pydantic V3
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    # To be activated for pydantic V3
    # @classmethod
    # def __get_pydantic_core_schema__(cls, schema: PydanticSchema):
    #     # Modify schema to include custom validation logic
    #     schema = schema.clone()
    #     schema.validate = cls.validate
    #     return schema

    @classmethod
    def validate(cls, value: Any, *args, **kwargs) -> "PrePostRunString":
        if not isinstance(value, str):
            raise ValueError("string required")
        if not (
            value.startswith("$pre-run-cpt")
            or value.startswith("$pre-run-md")
            or value.startswith("$post-run")
        ):
            raise ValueError(
                'string must start with "$pre-run-cpt" or $pre-run-md or "$post-run"'
            )
        return cls(value)

class NXattrModel(BaseModel):
    """
    Pydantic model representing an NXattr (NeXus attribute).

    Attributes:
    - nxclass (str): Class name of the NXattr.
    - value (Union[PrePostRunString, Scalar, ArrayLike]): Value of the attribute.
    - dtype (Optional[str]): Data type of the attribute.
    - shape (Optional[Union[list, Tuple[int]]]): Shape of the attribute if applicable.
    """

    nxclass: Optional[str] = Field("NXattr", description="The class of the NXattr.")
    value: Union[PrePostRunString, Scalar, ArrayLike] = Field(..., description="Value of the attribute.")
    dtype: Optional[str] = Field(None, description="Data type of the attribute.")
    shape: Optional[Union[list, Tuple[int]]] = Field(None, description="Shape of the attribute.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

class NXFileModel(BaseModel):
    """
    Pydantic model representing an NXFile (NeXus file structure).

    Attributes:
    - nxclass (str): Class name of the NXFile.
    - name (str): Name of the HDF5 file.
    - mode (str): Read/write mode.
    - recursive (Optional[bool]): Whether to load the file tree recursively.
    - kwargs (Dict[str, Any]): Additional keyword arguments for opening the file.
    """

    nxclass: str = Field("NXFile", description="The class of the NXFile.")
    name: str = Field(..., description="Name of the HDF5 file.")
    mode: str = Field("r", description="Read/write mode of the HDF5 file.")
    recursive: Optional[bool] = Field(None, description="If True, the file tree is loaded recursively.")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments for opening the h5py file object.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

class NXobjectModel(BaseModel):
    """
    Pydantic model representing a generic NXobject (NeXus object).

    Attributes:
    - nxclass (Optional[str]): Class name of the NXobject.
    - nxname (Optional[str]): Name of the NXobject.
    - nxpath (Optional[str]): Path of the object in the NeXus tree.
    - nxroot (Optional[NXgroupModel]): Root object of the NeXus tree.
    - nxfile (Optional[NXFileModel]): File handle of the root NeXus tree.
    - attrs (Optional[Dict[str, Any]]): Arbitrary user-defined attributes.
    """

    nxclass: Optional[str] = Field("NXobject", description="The class of the NXobject.")
    nx_model: Optional[str] = Field(None, description="The name of the model.")
    nxname: Optional[str] = Field(None, description="The name of the NXobject.")
    nxgroup: Optional["NXgroupModel"] = Field(None, description="The parent group containing this object within a NeXus tree.")
    nxpath: Optional[str] = Field(None, description="The path to this object with respect to the root of the NeXus tree.")
    nxroot: Optional["NXgroupModel"] = Field(None, description="The root object of the NeXus" " tree containing this " "object.")
    nxfile: Optional["NXFileModel"] = Field(None, description="The file handle of the root object of the NeXus tree containing this object.")
    nxfilename: Optional[str] = Field(None, description="The file name of NeXus object's " "tree file handle.")
    attrs: Optional[Dict[str, Any]] = Field(default={}, description="Arbitrary attributes belonging to a dataset assigned by a user.")
    description: Optional[Any] = Field(None, description="Optional description of the object")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    # The new version of model_dump to debug
    # def model_dump(self, exclude_none: bool = True) -> Dict:
    #     """
    #     Override `model_dump` to include 'description' in metadata (not in values) to avoid HDF5 issues.
    #     """

    #     # Generate the initial dump
    #     base_dump = super().model_dump(exclude_none=exclude_none)

    #     def inject_descriptions(dump: dict, fields: dict, metadata: dict):
    #         """
    #         Recursively traverse the dump dictionary and store descriptions separately in metadata.
    #         """
    #         for key, value in dump.items():
    #             if key in fields:
    #                 field = fields[key]
    #                 description = field.description

    #                 # If a description exists, store it in metadata
    #                 if description is not None:
    #                     metadata[key] = {"description": description}

    #             # If the value is a nested model (dict), recurse into it
    #             if isinstance(value, dict) and key in fields:
    #                 nested_fields = getattr(fields[key].annotation, "model_fields", None)
    #                 if nested_fields:
    #                     metadata[key] = metadata.get(key, {})  # Ensure nested metadata exists
    #                     inject_descriptions(value, nested_fields, metadata[key])

    #     # Metadata structure to store descriptions separately
    #     metadata = {}

    #     # Inject descriptions separately into metadata
    #     inject_descriptions(base_dump, self.model_fields, metadata)

    #     # Attach metadata under a special key (e.g., `_meta`)
    #     base_dump["_meta"] = metadata

    #     return base_dump


    # TODO: Modify to support args that are from BaseModel

    # def model_dump(self, exclude_none: bool = True) -> Dict:
    #     """
    #     Override `model_dump` to include 'description' in nested fields based on `self.model_fields`.

    #     This method extends the base `model_dump` functionality by recursively injecting
    #     field descriptions into the output dictionary (`base_dump`). It uses the field metadata
    #     defined in `self.model_fields` (from Pydantic's model structure) to include descriptions
    #     at every level of the nested dictionary structure.

    #     Steps:
    #     1. The base dump is generated using the `model_dump` method from the parent class.
    #     2. A helper function, `inject_descriptions`, is used to traverse the dictionary recursively
    #     and add descriptions for fields, where applicable.
    #     3. The function checks each key in the `dump` dictionary against `fields` to see if it has
    #     a corresponding description in `self.model_fields`. If a description exists, it is added
    #     to the field's dictionary as `"description"`.
    #     4. If a field is nested (e.g., its value is a dictionary that represents another model),
    #     the function looks for nested fields in the `annotation` attribute of the field and recurses
    #     into that structure.

    #     Parameters:
    #     - exclude_none: A flag passed to the base `model_dump` method to exclude fields with `None` values.

    #     Returns:
    #     - A dictionary representation of the model (`base_dump`) with descriptions injected into
    #     all applicable fields, including nested ones.

    #     Helper Function:
    #     - `inject_descriptions(dump: dict, fields: dict)`:
    #         - This function traverses the `dump` dictionary recursively and injects descriptions
    #         into each field if a corresponding description exists in the `fields` dictionary.
    #         - It also handles nested fields by checking if the current field has a Pydantic model
    #         type (with `__fields__` attribute) and recursing into its structure.

    #     Special Cases:
    #     - Keys `"attrs"` and `"default"` are explicitly skipped as they do not require descriptions.
    #     - Fields without a description or those not present in `self.model_fields` are ignored.
    #     """

    #     # Generate the initial dump using the base model's `model_dump` method.
    #     base_dump = super().model_dump(exclude_none=exclude_none)

    #     def inject_descriptions(dump: dict, fields: dict):
    #         """
    #         Recursively traverse the dump dictionary and inject descriptions from the fields dictionary.
    #         """
    #         for key, value in dump.items():
    #             if key in ["attrs", "default"]:
    #                 continue

    #             # Check if the key exists in fields and has a description
    #             if key in fields:
    #                 field = fields[key]
    #                 description = field.description
    #                 print("description:", description)

    #                 # If a description exists, inject it into the current key
    #                 if description is not None:
    #                     if isinstance(value, dict):  # For dictionary-like values
    #                         value["description"] = description
    #                         print("description:", description)

    #             # Recurse if the value is a dictionary and contains nested fields
    #             if isinstance(value, dict):
    #                 # Try to extract nested fields from the current field's annotation
    #                 nested_fields = (
    #                     getattr(fields[key].annotation, "model_fields", None)
    #                     if key in fields
    #                     else None
    #                 )
    #                 if nested_fields:
    #                     inject_descriptions(value, nested_fields)

    #     # Inject descriptions into the base dump using the model's fields
    #     inject_descriptions(base_dump, self.model_fields)

    #     return base_dump

class NXgroupModel(NXobjectModel):
    """
    Pydantic model representing an NXgroup (NeXus group).

    Inherits from NXobjectModel.
    """

    #nxclass: Optional[str] = Field("NXgroup", description="The class of the group.")
    nxclass: str = Field(..., description="The class of the group.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

class TransformationModel(BaseModel):
    """
    Pydantic model representing a symbolic transformation operation on a NeXus field.

    Attributes:
    - expression (str): Symbolic expression for transformation.
    - target (str): Target field for transformation.
    """

    expression: str = Field(..., description="Symbolic expression that defines the transformation, using 'x' as the array variable. "
        "Examples: '3 * x**2 + 5', 'np.sqrt(x) + 2', np.log(x) + 3, np.exp(x) + 3",
    )
    target: str = Field(..., description="Specifies the target array (e.g., 'value') on which the transformation is applied.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

class NXfieldModel(NXobjectModel):
    """
    Pydantic model representing an NXfield (NeXus field object).

    Attributes:
    - value (Any): Value of the field.
    - dtype (Optional[str]): Data type of the field.
    """

    value: Any = Field(None, description="Value of the field.")
    dtype: Optional[str] = Field(None, description="Data type of the field.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

class NXfieldModelWithPrePostRunString(NXfieldModel):
    """
    Extended NXfieldModel where the value must be a PrePostRunString.
    """
    nxclass: str = Field(..., description="The nexus class of the field.")
    value: PrePostRunString = Field(..., description="Value of the field.")
    dtype: Optional[str] = Field(None, description="Data type of the field.")
    transformation: Optional[TransformationModel] = Field(None, description="Transformation configuration that applies a symbolic operation to the target field.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

class NXfieldModelForAttribute(NXfieldModel):
    """
    Pydantic model representing an NXfield specifically for attributes.

    Attributes:
    - value (Union[PrePostRunString, str]): Value of the attribute field.
    """
    value: Union[PrePostRunString, Scalar] = Field(..., description="Value of the attribute field.")
    dtype: Optional[str] = Field(None, description="Data type of the attribute field.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
