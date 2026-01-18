
__version__ = '1.0.0'
__author__ = 'ALPR Development Team'
__title__ = 'Nigerian ALPR System'

from .main import run_alpr, get_result_summary
from . import detector
from . import ocr
from . import plate_color
from . import vehicle_db
from . import utils

__all__ = [
    'run_alpr',
    'get_result_summary',
    'detector',
    'ocr',
    'plate_color',
    'vehicle_db',
    'utils'
]
