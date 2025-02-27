
from typing import Optional
from bluesky_nexus.models.nx_core_models import (
    Field,
    ConfigDict,
    NXattrModel,
    NXgroupModel,
    NXfieldModelWithPrePostRunString
)

from bluesky_nexus.models.nx_log_model import NXlogModel
from bluesky_nexus.models.nx_data_model import NXdataModel
from bluesky_nexus.models.nx_off_geometry_model import NXoff_geometryModel
from bluesky_nexus.models.nx_transformations_model import NXtransformationsModel

class NXcrystalModel(NXgroupModel):

    default: NXattrModel = Field(NXattrModel(value="wavelength"), description='Default')
    usage: Optional[NXfieldModelWithPrePostRunString] = Field(None, description = "How this crystal is used. Choices are in the list.")
    type: Optional[NXfieldModelWithPrePostRunString] = Field(None, description = "Type or material of monochromating substance.")  
    chemical_formula: Optional[NXfieldModelWithPrePostRunString] = Field(None, description = 'The chemical formula specified using CIF conventions.')
    order_no: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="A number which describes if this is the first, second,.. crystal in a multi crystal monochromator.")
    cut_angle: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Cut angle of reflecting Bragg plane and plane of crystal surface.")
    space_group: Optional[NXfieldModelWithPrePostRunString] = Field(None, description='Space group of crystal structure')
    unit_cell: Optional[NXfieldModelWithPrePostRunString] = Field(None,description="Unit cell parameters (lengths and angles)")
    unit_cell_a: Optional[NXfieldModelWithPrePostRunString] = Field(None,description='Unit cell lattice parameter: length of side a')
    unit_cell_b: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Unit cell lattice parameter: length of side b")
    unit_cell_c: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Unit cell lattice parameter: length of side c")
    unit_cell_alpha: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Unit cell lattice parameter: angle alpha")
    unit_cell_beta: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Unit cell lattice parameter: angle beta")
    unit_cell_gamma: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Unit cell lattice parameter: angle gamma")
    unit_cell_volume: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Volume of the unit cell")
    orientation_matrix: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Orientation matrix of single crystal sample using Busing-Levy convention:")
    wavelength: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Optimum diffracted wavelength")
    d_spacing: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Spacing between crystal planes of the reflection")
    scattering_vector: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Scattering vector, Q, of nominal reflection")
    reflection: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Miller indices (hkl) values of nominal reflection")
    thickness: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Thickness of the crystal. (Required for Laue orientations - see “usage” field)")
    density: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="mass density of the crystal.")
    segment_width: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Horizontal width of individual segment")
    segment_height: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Vertical height of individual segment")
    segment_thickness: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Thickness of individual segment")
    segment_gap: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Typical gap between adjacent segments")
    segment_columns: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Number of segment columns in horizontal direction")
    segment_rows: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Number of segment rows in vertical direction")
    mosaic_horizontal: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Horizontal mosaic Full Width Half Maximum")
    mosaic_vertical: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Vertical mosaic Full Width Half Maximum")
    curvature_horizontal: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Horizontal curvature of focusing crystal")
    curvature_vertical: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Vertical curvature of focusing crystal")
    is_cylindrical: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Is this crystal bent cylindrically?")
    cylindrical_orientation_angle: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="If cylindrical: cylinder orientation angle")
    polar_angle: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Polar (scattering) angle at which crystal assembly is positioned. Note: some instrument geometries call this term 2theta. Note: it is recommended to use NXtransformations instead.")
    azimuthal_angle: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Azimuthal angle at which crystal assembly is positioned. Note: it is recommended to use NXtransformations instead.")
    bragg_angle: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="Bragg angle of nominal reflection")
    temperature: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="average/nominal crystal temperature.")
    temperature_coefficient: Optional[NXfieldModelWithPrePostRunString] = Field(None, description="how lattice parameter changes with temperature")
    depends_on: Optional[NXfieldModelWithPrePostRunString] = Field(None,description="NeXus positions components by applying a set of translations and rotations to apply to the component starting from 0, 0, 0. ")
    temperature_log: Optional[NXlogModel] = Field(None, description="log file of crystal temperature.")
    reflectivity: Optional[NXdataModel] = Field(None, description="crystal reflectivity versus wavelength.")
    transmission: Optional[NXdataModel] = Field(None, description="crystal transmission versus wavelength.")
    OFF_GEOMETRY: Optional[NXoff_geometryModel] = Field(None, description="This group describes the shape of the beam line component")
    TRANSFORMATIONS: Optional[NXtransformationsModel] = Field(None, description="Transformations used by this component to define its position and orientation.")  
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
