"""StitchLab Agent Core - A powerful agent core application for AI development."""

__version__ = "0.1.0"
__author__ = "StitchLab Team"
__license__ = "MIT"

# Expose main modules
from . import config, schema

__all__ = [
    "config",
    "schema",
    "__version__",
    "__author__",
    "__license__",
]
