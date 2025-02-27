from typing import Optional
from bluesky_nexus.models.nx_core_models import (
    Field,
    ConfigDict,
    NXattrModel,
    NXgroupModel,
    NXfieldModelWithPrePostRunString
)

class NXoff_geometryModel(NXgroupModel):
    
    default: NXattrModel = Field(NXattrModel(value="faces"), description='Default')
    vertices: Optional[NXfieldModelWithPrePostRunString] = Field(None, description='List of x,y,z coordinates for vertices.')
    winding_order: Optional[NXfieldModelWithPrePostRunString] = Field(None,description='List of indices of vertices in the vertices dataset to form each face, right-hand rule for face normal.')
    faces: Optional[NXfieldModelWithPrePostRunString] = Field(None,description='The start index in winding_order for each face.' )
    detector_faces: Optional[NXfieldModelWithPrePostRunString] = Field(None,description='List of pairs of index in the “faces” dataset and detector id.')
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")