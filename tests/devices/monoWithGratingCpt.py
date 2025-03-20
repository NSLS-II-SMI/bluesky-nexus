from ophyd import Component as Cpt
from ophyd import Device, Signal
from ophyd.sim import SynAxis
from bluesky_nexus.bluesky_nexus_device_decorators import NxSchemaLoader
from .nx_schema.monoWithGratingCpt import MonoWithGratingCpt_nxschema


# Class simulating metadata of monochromator with grating component
class MetadataMonoWithGratingCpt:
    grating_substrate_material: str = "leadless"
    worldPosition: dict = {
        "x": "11.120000013",
        "y": "14.150000016",
        "z": "17.180000019",
    }
    description: str = "I am the best mono with grating cpt at the bessyii facility"
    baseline: str = "True"

    def get_attributes(self):
        attributes = {
            "grating_substrate_material": self.grating_substrate_material,
            "worldPosition": self.worldPosition,
            "description": self.description,
            "baseline": self.baseline,
        }
        return attributes


# Class simulating grating component of monochromator
class Grating(Device):
    diffraction_order: Signal = Cpt(Signal, name="diff_order")


# Class simulating monochromator with grating component
@NxSchemaLoader(MonoWithGratingCpt_nxschema)
class MonoWithGratingCpt(Device):
    grating: Grating = Cpt(Grating, name="grating")
    engry: SynAxis = Cpt(SynAxis, name="engry")
    slit: Signal = Cpt(Signal, name="slit")
    md = MetadataMonoWithGratingCpt()
