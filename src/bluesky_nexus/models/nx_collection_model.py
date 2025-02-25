
from bluesky_nexus.models.nx_core_models import (
    ConfigDict,
    NXgroupModel,
)

class NXcollectionModel(NXgroupModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
