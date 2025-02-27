
from typing import Optional
from bluesky_nexus.models.nx_core_models import (
    Field,
    ConfigDict,
    NXgroupModel,
    NXfieldModelWithPrePostRunString
)

class NXdetector_channelModel(NXgroupModel):
    
    threshold_energy: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Energy at which a photon will be recorded.")
    flatfield_applied: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="True when the flat field correction has been applied in the electronics, false otherwise.")
    flatfield: Optional[NXfieldModelWithPrePostRunString] = Field(None, description = "Response of each pixel given a constant input.")
    flatfield_errors: Optional[NXfieldModelWithPrePostRunString] = Field(None, description = "Errors of the flat field correction data. The form flatfield_error is deprecated.")
    pixel_mask_applied: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="True when the pixel mask correction has been applied in the electronics, false otherwise.")
    pixel_mask: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Custom pixel mask for this channel. May include nP as the first dimension for masks that vary for each scan point.")
    saturation_value: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="The value at which the detector goes into saturation. Especially common to CCD detectors, the data is known to be invalid above this value.")
    underload_value: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="The lowest value at which pixels for this detector would be reasonably measured. The data is known to be invalid below this value.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
