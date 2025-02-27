
from typing import Optional
from bluesky_nexus.models.nx_core_models import (
    BaseModel,
    Field,
    ConfigDict,
    NXattrModel,
    NXgroupModel,
    NXfieldModelForAttribute,
    NXfieldModelWithPrePostRunString
)

class NXdetector_moduleModel(NXgroupModel):
    
    class CommonModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            transformation_type: Optional[str] = Field(None, description="Obligatory value: translation")
            vector: Optional[NXfieldModelForAttribute] = Field(None, description="Three values that define the axis for this transformation")
            offset: Optional[NXfieldModelForAttribute] = Field(None, description="A fixed offset applied before the transformation (three vector components).")
            offset_units: Optional[NXfieldModelForAttribute] = Field(None, description="Units of the offset.")
            depends_on: Optional[NXfieldModelForAttribute] = Field(None, description="Points to the path of the next element in the geometry chain.")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to field: 'module_offset' or 'fast_pixel_direction' or 'slow_pixel_direction'.")

    default: NXattrModel = Field(NXattrModel(value="data_origin"), description='Default')
    data_origin: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="A dimension-2 or dimension-3 field which gives the indices of the origin of the hyperslab of data for this module in the main area detector image in the parent NXdetector module.")
    data_size: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Two or three values for the size of the module in pixels in each direction. Dimensionality and order of indices is the same as for data_origin.")
    module_offset: Optional[CommonModel] = Field(None, description="Offset of the module in regards to the origin of the detector in an arbitrary direction.")
    fast_pixel_direction: Optional[CommonModel] = Field(None, description="Values along the direction of fastest varying pixel direction.")
    slow_pixel_direction: Optional[CommonModel] = Field(None, description="Values along the direction of slowest varying pixel direction.")
    depends_on: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Points to the start of the dependency chain for this module.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
