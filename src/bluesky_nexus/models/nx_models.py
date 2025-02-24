"""
Module: nexusformat_models_hzb.py

"""

from bluesky_nexus.models.nx_general_model import NXgeneralModel
from bluesky_nexus.models.nx_monochromator_model import NXmonochromatorModel

__all__ = ["MODEL_NAME_TO_CLASS_MAPPING"]

# Define a mapping between model name and model class name
MODEL_NAME_TO_CLASS_MAPPING = {
    "NXgeneralModel": NXgeneralModel,
    "NXmonochromatorModel": NXmonochromatorModel,
}
