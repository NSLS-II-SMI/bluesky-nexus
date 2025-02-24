
from typing import List, Optional, Union
from bluesky_nexus.models.nx_core_models import (
    BaseModel,
    Field,
    ConfigDict,
    NXattrModel,
    NXgroupModel,
    NXfieldModelWithPrePostRunString
)

class NXtransformationsModel(NXgroupModel):

    default: NXattrModel = Field(NXattrModel(value="TBD"), description='Default')

    # ----- AXISNAME -----
    class AXISNAMEModel(NXfieldModelWithPrePostRunString):

        class AttributesModel(BaseModel):
            transformation_type: Optional[str] = Field(None, description="The transformation_type may be translation, in which case the values are linear displacements along the axis, rotation, in which case the values are angular rotations around the axis.")
            vector: Optional[List[Union[int, float]]] = Field(None, description="Three values that define the axis for this transformation.")
            offset: Optional[List[Union[int, float]]] = Field(None, description="A fixed offset applied before the transformation (three vector components). ")
            offset_units: Optional[List[str]] = Field(None, description="Units of the offset. Values should be consistent with NX_LENGTH.")
            depends_on: Optional[str] = Field(None, description="Points to the path to a field defining the axis on which this depends or the string “.”.")
            equipment_component: Optional[str] = Field(None, description="An arbitrary identifier of a component of the equipment to which the transformation belongs, such as ‘detector_arm’ or ‘detector_module’.")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
            
        attrs: Optional[AttributesModel] = Field(None, description="Attributes specific to the AXISNAME field.")

    AXISNAME: Optional[AXISNAMEModel]= Field(None, description='Units need to be appropriate for translation or rotation.')
    AXISNAME_end: Optional[NXfieldModelWithPrePostRunString]= Field(None, description='AXISNAME_end is a placeholder for a name constructed from the actual name of an axis to which _end has been appended.')
    AXISNAME_increment_set: Optional[NXfieldModelWithPrePostRunString]= Field(None, description='AXISNAME_increment_set is a placeholder for a name constructed from the actual name of an axis to which _increment_set has been appended.')
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
