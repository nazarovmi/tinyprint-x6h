import logging
from . import printer

__all__ = ["printer"]
__version__ = "0.1.0"

logging.getLogger("tinyprint_x6h").addHandler(logging.NullHandler())
