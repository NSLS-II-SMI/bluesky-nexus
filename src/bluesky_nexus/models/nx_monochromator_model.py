"""
nx_monochromator_model: Model for managing monochromator-related metadata and configuration.

This module defines a model that organizes and manages metadata and configuration specific to
monochromators in an experimental setup. It includes attributes for describing the wavelength,
energy, diffraction grating, crystal properties, and transformations related to the monochromator
component in a NeXus-compliant format.

Classes:
    - NXmonochromatorModel: Model for managing monochromator-related metadata and configuration.

"""

from typing import Optional
from bluesky_nexus.models.nx_core_models import (
    Field,
    ConfigDict,
    NXattrModel,
    NXgroupModel,
    NXfieldModelWithPrePostRunString,
)

from bluesky_nexus.models.nx_data_model import NXdataModel
from bluesky_nexus.models.nx_off_geometry_model import NXoff_geometryModel
from bluesky_nexus.models.nx_crystal_model import NXcrystalModel
from bluesky_nexus.models.nx_grating_model import NXgratingModel
from bluesky_nexus.models.nx_transformations_model import NXtransformationsModel


class NXmonochromatorModel(NXgroupModel):
    """
    Model for managing monochromator-related metadata and configuration.

    This class organizes and manages metadata and configuration specific to monochromators
    in an experimental setup. It allows for the inclusion of key attributes such as wavelength,
    energy, diffraction grating, crystal properties, and transformation operations related to
    the monochromator component.

    Attributes:
        default (NXattrModel): Default attribute, typically for energy selection.
        wavelength (Optional[NXfieldModelWithPrePostRunString]): The selected wavelength.
        wavelength_errors (Optional[NXfieldModelWithPrePostRunString]): Standard deviation for the wavelength.
        energy (Optional[NXfieldModelWithPrePostRunString]): The selected energy.
        energy_errors (Optional[NXfieldModelWithPrePostRunString]): Standard deviation for the energy.
        depends_on (Optional[NXfieldModelWithPrePostRunString]): Translation and rotation operations.
        distribution (Optional[NXdataModel]): Distribution data related to the monochromator.
        OFF_GEOMETRY (Optional[NXoff_geometryModel]): Describes the shape of the beam line component.
        CRYSTAL (Optional[NXcrystalModel]): Properties for diffraction crystals.
        GRATING (Optional[NXgratingModel]): Grating properties for diffraction-based monochromators.
        TRANSFORMATIONS (Optional[NXtransformationsModel]): Transformation chain for component positioning.
        description (Optional[NXfieldModelWithPrePostRunString]): Description of the monochromator.

    Config:
        model_config (ConfigDict): A configuration model that allows arbitrary types and extra fields,
        providing flexibility for different metadata or attributes.
    """

    default: NXattrModel = Field(NXattrModel(value="energy"), description="Default.")
    wavelength: Optional[NXfieldModelWithPrePostRunString] = Field(
        None, description="Wavelength selected."
    )
    wavelegth_errors: Optional[NXfieldModelWithPrePostRunString] = Field(
        None, description="Wavelength standard deviation."
    )
    energy: Optional[NXfieldModelWithPrePostRunString] = Field(
        None, description="Energy selected."
    )
    energy_errors: Optional[NXfieldModelWithPrePostRunString] = Field(
        None, description="Energy standard deviation."
    )
    depends_on: Optional[NXfieldModelWithPrePostRunString] = Field(
        None,
        description="NeXus positions components by applying a set of translations and rotations.",
    )
    distribution: Optional[NXdataModel] = Field(None, description="Distribution.")
    OFF_GEOMETRY: Optional[NXoff_geometryModel] = Field(
        None, description="This group describes the shape of the beam line component."
    )
    CRYSTAL: Optional[NXcrystalModel] = Field(
        None, description="Use as many crystals as necessary to describe."
    )
    GRATING: Optional[NXgratingModel] = Field(
        None, description="For diffraction grating based monochromators."
    )
    TRANSFORMATIONS: Optional[NXtransformationsModel] = Field(
        None,
        description="This is the group recommended for holding the chain of translation and rotation operations necessary to position the component within the instrument.",
    )
    description: Optional[NXfieldModelWithPrePostRunString] = Field(
        None, description="Description of the monochromator."
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
