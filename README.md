# bluesky nexus

## Table of Contents

- [bluesky nexus](#bluesky-nexus)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Pydantic Schema and Model Capabilities](#pydantic-schema-and-model-capabilities)
    - [Example of Schema YAML file](#example-of-schema-yaml-file)
  - [Role of the Schema with the Model](#role-of-the-schema-with-the-model)
    - [Example of Model classes](#example-of-model-classes)
  - [Unit Definition Strategy](#unit-definition-strategy)
  - [Placeholder Mechanism](#placeholder-mechanism)
    - [Placeholder Syntax](#placeholder-syntax)
  - [Requirements for Device Classes](#requirements-for-device-classes)
    - [Example of custom device](#example-of-custom-device)
  - [Installation and usage in the context of bluesky container](#installation-and-usage-in-the-context-of-bluesky-container)
  - [NeXus logging setup](#nexus-logging-setup)
    - [Let the preprocessor append `nexus metadata` to the start document](#let-the-preprocessor-append-nexus-metadata-to-the-start-document)
    - [Let the preprocessor append `devices metadata` to the start document](#let-the-preprocessor-append-devices-metadata-to-the-start-document)
    - [Subscribe the callback: 'NexusWriter'](#subscribe-the-callback-nexuswriter)
  - [Installation and usage outside the bluesky container](#installation-and-usage-outside-the-bluesky-container)
    - [NeXus logging setup](#nexus-logging-setup-1)
    - [Let the preprocessor append ```nexus metadata``` to the start document](#let-the-preprocessor-append-nexus-metadata-to-the-start-document-1)
    - [Let the preprocessor append ```devices metadata``` to the start document](#let-the-preprocessor-append-devices-metadata-to-the-start-document-1)
    - [Subscribe the callback: NexusWriter](#subscribe-the-callback-nexuswriter-1)
  - [Cheat sheet for maintenance purposes in context of HZB bluesky deployment](#cheat-sheet-for-maintenance-purposes-in-context-of-hzb-bluesky-deployment)
  - [License](#license)

## Description

**bluesky_nexus** is a Python library designed to create NeXus files from a Bluesky run. The library generates NeXus files containing two primary groups:

- **NXinstrument Group**: Includes all instruments involved in the run, including baseline instruments.
- **NXcollection Group**: Contains the content of the `start` and `stop` documents generated during the run by the Bluesky Run Engine.

---

## Pydantic Schema and Model Capabilities

This library employs Pydantic schemas to allow for detailed mapping and customization, including:

1. **Component Selection and Mapping**:
   - Specify which components of a device class are mapped into the NeXus base class.
   - Define mappings between device class component names and NeXus field names (e.g., `en` → `energy`).

2. **Structural Mapping**:
   - Map device class component structures to NeXus base class structures (e.g., `mono.grating` → `mono.grating.diffraction_order`).

3. **Value Transformation**:
   - Apply conversion formulas to transform component values (e.g., eV to keV). 
     - The evaluation of the expression is executed in the restricted environment.

4. **NeXus Metadata**:
   - Define NeXus base class names (e.g. `NXmonochromator`, `NX_FLOAT`)
   - Define data types of component values mapped into nexus fields (e.g. `float64`, `int32`, `str`).
   - Specify the unit of component values (e.g., `rad`, `keV`).

5. **Data Fetching**:
   - Determine when component values should be fetched:
     - **Pre-run**: Based on static metadata or data read from the instrument available before the run
     - **Post-run**: Based on event documents available after the run.

### Example of Schema YAML file

```yaml
nx_model: NXmonochromatorModel
nxclass: NXmonochromator
energy:
  nxclass: NX_FLOAT
  value: $post-run:events:en
  dtype: float64
  attrs:
    units: "keV"
  transformation:
    expression: 3 * x**2 + np.exp(x+5) + 1.35 # Symbolic expression for the transformation
    target: value # Specifies the name of array to which expression is applied
grating:
  nxclass: NXgrating
  diffraction_order:
    nxclass: NX_INT
    value: $pre-run-cpt:grating
    dtype: int32
```

## Role of the Schema with the Model

The schema file specifies how data should be structured and which model should be applied. 
This connection is established through the nx_model field in the schema file. For example:

```yaml
nx_model: NXmonochromatorModel
nxclass: NXmonochromator
```

Here, the nx_model field (e.g., NXmonochromatorModel) explicitly defines the model responsible for handling the schema. This mapping ensures that the rules, transformations, and validations specified in the model are applied to the corresponding NeXus group or field. Moreover, the model allows for the inclusion of verbal descriptions of component roles, improving clarity.

### Example of Model classes

```python

class NXgratingModel(NXgroupModel):
    diffraction_order: NXfieldModelWithPrePostRunString = Field(
        None, description="Diffraction order value"
    )
    substrate_material: Optional[NXfieldModelWithPrePostRunString] = Field(
        None, description="Substrate material type"
    )

class NXmonochromatorModel(NXgroupModel):
    default: NXattrModelWithString = Field(
        NXattrModel(value="energy"), description="Default"
    )
    energy: NXfieldModelWithPrePostRunString = Field(None, description="Energy value")
    grating: NXgratingModel = Field(None, description="Grating")

```

---

## Unit Definition Strategy

The schema supports defining units for device components. The strategy for defining units in the schema YAML file is as follows:

1. **Device Provides Units**:  
   If the device natively returns units, set the `units` field in the schema to an empty string (`""`). This ensures that the units provided by the device are used directly.

2. **Device Does Not Provide Units**:  
   If the device does not return units, define the appropriate unit value in the `units` field of the schema. This ensures that the correct unit for that specific device is explicitly set.

## Placeholder Mechanism

The **bluesky_nexus** library uses placeholders to manage and organize data fetched during different phases of the run. These placeholders are incorporated into the `nexus_md` dictionary in the `start` document and are filled during the pre-run or post-run phases.

### Placeholder Syntax

1. **Pre-run Metadata**:  
   - Fetch metadata associated with a device instance.
   - Syntax: `$pre-run-md:<metadata_name>`  
   - Details:  
     - The separation between the prefix `$pre-run-md` and metadata name is made by applying the colon sign (`:`).  
     - The separation between items of the `<metadata_name>` is also made by applying the colon sign (`:`).  
     - **Examples**:  
       - `$pre-run-md:grating_substrate_material`  
       - `$pre-run-md:worldPosition:x`

2. **Pre-run Component Values**:  
   - Fetch values from components before the run.
   - Syntax: `$pre-run-cpt:<component_name>`  
   - Details:  
     - The separation between the prefix `$pre-run-cpt` and component name is made by applying the colon sign (`:`).  
     - The separation between items of the `<component_name>` is also made by applying the colon sign (`:`).  
     - **Examples**:  
       - `$pre-run-cpt:grat:diffraction_order`

3. **Post-run Component Values**:  
   - Fetch values from components after the run (event documents).
   - Syntax: `$post-run:events:<component_name>`  
   - Details:  
     - The separation between the prefix `$post-run:events` and component name is made by applying the colon sign (`:`).  
     - The separation between items of the `<component_name>` is made by applying the underscore sign (`_`) (as per the ophyd naming style).  
     - **Examples**:  
       - `$post-run:events:grating_diffraction_order`

---

## Requirements for Device Classes

All device classes used with this package must inherit from the `NXdevice` base class. The `NXdevice` class enforces the presence of a `nx_schema` attribute, which specifies the name of the pydantic schema yml file associated with the device. This requirement ensures that each device instance is correctly configured for NeXus data handling.
The definition of `NXdevice` class is located at: `bluesky_nexus/src/bluesky_nexus/bluesky_nexus_device_base.py`.

### Example of custom device

To define a custom device, create a class that inherits from `NXdevice` and specify the `nx_schema` attribute. This ensures that the device is correctly associated with its corresponding NeXus pydantic schema yml file.

```python
class Mono(NXdevice):
    en: SynAxis = Cpt(SynAxis, name="en")
    grating: Signal = Cpt(Signal, name="grating")
    slit: Signal = Cpt(Signal, name="slit")
    nx_schema = "nx_schema_mono"
```

---

## Installation and usage in the context of bluesky container

  Bluesky deployment

  Add to the "baseline.py" following imports:

  ```python
  from bluesky_nexus.preprocessors.supplemental_metadata import SupplementalMetadata
  from bluesky_nexus.callbacks.nexus_writer import NexusWriter
  from bluesky_nexus.common.logging_utils import setup_nx_logger, logging

  from bluesky_nexus.bluesky_nexus_paths import (
      get_nx_file_dir_path,
      get_nx_schema_dir_path,
      get_nx_log_file_dir_path,
  )  # This import is only applicable if HZB containerized application is used
  ```

At the bottom of baseline.py, add the following NeXus logging setup, preprocessor, and callback subscriptions:

## NeXus logging setup

This is an optional setting of the NeXus logger. If the setting is not defined, logging to a log file is deactivated.

```python
nx_log_file_dir_path: str = get_nx_log_file_dir_path()
setup_nx_logger(
    level=logging.DEBUG,
    log_file_dir_path=nx_log_file_dir_path,
    log_format=None,
    max_file_size=10 * 1024 * 1024,
    backup_count=5,
)
```

- Adjust the log level using `level` if necessary, e.g. logging.INFO, logging.WARNING
  - Default value: `level`=`logging.DEBUG`
- Adjust custom log format using `log_format` if necessary.
  - Default value defined in the body of the `setup_logger` function: `log_format` = `"%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s  %(message)s"`
- Adjust the maximum size of a log file in bytes before rotation occurs using `max_file_size` if necessary.
  - Default value: `max_file_size`=`10 * 1024 * 1024`
- "Adjust the number of backup log files to keep using `backup_count` if necessary."
  - Default value: `backup_count`=`5`

### Let the preprocessor append `nexus metadata` to the start document

  ```python
  nx_schema_dir_path: str = get_nx_schema_dir_path()
  metadata = SupplementalMetadata(nx_schema_dir_path=nx_schema_dir_path)
  metadata.devices_dictionary: dict = devices_dictionary
  metadata.baseline = baseline
  metadata.md_type = SupplementalMetadata.MetadataType.NEXUS_MD
  RE.preprocessors.append(metadata)
  ```

### Let the preprocessor append `devices metadata` to the start document

  ```python
  metadata = (
      SupplementalMetadata()
  )  # No need to pass "nx_schema_dir_path" in case of DEVICE_MD
  metadata.devices_dictionary: dict = devices_dictionary
  metadata.baseline = baseline
  metadata.md_type = SupplementalMetadata.MetadataType.DEVICE_MD
  RE.preprocessors.append(metadata)
  ```

### Subscribe the callback: 'NexusWriter'

  ```python
  nx_file_dir_path: str = get_nx_file_dir_path()
  nexus_writer = NexusWriter(nx_file_dir_path=nx_file_dir_path)
  RE.subscribe(nexus_writer)
  ```
  
  Optionally define metadata dictionary which is going to be passed to the plan.

  ```python
  md = {
      "nx_file_name": "test_{uid}",  # Facultative
      "title": "fast test at HZB",  # Facultative
      "definition": "NXxas",  # Facultative
      }
  ```

  ```python
  def my_plan():
    yield from scan(detectors, motor, 1, 10, 5, md=md)
  ```

## Installation and usage outside the bluesky container

- Clone the main branch of the project [bluesky_nexus](https://codebase.helmholtz.cloud/hzb/bluesky/core/source/bluesky_nexus)
- Create and activate an environemet with python_version >= "3.10"
- Install bluesky_nexus package in this environement.

  If you are working in a production environment use:

  ```bash
  cd "path to cloned `bluesky_nexus` package"
  pip install .
  ```

  If you are working in a development environment use:

  ```bash
  cd "path to cloned `bluesky_nexus` package"
  pip install -e .
  ```

  In your script use following imports:

  ```python
  from bluesky_nexus.preprocessors.supplemental_metadata import SupplementalMetadata
  from bluesky_nexus.callbacks.nexus_writer import NexusWriter
  from bluesky_nexus.common.logging_utils import setup_nx_logger, logging
  ```

Add the following NeXus logging setup, preprocessor, and callback subscriptions to your script:

### NeXus logging setup

```python
nx_log_file_dir_path: str = "Your path to the nexus log file directory"
setup_nx_logger(
    level=logging.DEBUG,
    log_file_dir_path=nx_log_file_dir_path,
    log_format=None,
    max_file_size=10 * 1024 * 1024,
    backup_count=5,
)
```

- Adjust the log level using `level` if necessary, e.g. logging.INFO, logging.WARNING
  - Default value: `level`=`logging.DEBUG`
- Adjust custom log format using `log_format` if necessary.
  - Default value defined in the body of the `setup_logger` function: `log_format` = `"%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s  %(message)s"`
- Adjust the maximum size of a log file in bytes before rotation occurs using `max_file_size` if necessary.
  - Default value: `max_file_size`=`10 * 1024 * 1024`
- "Adjust the number of backup log files to keep using `backup_count` if necessary."
  - Default value: `backup_count`=`5`

  In your script subscribe to the preprocessor and the callback:

### Let the preprocessor append ```nexus metadata``` to the start document

  ```python
  nx_schema_dir_path: str = "Your path to nx_schema directory"
  metadata = SupplementalMetadata(nx_schema_dir_path=nx_schema_dir_path)
  metadata.devices_dictionary: dict = devices_dictionary
  metadata.baseline = baseline
  metadata.md_type = SupplementalMetadata.MetadataType.NEXUS_MD
  RE.preprocessors.append(metadata)
  ```

### Let the preprocessor append ```devices metadata``` to the start document

  ```python
  metadata = (
      SupplementalMetadata()
  )  # No need to pass "nx_schema_dir_path" in case of DEVICE_MD
  metadata.devices_dictionary: dict = devices_dictionary
  metadata.baseline = baseline
  metadata.md_type = SupplementalMetadata.MetadataType.DEVICE_MD
  RE.preprocessors.append(metadata)
  ```

### Subscribe the callback: NexusWriter

  ```python
  nx_file_dir_path: str = "Your path to nx_file directory"
  nexus_writer = NexusWriter(nx_file_dir_path=nx_file_dir_path)
  RE.subscribe(nexus_writer)
  ```

  Optionally define metadata dictionary which is going to be passed to the plan.

  ```python
  md = {
      "nx_file_name": "test_{uid}",  # Facultative
      "title": "fast test at HZB",  # Facultative
      "definition": "NXxas",  # Facultative
      }
  ```

  ```python
  def my_plan():
    yield from scan(detectors, motor, 1, 10, 5, md=md)
  ```

## Cheat sheet for maintenance purposes in context of HZB bluesky deployment

  The file "run_bluesky.sh" has to contain following volume mounts and environment variable setting:

  ```bash
  -v ${NX_FILE_DIR_PATH}:${_NX_FILE_DIR_PATH} \
  -v ${NX_LOG_FILE_DIR_PATH}:${_NX_LOG_FILE_DIR_PATH} \
  -v ${NX_SCHEMA_DIR_PATH}:${_NX_SCHEMA_DIR_PATH} \
  ```

  ```bash
  --env _NX_FILE_DIR_PATH=${_NX_FILE_DIR_PATH} \
  --env _NX_LOG_FILE_DIR_PATH=${_NX_LOG_FILE_DIR_PATH} \
  --env _NX_SCHEMA_DIR_PATH=${_NX_SCHEMA_DIR_PATH} \
  ```

  The file ".bluesky_config" has to contain following definitions of env. variables:

  ```bash
  export NX_FILE_DIR_PATH=~/bluesky/data/nexus/file
  export _NX_FILE_DIR_PATH=/opt/bluesky/nx_file
  export NX_LOG_FILE_DIR_PATH=~/bluesky/data/nexus/log
  export _NX_LOG_FILE_DIR_PATH=/opt/bluesky/nx_log
  export NX_SCHEMA_DIR_PATH=~/bluesky/beamlinetools/beamlinetools/devices/nx_schema
  export _NX_SCHEMA_DIR_PATH=/opt/bluesky/nx_schema
  ```

## License

This project is licensed under the terms specified in the [License](./LICENSE) file.
