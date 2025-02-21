"""
Module: nexusformat_models_hzb.py

This module defines Pydantic models tailored for device classes used at HZB's BESSY II facility. The models ensure
structured validation and organization of data for different device types.

Classes:
    - NXgratingModel: A model for grating components, used in monochromators.
    - NXmonochromatorModel: A model representing a monochromator, including energy and grating details.
    - NXgeneralModel: A generic model applicable to all device classes except Monitor, Monochromator, and Detector.

Mappings:
    MODEL_NAME_TO_CLASS_MAPPING: A dictionary mapping model names to their respective class definitions, allowing
    dynamic resolution of models by name.
"""

from typing import Optional

from bluesky_nexus.models.nexusformat_models import (
    Field,
    ConfigDict,
    NXattrModel,
    NXfieldModel,
    NXgroupModel,
)

__all__ = ["NXmonochromatorModel", "NXgeneralModel", "MODEL_NAME_TO_CLASS_MAPPING"]

class NXtransformationsModel(NXgroupModel):
    """
    Collection of axis-based translations and rotations to 
    describe a geometry.
    """

    default: Optional[NXattrModel] = Field(
        None,
        description='Default'
    )

    AXISNAME: Optional[NXfieldModel] = Field(
        None,
        description='AXISNAME'
    )

    AXISNAME_end: Optional[NXfieldModel] = Field(
        None,
        description='AXISNAME_end'
    )

    AXISNAME_increment_set: Optional[NXfieldModel] = Field(
        None,
        description='AXISNAME_increment_set'
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class NXdataModel(NXgroupModel):

    AXISNAME: Optional[NXfieldModel]= Field(
        None,
        description='Coordinate values along one or more data dimensions.'
    )

    DATA: Optional[NXfieldModel] = Field(
        None,
        description='Data values to be used as the NeXus plottable data.'
    )

    FIELDNAME_errors: Optional[NXfieldModel] = Field(
        None,
        description='Errors (uncertainties or standard deviations) for the data values.'
    )

    scaling_factor: Optional[NXfieldModel] = Field(
        None,
        description='Scaling factor to apply to the data.'
    )
    
    offset: Optional[NXfieldModel] = Field(
        None,
        description='Optional offset to apply to the data values.'
    )
    
    title: Optional[NXfieldModel] = Field(
        None,
        description='Title for the plot.'
    )
    
    x: Optional[NXfieldModel] = Field(
        None,
        description='Array of x-axis values for the plot.'
    )
    
    y: Optional[NXfieldModel] = Field(
        None,
        description='Array of y-axis values for the plot.'
    )
    
    z: Optional[NXfieldModel] = Field(
        None,
        description='Array of z-axis values for the plot.'
    )
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


class NXlogModel(NXgroupModel):

    default: Optional[NXattrModel] = Field(
        None,
        description="Declares which child group contains a path leading to the primary data."
    )

    time: Optional[NXfieldModel] = Field(
        None,
        description="Time of logged entry, relative to the 'start' attribute."
    )

    value: Optional[NXfieldModel] = Field(
        None,
        description="Array of logged values, such as temperature."
    )

    raw_value: Optional[NXfieldModel] = Field(
        None,
        description="Array of raw information, such as thermocouple voltage."
    )

    description: Optional[NXfieldModel] = Field(
        None,
        description="Description of the logged value."
    )

    average_value: Optional[NXfieldModel] = Field(
        None,
        description="Average of the logged values."
    )

    average_value_errors: Optional[NXfieldModel] = Field(
        None,
        description="Estimated uncertainty (e.g., standard deviation) of average_value."
    )

    minimum_value: Optional[NXfieldModel] = Field(
        None,
        description="Minimum recorded value."
    )

    maximum_value: Optional[NXfieldModel] = Field(
        None,
        description="Maximum recorded value."
    )

    duration: Optional[NXfieldModel] = Field(
        None,
        description="Total duration over which the log was recorded."
    )

    cue_timestamp_zero: Optional[NXfieldModel] = Field(
        None,
        description="Timestamps corresponding to cue_index."
    )

    cue_index: Optional[NXfieldModel] = Field(
        None,
        description="Index into the time, value pair matching the corresponding cue_timestamp_zero."
    )

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


class NXoff_geometryModel(NXgroupModel):
    
    deafult: Optional[NXattrModel] = Field(
        None,
        description='Default'
    )

    vertices: Optional[NXfieldModel] = Field(
        None,
        description='vertices'
    )

    winding_order: Optional[NXfieldModel] = Field(
        None,
        description='winding_order'
    )

    faces: Optional[NXfieldModel] = Field(
        None,
        description='faces'
    )

    detector_faces: Optional[NXfieldModel] = Field(
        None,
        description='detector_faces'
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class NXcrystalModel(NXgroupModel):
    """"
    A crystal monochromator or analyzer.
    """

    default: Optional[NXattrModel] = Field(
            None,
            description='Default'
        )

    usage: Optional[NXfieldModel] = Field(
        None,
        description = 'usage' 
    )

    type: Optional[NXfieldModel] = Field(
        None,
        description = 'type'
    )  

    chemical_formula: Optional[NXfieldModel] = Field(
        None,
        description = 'chemical_formula'
    )

    order_no: Optional[NXfieldModel] = Field(
        None,
        description='order_no'
    )

    cut_angle: Optional[NXfieldModel] = Field(
        None,
        description='cut_angle'
    )

    space_group: Optional[NXfieldModel] = Field(
        None,
        description='space_group'
    )

    unit_cell: Optional[NXfieldModel] = Field(
        None,
        description='unit_cell'
    )

    unit_cell_a: Optional[NXfieldModel] = Field(
        None,
        description='unit_cell_a'
    )

    unit_cell_b: Optional[NXfieldModel] = Field(
        None,
        description='unit_cell_b'
    )

    unit_cell_c: Optional[NXfieldModel] = Field(
        None,
        description='unit_cell_c'
    )

    unit_cell_alpha: Optional[NXfieldModel] = Field(
        None,
        description='unit_cell_alpha'
    )

    unit_cell_beta: Optional[NXfieldModel] = Field(
        None,
        description='unit_cell_beta'
    )

    unit_cell_gamma: Optional[NXfieldModel] = Field(
        None,
        description='unit_cell_gamma'
    )

    unit_cell_volume: Optional[NXfieldModel] = Field(
        None,
        description='unit_cell_volume'
    )

    orientation_matrix: Optional[NXfieldModel] = Field(
        None,
        description='orientation_matrix'
    )

    wavelength: Optional[NXfieldModel] = Field(
        None,
        description='wavelength'
    )

    d_spacing: Optional[NXfieldModel] = Field(
        None,
        description='d_spacing'
    )

    scattering_vector: Optional[NXfieldModel] = Field(
        None,
        description='scattering_vector'
    )

    reflection: Optional[NXfieldModel] = Field(
        None,
        description='reflection'
    )

    thickness: Optional[NXfieldModel] = Field(
        None,
        description='thickness'
    )

    density: Optional[NXfieldModel] = Field(
        None,
        description='density'
    )

    segment_width: Optional[NXfieldModel] = Field(
        None,
        description='segment_width'
    )

    segment_height: Optional[NXfieldModel] = Field(
        None,
        description='segment_height'
    )

    segment_thickness: Optional[NXfieldModel] = Field(
        None,
        description='segment_thickness'
    )

    segment_gap: Optional[NXfieldModel] = Field(
        None,
        description='segment_gap'
    )

    segment_column: Optional[NXfieldModel] = Field(
        None,
        description='segment_column'
    )

    segment_rows: Optional[NXfieldModel] = Field(
        None,
        description='segment_rows'
    )

    mosaic_horizontal: Optional[NXfieldModel] = Field(
        None,
        description='mosaic_horizontal'
    )

    mosaic_vertical: Optional[NXfieldModel] = Field(
        None,
        description='mosaic_vertical'
    )

    curvature_horizontal: Optional[NXfieldModel] = Field(
        None,
        description='curvature_horizontal'
    )
    
    curvature_vertical: Optional[NXfieldModel] = Field(
        None,
        description='curvature_horizontal'
    )

    is_cylindrical: Optional[NXfieldModel] = Field(
        None,
        description='is_cylindrical'
    )

    cylindrical_orientation_angle: Optional[NXfieldModel] = Field(
        None,
        description='cylindrical_orientation_angle'
    )

    polar_angle: Optional[NXfieldModel] = Field(
        None,
        description='polar_angle'
    )

    azimuthal_angle: Optional[NXfieldModel] = Field(
        None,
        description='azimuthal_angle'
    )

    bragg_angle: Optional[NXfieldModel] = Field(
        None,
        description='bragg_angle'
    )

    temperature: Optional[NXfieldModel] = Field(
        None,
        description='temperature'
    )

    temperature_coefficient: Optional[NXfieldModel] = Field(
        None,
        description='temperature_coefficient'
    )

    depends_on: Optional[NXfieldModel] = Field(
        None,
        description='depends_on'
    )

    temperature_log: Optional[NXlogModel] = Field(
        None,
        description='temperature_log'
    )

    reflectivity: Optional[NXgroupModel] = Field(
        None,
        description='reflectivity'
    )
    
    transmission: Optional[NXdataModel] = Field(
    None,
    description='crystal transmission versus wavelength'
    )
    
    OFF_GEOMETRY: Optional[NXoff_geometryModel] = Field(
        None,
        description='off_geometry'
    )
    
    TRANSFORMATIONS: Optional[NXtransformationsModel] = Field(
        None,
        description='Transformations used by this component to define its position and orientation.'
    )  
    
    
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


# This is the model which describes the structure of the data from a grating component of a mono
class NXgratingModel(NXgroupModel):
    """
    A diffraction grating, as could be used in a soft X-ray monochromator
    """

    default: Optional[NXattrModel] = Field(
        None,
        description='Default'
    ) # Remember to implement the default child group path leading to NXdata in yml

    angles: Optional[NXfieldModel] = Field(
        None,
        description='angles'
    )

    period: Optional[NXfieldModel] = Field(
        None,
        description='period'
    )

    duty_cycle: Optional[NXfieldModel] = Field(
        None,
        description='duty_cycle'
    )

    depth: Optional[NXfieldModel] = Field(
        None,
        description='depth'
    )

    diffraction_order: Optional[NXfieldModel] = Field(
        None, 
        description='Diffraction order'
        )

    deflection_angle: Optional[NXfieldModel] = Field(
        None,
        description='deflection_angle'
    )

    interior_atmoshpere: Optional[NXfieldModel] = Field(
        None,
        description='interior_atmoshpere'
    )
    
    substrate_material: Optional[NXfieldModel] = Field(
        None, 
        description='Substrate material'
        )

    substrate_density: Optional[NXfieldModel] = Field(
        None,
        description='substrate_density'
    )

    substrate_thickness: Optional[NXfieldModel] = Field(
        None,
        description='substrate_density'
    )

    coating_material: Optional[NXfieldModel] = Field(
        None,
        description='coating_material'
    )

    substrate_roughness: Optional[NXfieldModel] = Field(
        None,
        description='substrate_roughness'
    )

    layer_thickness: Optional[NXfieldModel] = Field(
        None,
        description='layer_thickness'
    )

    depends_on: Optional[NXfieldModel] = Field(
        None,
        description='depends_on'
    )

    figure_data: Optional[NXgroupModel] = Field(
        None,
        description='figure_data'
    )    

    OFF_GEOMETRY: Optional[NXoff_geometryModel] = Field(
        None,
        description='off_geometry'
    )

    TRANSFORMATIONS: Optional[NXtransformationsModel] = Field(
        None,
        description='TRANSFORMATIONS'
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

class NXmonochromatorModel(NXgroupModel):
    default: NXattrModel = Field(NXattrModel(value="energy"), description='Default')

    wavelength: Optional[NXfieldModel] = Field(
        None, 
        description='wavelength selected'
        )
    
    wavelegth_errors: Optional[NXfieldModel] = Field(
        None, 
        description='wavelength standard deviation'
        )
    
    energy: Optional[NXfieldModel] = Field(None, description='energy selected')

    energy_errors: Optional[NXfieldModel] = Field (None, description='energy standard deviation')

    depends_on: Optional[NXfieldModel] = Field(
        None, 
        description='NeXus positions components by applying a set of translations and rotations '
        )

    distribution: Optional[NXdataModel] = Field(None)


    OFF_GEOMETRY: Optional[NXoff_geometryModel] = Field(
        None,
        description='This group describes the shape of the beam line component'
    )

    CRYSTAL: Optional[NXcrystalModel] = Field(
        None, 
        description='Use as many crystals as necessary to describe'
    )
    
    GRATING: Optional[NXgratingModel] = Field(
        None, 
        description='grating'
    )

    TRANSFORMATIONS: Optional[NXtransformationsModel] = Field(
        None,
        description='TRANSFORMATIONS'
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class NXgeneralModel(NXgroupModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

# Define a mapping between model name and class name
MODEL_NAME_TO_CLASS_MAPPING = {
    "NXmonochromatorModel": NXmonochromatorModel,
    "NXgeneralModel": NXgeneralModel,
}
