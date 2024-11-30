"""Module: pydantic_models_hzb.py

1) Definitions of pydantic models designed for device classes used at HZB bessyii.

    - Monitor, Monochromator, Detector are suposed to have their own pydantic models defined in this file
    - NXgeneralModel is to be applied for all device classes but not Monitor, Monochromator, Detector

2) Definition of a mapping between model_name and class definition
"""

from typing import Optional

from bluesky_nexus.models.nexusformat_models import *

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


# Define a mapping between model_name and classes
MODEL_NAME_TO_CLASS_MAPPING = {
    "NXmonochromatorModel": NXmonochromatorModel,
    "NXgeneralModel": NXgeneralModel,
}
