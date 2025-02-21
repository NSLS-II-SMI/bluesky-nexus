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
    NXattrModelWithString,
    NXgroupModel,
    NXfieldModelWithPrePostRunString,
)

__all__ = ["NXmonochromatorModel", "NXgeneralModel", "MODEL_NAME_TO_CLASS_MAPPING"]
 
 
 
 

# ------------------------ Models copied 1:1 from:
# - https://codebase.helmholtz.cloud/rock-it/wp2/structured_metadata/-/blob/demonstrator-hzb/demonstrator/hzb/example/demonstrator_hzb.ipynb?ref_type=heads
# - https://codebase.helmholtz.cloud/rock-it/wp2/structured_metadata/-/tree/demonstrator-hzb/blueData/data/models?ref_type=heads 
#
# Problems visible on the first view:
# - Spelling problems: e.g. 'wavelegth_error'
# - Indentation problems: e.g. the  whole 'NXcrystalModel' class, the whole 'NXtransformationsModel' class
# - Contain deprecated fields e.g. 'energy_error', 'wavelegth_error'
# - obsolete function(s) in NXmonochromatorModel: validate_and_convert_energy()
# - missing model(s) for NXmonochromatorModel : NXdata
# ------------------------
 
class NXmonochromatorModel(NXgroupModel):
    default: NXattrModelWithString = Field(NXattrModel(value="energy"),
                                 description='Default')

        
    wavelength: NXfieldModelWithFloat = Field(
        None, 
        description='wavelength',
        units='angstrom'
        )
    wavelegth_error: NXfieldModelWithFloat = Field(
        None, 
        description='wavelength_error'
        )
    energy: NXfieldModelWithFloat = Field(None, description='energy')
    energy_error: NXfieldModelWithFloat = Field (None)

    CRYSTAL: Optional[NXcrystalModel] = Field(
        None, 
        description='crystal'
    )

    GRATING: Optional[NXgratingModel] = Field(
        None, 
        description='grating'
    )
    OFF_GEOMETRY: Optional[NXoff_geometryModel] = Field(
        None,
        description='off_geometry'
    )
    TRANSFORMATIONS: Optional[NXtransformationsModel] = Field(
        None,
        description='TRANSFORMATIONS'
    )

    @field_validator('energy', mode='before')
    def validate_and_convert_energy(cls, value):
        if isinstance(value, dict):
            energy_value = value.get('value')
            attrs = value.get('attrs', {})
            unit = attrs.get('units')
            if unit and isinstance(energy_value, (int, float)):
                quantity = energy_value * getattr(u, unit)
                desired_unit = u.keV
                
                if unit != 'keV':
                    converted_quantity = quantity.to(desired_unit)
                    value['value'] = converted_quantity.value
                    value['attrs']['units'] = 'keV'
        return value
    
    def dtype_validation(self):
        for name, _ in self.__annotations__.items():
            attr = getattr(self, name)
            if isinstance(attr, (NXfieldModel, NXattrModel)):
                try:
                    value = np.array(attr.value, dtype=attr.dtype)
                    if attr.shape:
                        value = value.reshape(attr.shape)
                    attr.value = value
                except Exception as e:
                    raise ValidationError([{
                        'loc': (name, 'value'),
                        'msg': f'Error converting value to {attr.dtype} with shape {attr.shape}',
                        'type': 'dtype_error'
                    }])
    
    class Config:
        extra = 'allow'


class NXcrystalModel(NXgroupModel):
    """"
    A crystal monochromator or analyzer.
    """

default: Optional[NXattrModelWithString] = Field(
        None,
        description='Default'
    )

usage: Optional[NXfieldModelWithString] = Field(
    None,
    description = 'usage' 
)

type: Optional[NXfieldModelWithString] = Field(
    None,
    description = 'type'
)  

chemical_formula: Optional[NXfieldModelWithString] = Field(
    None,
    description = 'chemical_formula'
)

order_no: Optional[NXfieldModelWithInt] = Field(
    None,
    description='order_no'
)

cut_angle: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='cut_angle'
)

space_group: Optional[NXfieldModelWithString] = Field(
    None,
    description='space_group'
)

unit_cell: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='unit_cell'
)

unit_cell_a: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='unit_cell_a'
)

unit_cell_b: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='unit_cell_b'
)

unit_cell_c: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='unit_cell_c'
)

unit_cell_alpha: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='unit_cell_alpha'
)

unit_cell_beta: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='unit_cell_beta'
)

unit_cell_gamma: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='unit_cell_gamma'
)

unit_cell_volume: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='unit_cell_volume'
)

orientation_matrix: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='orientation_matrix'
)

wavelength: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='wavelength'
)

d_spacing: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='d_spacing'
)

scattering_vector: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='scattering_vector'
)

reflection: Optional[NXfieldModelWithInt] = Field(
    None,
    description='reflection'
)

thickness: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='thickness'
)

density: Optional[NXfieldModelWithInt] = Field(
    None,
    description='density'
)

segment_width: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='segment_width'
)

segment_height: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='segment_height'
)

segment_thickness: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='segment_thickness'
)

