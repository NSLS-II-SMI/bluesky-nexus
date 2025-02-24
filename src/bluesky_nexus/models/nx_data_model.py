
from typing import List, Optional, Union
from bluesky_nexus.models.nx_core_models import (
    BaseModel,
    Scalar,
    Field,
    ConfigDict,
    NXgroupModel,
    NXfieldModelWithPrePostRunString
)

class NXdataModel(NXgroupModel):
    
    # ----- Define attributes of the NXData group -----
    class AttributesModel(BaseModel):
        signal: Optional[str] = Field(None, description="The value is the name of the signal that contains the default plottable data.")
        auxiliary_signals: Optional[List[str]] = Field(None, description="Array of strings holding the names of additional signals to be plotted with the default signal. ")
        default_slice: Optional[Scalar] = Field(None, description="Which slice of data to show in a plot by default.")
        AXISNAME_indices: Optional[List[int]]  = Field(None, description="The AXISNAME_indices attribute is a single integer or an array of integers that defines which data dimension(s) are spanned by the corresponding axis. The first dimension index is 0 (zero).")
        axes: Optional[List[str]]  = Field(None, description="The axes attribute is a list of strings which are the names of the AXISNAME fields that contain the values of the coordinates along the data dimensions.")
        model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    
    attrs: Optional[AttributesModel] = Field(None, description="Attributes specific to the NXdata group.")

    # ----- AXISNAME -----
    class AXISNAMEModel(NXfieldModelWithPrePostRunString):
        
        class AttributesModel(BaseModel):
            long_name: Optional[str] = Field(None, description="Axis label")
            units: Optional[str] = Field(None, description="Unit in which the coordinate values are expressed")
            distribution: Optional[bool] = Field(None, description="0|false: single value, 1|true: multiple values")
            first_good: Optional[int] = Field(None, description="Index of first good value")
            last_good: Optional[int] = Field(None, description="Index of last good value")
            axis: Optional[int] = Field(None, gt=0, description="Index (positive integer) identifying this specific set of numbers.")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
            
        attrs: Optional[AttributesModel] = Field(None, description="Attributes specific to the AXISNAME field.")

    AXISNAME: Optional[AXISNAMEModel]= Field(None, description='Coordinate values along one or more data dimensions.')

    # ----- DATA -----
    class DATAModel(NXfieldModelWithPrePostRunString):
        
        class AttributesModel(BaseModel):
            signal: Optional[int] = Field(None, gt=0, description="Plottable (independent) axis, indicate index number. ")
            axes: Optional[str] = Field(None, description="Defines the names of the coordinates (independent axes) for this data set as a colon-delimited array")
            long_name: Optional[bool] = Field(None, description="data label")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

        attrs: Optional[AttributesModel] = Field(None, description="Attributes specific to the DATA field.")

    DATA: Optional[DATAModel] = Field(None, description='Data values to be used as the NeXus plottable data. ')
    FIELDNAME_errors: Optional[NXfieldModelWithPrePostRunString] = Field(None, description='“Errors” (meaning uncertainties or standard deviations) associated with any field named FIELDNAME in this NXdata group (e.g. an axis, signal or auxiliary signal).')
    scaling_factor: Optional[NXfieldModelWithPrePostRunString] = Field(None, description='The elements in data are usually float values really. For efficiency reasons these are usually stored as integers after scaling with a scale factor. This value is the scale factor. It is required to get the actual physical value, when necessary.')
    offset: Optional[NXfieldModelWithPrePostRunString] = Field(None, description='An optional offset to apply to the values in data.')
    title: Optional[NXfieldModelWithPrePostRunString] = Field(None, description='Title for the plot.')
    x: Optional[NXfieldModelWithPrePostRunString] = Field(None, description='Array of x-axis values for the plot.')
    y: Optional[NXfieldModelWithPrePostRunString] = Field(None, description='Array of y-axis values for the plot.')
    z: Optional[NXfieldModelWithPrePostRunString] = Field(None,description='Array of z-axis values for the plot.')
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")