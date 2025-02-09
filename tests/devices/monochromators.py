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
    baseline: str = "True"

    def get_attributes(self):
        attributes = {
            "grating_substrate_material": self.grating_substrate_material,
            "worldPosition": self.worldPosition,
            "baseline": self.baseline,
        }
        return attributes


# Class simulating monochromator
class Mono(NXdevice):
    en: SynAxis = Cpt(SynAxis, name="en")
    grating: Signal = Cpt(Signal, name="grating")
    slit: Signal = Cpt(Signal, name="slit", kind = 'config')
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
    baseline: str = "True"

    def get_attributes(self):
        attributes = {
            "grating_substrate_material": self.grating_substrate_material,
            "worldPosition": self.worldPosition,
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


class MetadataMonoWithStrCpt:
    grating_substrate_material: str = "leadless"
    worldPosition: dict = {
        "x": "20.210000022",
        "y": "23.240000025",
        "z": "26.270000028",
    }
    baseline: str = "True"

    def get_attributes(self):
        attributes = {
            "grating_substrate_material": self.grating_substrate_material,
            "worldPosition": self.worldPosition,
            "baseline": self.baseline,
        }
        return attributes


class StringSignal(Signal):
    """A Signal that holds string values instead of numeric ones."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._readback = "default_value"  # Set an initial string value

    def get(self):
        """Override get method to return the string value."""
        return self._readback

    def put(self, value):
        """Override put method to store a string value."""
        if not isinstance(value, str):
            raise ValueError("Only string values are allowed for slit.")
        self._readback = value
        self._run_subs(sub_type=self.SUB_VALUE, old_value=self._readback, value=value)


class MonoWithStrCpt(NXdevice):
    en: SynAxis = Cpt(SynAxis, name="en")
    grating: Signal = Cpt(Signal, name="grating")
    slit: StringSignal = Cpt(StringSignal, name="slit", kind = 'config')
    md = MetadataMonoWithStrCpt()
    nx_schema = "nx_schema_mono_with_str_cpt"
