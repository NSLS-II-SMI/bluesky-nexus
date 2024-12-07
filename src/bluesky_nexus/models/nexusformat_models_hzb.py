"""
Module: nexusformat_models_hzb.py

This module defines Pydantic models tailored for device classes used at HZB's BESSY II facility. The models ensure
structured validation and organization of data for different device types.

Classes:
    - NXgratingModel: A model for grating components, used in monochromators.
    - NXmonochromatorModel: A model representing a monochromator, including energy and grating details.
    - NXgeneralModel: A generic model applicable to all device classes except Monitor, Monochromator, and Detector.

Mappings:
    MODEL_NAME_TO_CLASS_MAPPING: A dictionary mapping model names to their respective class definitions, allowing
    dynamic resolution of models by name.
"""

from typing import Optional

from bluesky_nexus.models.nexusformat_models import (
    Field,
    NXattrModel,
    NXattrModelWithString,
    NXfieldModelWithFloat,
    NXfieldModelWithInt,
    NXfieldModelWithString,
    NXgroupModel,
)

__all__ = ["NXmonochromatorModel", "NXgeneralModel", "MODEL_NAME_TO_CLASS_MAPPING"]


# This is the model which describes the structure of the data from a grating component of a mono
class NXgratingModel(NXgroupModel):
    diffraction_order: NXfieldModelWithInt = Field(
        None, description="Diffraction order"
    )
    substrate_material: Optional[NXfieldModelWithString] = Field(
        None, description="Substrate material"
    )


# This is the model for any NX Monchromator
class NXmonochromatorModel(NXgroupModel):
    default: NXattrModelWithString = Field(
        NXattrModel(value="energy"), description="Default"
    )
    energy: NXfieldModelWithFloat = Field(None, description="energy")
    grating: NXgratingModel = Field(None, description="grating")


# This is a general model for all classes but not Monitor, Monochromator, Detector
class NXgeneralModel(NXgroupModel):
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


# Define a mapping between model name and class name
MODEL_NAME_TO_CLASS_MAPPING = {
    "NXmonochromatorModel": NXmonochromatorModel,
    "NXgeneralModel": NXgeneralModel,
}
