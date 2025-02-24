
from typing import Optional
from bluesky_nexus.models.nx_core_models import (
    Field,
    ConfigDict,
    NXattrModel,
    NXgroupModel,
    NXfieldModel,
    NXfieldModelWithPrePostRunString
)

from bluesky_nexus.models.nx_data_model import NXdataModel
from bluesky_nexus.models.nx_off_geometry_model import NXoff_geometryModel
from bluesky_nexus.models.nx_crystal_model import NXcrystalModel
from bluesky_nexus.models.nx_grating_model import NXgratingModel
from bluesky_nexus.models.nx_transformations_model import NXtransformationsModel

class NXmonochromatorModel(NXgroupModel):
    
    default: NXattrModel = Field(NXattrModel(value="energy"), description='Default')
    wavelength: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Wavelength selected")
    wavelegth_errors: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Wavelength standard deviation")
    energy: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Energy selected")
    energy_errors: Optional[NXfieldModelWithPrePostRunString] = Field (None, description="Energy standard deviation")
    depends_on: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="NeXus positions components by applying a set of translations and rotations")
    distribution: Optional[NXdataModel] = Field(None)
    OFF_GEOMETRY: Optional[NXoff_geometryModel] = Field(None, description='This group describes the shape of the beam line component')
    CRYSTAL: Optional[NXcrystalModel] = Field(None, description="Use as many crystals as necessary to describe")
    GRATING: Optional[NXgratingModel] = Field(None, description="For diffraction grating based monochromators")
    TRANSFORMATIONS: Optional[NXtransformationsModel] = Field(None, description="This is the group recommended for holding the chain of translation and rotation operations necessary to position the component within the instrument. ")
    #description: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Description of the monochromator")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
