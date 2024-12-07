from bluesky import RunEngine
from bluesky.plans import scan
from devices.monochromators import Mono, MonoWithGratingCpt
from ophyd.sim import motor
from preprocessors.baseline import SupplementalDataBaseline

from bluesky_nexus.callbacks.nexus_writer import NexusWriter
from bluesky_nexus.preprocessors.supplemental_metadata import SupplementalMetadata

# Define RE
RE = RunEngine()

# Instantiate monochromator: 'mono'
mono = Mono(name="mono")

# Instantiate monochromator: 'MonoWithGratingCpt'
mono_with_grating_cpt = MonoWithGratingCpt(name="mono_with_grating_cpt")

# Assemble all instantiated devices in a dict: "devices_dictionary"
# as it is made at the beamline
devices_dictionary = {"mono": mono, "mono_with_grating_cpt": mono_with_grating_cpt}

# Create a list of baseline devices, i.e. devices to be read before and after run.
baseline: list = []
for device in devices_dictionary.values():
    try:
        if device.md.get_attributes()["baseline"] == "True":
            baseline.append(device)
    except KeyError:
        pass

# Create baseline preprocessor
sdd = SupplementalDataBaseline(baseline=baseline)

# Append baseline preprocessor to the run engine
RE.preprocessors.append(sdd)

# Let the preprocessor append nexus metadata to the start document
metadata = SupplementalMetadata()
metadata.devices_dictionary = devices_dictionary
metadata.baseline = baseline
metadata.md_type = SupplementalMetadata.MetadataType.NEXUS_MD
RE.preprocessors.append(metadata)

# Let the preprocessor append devices metadata to the start document
metadata = SupplementalMetadata()
metadata.devices_dictionary = devices_dictionary
metadata.baseline = baseline
metadata.md_type = SupplementalMetadata.MetadataType.DEVICE_MD
RE.preprocessors.append(metadata)

# Subscribe the callback: 'NexusWriter'
RE.subscribe(NexusWriter())
# ----------------- End of NEXUS -----------------

# Define detectors applied in the  plan
mono = devices_dictionary["mono"]
detectors = [mono.en]


def test_execute_plan():
    # Define a metadata dict which is going to be passed to the plan
    # Define at least values for the keys 'nx_file_dir_path' and 'nx_file_name'
    md = {
        "nx_file_name": "test_77",  # Facultative
        "title": "test at HZB",  # Facultative
        "definition": "NXxas",  # Facultative
        "test_dict": {"a": 1, "b": 2, "c": {"d": 3, "e": 4}},
    }

    # Define a plan
    def my_plan():
        yield from scan(detectors, motor, 1, 10, 5, md=md)

    # Run engine on the plan
    RE(my_plan())

    print("END OF RUN")
