"""
nx_models: A module defining and mapping various models used in the NeXus data format.

This module provides a collection of models representing different components in a scientific
experiment setup, including detectors, general configurations, and monochromators. These models
are part of the Bluesky Nexus framework for organizing metadata and experimental data.

Classes:
    - NXdetectorModel: Model for representing detector-related metadata and configuration.
    - NXgeneralModel: General model for grouping metadata and configuration.
    - NXmonochromatorModel: Model for managing monochromator-related metadata and configuration.

Mappings:
    - MODEL_NAME_TO_CLASS_MAPPING: A dictionary mapping model names to their corresponding model classes.
"""

from bluesky_nexus.models.nx_detector_model import NXdetectorModel
from bluesky_nexus.models.nx_general_model import NXgeneralModel
from bluesky_nexus.models.nx_monochromator_model import NXmonochromatorModel
from bluesky_nexus.models.nx_positioner_model import NXpositionerModel
from bluesky_nexus.models.nx_monitor_model import NXmonitorModel
from bluesky_nexus.models.nx_detector_group_model import NXdetector_groupModel

__all__ = ["MODEL_NAME_TO_CLASS_MAPPING"]

# Define a mapping between model name and model class name
MODEL_NAME_TO_CLASS_MAPPING = {
    "NXdetectorModel": NXdetectorModel,
    "NXgeneralModel": NXgeneralModel,
    "NXmonochromatorModel": NXmonochromatorModel,
    "NXpositionerModel": NXpositionerModel,
    "NXmonitorModel": NXmonitorModel,
    "NXdetector_groupModel": NXdetectorModel,
}
