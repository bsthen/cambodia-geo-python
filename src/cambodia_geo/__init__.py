"""cambodia-geo: Cambodia's provinces, districts, communes and villages.

    >>> import cambodia_geo as kh
    >>> kh.provinces()[0].name_en          # doctest: +SKIP
    >>> kh.districts("Siemreap")           # code, Khmer or English name       # doctest: +SKIP

Only the names listed in ``__all__`` are public API and follow semantic versioning.
"""
from importlib.metadata import PackageNotFoundError, version as _version

from ._meta import DATA_YEAR
from .core import (
    communes,
    districts,
    get_commune,
    get_district,
    get_province,
    get_village,
    provinces,
    search,
    villages,
)
from .models import Commune, District, Province, Village

try:
    __version__ = _version("cambodia-geo")
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "0+unknown"

__all__ = [
    "DATA_YEAR",
    "Commune",
    "District",
    "Province",
    "Village",
    "__version__",
    "communes",
    "districts",
    "get_commune",
    "get_district",
    "get_province",
    "get_village",
    "provinces",
    "search",
    "villages",
]
