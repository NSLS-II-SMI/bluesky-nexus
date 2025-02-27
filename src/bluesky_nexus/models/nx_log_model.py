
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

class NXlogModel(NXgroupModel):
    
    default: NXattrModel = Field(NXattrModel(value="TBD"), description='Default')

    # ----- time -----
    class timeModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            start: Optional[NXfieldModelForAttribute] = Field(None)
            scaling_factor: Optional[NXfieldModelForAttribute] = Field(None)
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'time' field.")

    time: Optional[timeModel] = Field(None, description="Time of logged entry. The times are relative to the “start” attribute and in the units specified in the “units” attribute. Please note that absolute timestamps under unix are relative to 1970-01-01T00:00:00.0Z.")
    value: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Array of logged value, such as temperature. If this is a single value the dimensionality is nEntries.")
    raw_value: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Array of raw information, such as thermocouple voltage")
    description: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Description of logged value.")
    average_value: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Average of the logged values.")
    average_value_errors: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="estimated uncertainty (often used: standard deviation) of average_value")
    minimum_value: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Minimum recorded value.")
    maximum_value: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Maximum recorded value.")
    duration: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Total time log was taken")

    class cue_timestamp_zeroModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            start: Optional[NXfieldModelForAttribute] = Field(None, description="If missing start is assumed to be the same as for “time”.")
            scaling_factor: Optional[NXfieldModelForAttribute] = Field(None, description="If missing start is assumed to be the same as for “time”.")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'cue_timestamp_zero' field.")

    cue_timestamp_zero: Optional[cue_timestamp_zeroModel] = Field(None, description="Timestamps matching the corresponding cue_index into the time, value pair.")
    cue_index: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Index into the time, value pair matching the corresponding cue_timestamp_zero.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")