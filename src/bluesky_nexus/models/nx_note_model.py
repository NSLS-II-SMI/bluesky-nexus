
from typing import Optional
from bluesky_nexus.models.nx_core_models import (
    Field,
    ConfigDict,
    NXattrModel,
    NXgroupModel,
    NXfieldModelWithPrePostRunString
)

class NXnoteModel(NXgroupModel):
    default: NXattrModel = Field(NXattrModel(value="author"), description='Default')
    author: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Author or creator of note.")
    date: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Date note created/added.")
    type: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Mime content type of note data field e.g. image/jpeg, text/plain, text/html.")
    file_name: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Name of original file name if note was read from an external source.")
    description: Optional[NXfieldModelWithPrePostRunString] = Field (None, description="Title of an image or other details of the note.")
    sequence_index: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Sequence index of note, for placing a sequence of multiple NXnote groups in an order. Starts with 1.")
    data: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Binary note data - if text, line terminator is [CR][LF].")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
