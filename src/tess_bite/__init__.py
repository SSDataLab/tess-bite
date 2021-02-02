import logging

__version__ = "0.1.0"

# Configure logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

from .core import RemoteTessImage
from .bite import bite

__all__ = [
    "RemoteTessImage",
    "bite",
]
