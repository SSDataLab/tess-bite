import logging

__version__ = "0.1.0"

# Configure logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

from .core import RemoteTessImage
from .targetpixelfile import TargetPixelFile
from .bite import bite, bite_header, bite_ffi, bite_asteroid

__all__ = [
    "bite",
    "bite_header",
    "bite_ffi",
    "bite_asteroids",
    "RemoteTessImage",
    "TargetPixelFile",
]
