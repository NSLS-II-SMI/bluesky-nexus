# bluesky nexus

## Table of Contents
- [bluesky nexus](#bluesky-nexus)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Installation and usage](#installation-and-usage)
  - [Cheat sheet for maintenance purposes](#cheat-sheet-for-maintenance-purposes)
    - [Bluesky deployment](#bluesky-deployment)

<a name="Description"></a>
## Description

This project enables generation of a NeXus file from  a bluesky run. TODO


<a name="Installation and usage"></a>
## Installation and usage


1. Installation and usage in the context of bluesky container

TODO

2. Installation and usage outside the bluesky container

TODO

3. Units
 
Concerning the units:

If we know that the device returns the “units”, we put an empty string under the “units” in the schema so that the "units" provided by the device are used.
If we know that the device does not return the “units”, we enter the unit value that this particular device works with as the value of the “units” in the schema.





<a name="Cheat sheet for maintenance purposes"></a>
## Cheat sheet for maintenance purposes

### Bluesky deployment

Add to the "baseline.py" (at the top of the file)
```
from bluesky_nexus.preprocessors.supplemental_metadata import SupplementalMetadata
from bluesky_nexus.callbacks.nexus_writer import NexusWriter
from bluesky_nexus.bluesky_nexus_paths import (
    get_nx_file_dir_path,
    get_nx_schema_dir_path,
)  # This import is only applicable if our containerized applications are used

```

Add to the "baseline.py" (at the bottom of the file)

```
# ----------------- NEXUS -----------------
# Let the preprocessor append nexus metadata to the start document

nx_schema_dir_path: str = get_nx_schema_dir_path()
metadata = SupplementalMetadata(nx_schema_dir_path=nx_schema_dir_path)
metadata.devices_dictionary: dict = devices_dictionary
metadata.baseline = baseline
metadata.md_type = SupplementalMetadata.MetadataType.NEXUS_MD
RE.preprocessors.append(metadata)

# Let the preprocessor append devices metadata to the start document
metadata = (
    SupplementalMetadata()
)  # No need to pass "nx_schema_dir_path" in case of DEVICE_MD
metadata.devices_dictionary: dict = devices_dictionary
metadata.baseline = baseline
metadata.md_type = SupplementalMetadata.MetadataType.DEVICE_MD
RE.preprocessors.append(metadata)

# Subscribe the callback: 'NexusWriter'
nx_file_dir_path: str = get_nx_file_dir_path()
nexus_writer = NexusWriter(nx_file_dir_path=nx_file_dir_path)
RE.subscribe(nexus_writer)
# ----------------- End of NEXUS -----------------


```

Optionally define metadata dictionary which is going to be passed to the plan.
```
md = {
    "nx_file_name": "test_{uid}",  # Facultative
    "title": "fast test at HZB",  # Facultative
    "definition": "NXxas",  # Facultative
}
```

Examplary application
```
def my_plan():
    yield from scan(detectors, motor, 1, 10, 5, md=md)
```
The file "run_bluesky.sh" has to contain following volume mounts and environment variable setting:

```
-v ${NX_FILE_DIR_PATH}:${_NX_FILE_DIR_PATH} \
-v ${NX_SCHEMA_FILE_DIR_PATH}:${_NX_SCHEMA_FILE_DIR_PATH} \
```

```
--env _NX_FILE_DIR_PATH=${_NX_FILE_DIR_PATH} \
--env _NX_SCHEMA_FILE_DIR_PATH=${_NX_SCHEMA_FILE_DIR_PATH} \
```


The file ".bluesky_config" has to contain following definitions of env. variables:
```
export NX_FILE_DIR_PATH=~/bluesky/data/nexus
export _NX_FILE_DIR_PATH=/opt/bluesky/nx_file_dir_path
export NX_SCHEMA_FILE_DIR_PATH=~/bluesky/beamlinetools/beamlinetools/beamline_config/nx_schema
export _NX_SCHEMA_FILE_DIR_PATH=/opt/bluesky/nx_schema_file_dir_path
```