segment_gap: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='segment_gap'
)

segment_column: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='segment_column'
)

segment_rows: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='segment_rows'
)

mosaic_horizontal: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='mosaic_horizontal'
)

mosaic_vertical: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='mosaic_vertical'
)

curvature_horizontal: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='curvature_horizontal'
)

is_cylindrical: Optional[NXfieldModel] = Field(
    None,
    description='is_cylindrical'
) # NXfieldModelWithBool to be added

cylindrical_orientation_angle: Optional[NXfieldModelWithInt] = Field(
    None,
    description='cylindrical_orientation_angle'
)

polar_angle: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='polar_angle'
)

azimuthal_angle: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='azimuthal_angle'
)

bragg_angle: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='bragg_angle'
)

temperature: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='temperature'
)

temperature_coefficient: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='temperature_coefficient'
)

depends_on: Optional[NXfieldModelWithString] = Field(
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


OFF_GEOMETRY: Optional[NXoff_geometryModel] = Field(
    None,
    description='off_geometry'
)


# This is the model which describes the structure of the data from a grating component of a mono
class NXgratingModel(NXgroupModel):
    """
    A diffraction grating, as could be used in a soft X-ray monochromator
    """

    default: Optional[NXattrModelWithString] = Field(
        None,
        description='Default'
    ) # Remember to implement the default child group path leading to NXdata in yml

    angles: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='angles'
    )

    period: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='period'
    )

    duty_cycle: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='duty_cycle'
    )

    depth: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='depth'
    )

    diffraction_order: Optional[NXfieldModelWithInt] = Field(
        None, 
        description='Diffraction order'
        )

    deflection_angle: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='deflection_angle'
    )

    interior_atmoshpere: Optional[NXfieldModelWithString] = Field(
        None,
        description='interior_atmoshpere'
    )
    
    substrate_material: Optional[NXfieldModelWithString] = Field(
        None, 
        description='Substrate material'
        )

    substrate_density: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='substrate_density'
    )

    substrate_thickness: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='substrate_density'
    )

    coating_material: Optional[NXfieldModelWithString] = Field(
        None,
        description='coating_material'
    )

    substrate_roughness: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='substrate_roughness'
    )

    layer_thickness: Optional[NXfieldModelWithFloat] = Field(
        None,
        description='layer_thickness'
    )

    depends_on: Optional[NXfieldModelWithString] = Field(
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

class NXoff_geometryModel(NXgroupModel):
    """
    Geometry (shape) description. The format closely matches
    the Object File Format (OFF) which can be output by most 
    CAD software. It can be used to describe the shape of 
    any beamline component, including detectors. In the case 
    of detectors it can be used to define the shape of a
    single pixel, or, if the pixel shapes are non-uniform, 
    to describe the shape of the whole detector.
    """

    deafult: Optional[NXattrModelWithString] = Field(
        None,
        description='Default'
    )

    vertices: Optional[NXfieldModelWithInt] = Field(
        None,
        description='vertices'
    ) # This is to be changed to NXFieldModelWithScalar

    winding_order: Optional[NXfieldModelWithInt] = Field(
        None,
        description='winding_order'
    )

    faces: Optional[NXfieldModelWithInt] = Field(
        None,
        description='faces'
    )

    detector_faces: Optional[NXfieldModelWithInt] = Field(
        None,
        description='detector_faces'
    )

class NXtransformationsModel(NXgroupModel):
    """
    Collection of axis-based translations and rotations to 
    describe a geometry.
    """

default: Optional[NXattrModelWithString] = Field(
    None,
    description='Default'
)

AXISNAME: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='AXISNAME'
)

AXISNAME_end: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='AXISNAME_end'
)

AXISNAME_increment_set: Optional[NXfieldModelWithFloat] = Field(
    None,
    description='AXISNAME_increment_set'
)

# ------------------------
# ------------------------ END OF Models copied 1:1 from
# ------------------------


# ------------------------
# ------------------------ Models used so far for test purposes ------------------------
# ------------------------

# This is the model which describes the structure of the data from a grating component of a mono
class NXgratingModelDeprecated(NXgroupModel):
    diffraction_order: NXfieldModelWithPrePostRunString = Field(
        None, description="Diffraction order value"
    )
    substrate_material: Optional[NXfieldModelWithPrePostRunString] = Field(
        None, description="Substrate material type"
    )


# This is the model for any NX Monchromator
class NXmonochromatorModelDeprecated(NXgroupModel):
    default: NXattrModelWithString = Field(
        NXattrModel(value="energy"), description="Default"
    )
    energy: NXfieldModelWithPrePostRunString = Field(None, description="Energy value")
    grating: NXgratingModel = Field(None, description="Grating")


# This is a general model for all classes but not Monitor, Monochromator, Detector
class NXgeneralModel(NXgroupModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


# ------------------------
# ------------------------ End of  Models used so far for test purposes ------------------------
# ------------------------




# Define a mapping between model name and class name
MODEL_NAME_TO_CLASS_MAPPING = {
    "NXmonochromatorModel": NXmonochromatorModel,
    "NXgeneralModel": NXgeneralModel,
}
