"""Immutable record types returned by :mod:`cambodia_geo`.

Stability promise: fields may be *added* in minor releases (always at the end,
with defaults), but are never renamed, removed or re-typed within a major version.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict


class _Record:
    def to_dict(self) -> Dict[str, str]:
        """Return the record as a plain ``dict`` (JSON-serialisable)."""
        return asdict(self)  # type: ignore[call-overload]


@dataclass(frozen=True)
class Province(_Record):
    """ខេត្ត / រាជធានី"""

    code: str
    name_kh: str
    name_en: str


@dataclass(frozen=True)
class District(_Record):
    """ស្រុក / ខណ្ឌ / ក្រុង"""

    code: str
    name_kh: str
    name_en: str
    province_code: str


@dataclass(frozen=True)
class Commune(_Record):
    """ឃុំ / សង្កាត់"""

    code: str
    name_kh: str
    name_en: str
    province_code: str
    district_code: str


@dataclass(frozen=True)
class Village(_Record):
    """ភូមិ"""

    code: str
    name_kh: str
    name_en: str
    province_code: str
    district_code: str
    commune_code: str
