from ophyd import Component as Cpt
from ophyd import Device, Signal
from ophyd.sim import SynAxis
from bluesky_nexus.common.decorator_utils import NxSchemaLoader
from .nx_schema.mono import Mono_nxschema


# Class simulating metadata of monochromator
class MetadataMono:
    grating_substrate_material: str = "lead"
    worldPosition: dict = {
        "x": "1.2000000000000003",
        "y": "4.5000000000000006",
        "z": "7.8000000000000009",
    }
    description: str = "I am the best mono at the bessyii facility"
    calibration_on: bool = True
    baseline: str = "True"
    transformations_axisname: str = "x"

    def get_attributes(self):
        attributes = {
            "grating_substrate_material": self.grating_substrate_material,
            "worldPosition": self.worldPosition,
            "description": self.description,
            "baseline": self.baseline,
            "calibration_on": self.calibration_on,
            "transformations_axisname": self.transformations_axisname,
        }
        return attributes


# Class simulating monochromator
@NxSchemaLoader(Mono_nxschema)
class Mono(Device):
    en: SynAxis = Cpt(SynAxis, name="en")
    grating: Signal = Cpt(Signal, name="grating")
    slit: Signal = Cpt(Signal, name="slit", kind="config")
    md = MetadataMono()
