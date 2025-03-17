from ophyd import Component as Cpt
from ophyd import Device, Signal
from ophyd.sim import SynAxis


from bluesky_nexus.bluesky_nexus_device_base import NXdevice


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
class Mono(NXdevice):
    en: SynAxis = Cpt(SynAxis, name="en")
    grating: Signal = Cpt(Signal, name="grating")
    slit: Signal = Cpt(Signal, name="slit", kind="config")
    md = MetadataMono()
    nx_schema = "nx_schema_mono"


# Class simulating grating component of monochromator
class Grating(Device):
    diffraction_order: Signal = Cpt(Signal, name="diff_order")


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


# Class simulating monochromator with grating component
class MonoWithGratingCpt(NXdevice):
    grating: Grating = Cpt(Grating, name="grating")
    engry: SynAxis = Cpt(SynAxis, name="engry")
    slit: Signal = Cpt(Signal, name="slit")
    md = MetadataMonoWithGratingCpt()
    nx_schema = "nx_schema_mono_with_grating_cpt"
