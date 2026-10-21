"""Lookup engine (internal). Import everything from :mod:`cambodia_geo` instead."""
from __future__ import annotations

import csv
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any, Dict, List, Optional, Tuple, Union

from ._meta import DATA_YEAR
from .models import Commune, District, Province, Village

Record = Union[Province, District, Commune, Village]
Query = Union[str, int, Record]

LEVELS: Tuple[str, ...] = ("province", "district", "commune", "village")

_CLASSES: Dict[str, type] = {
    "province": Province,
    "district": District,
    "commune": Commune,
    "village": Village,
}
_FILES: Dict[str, str] = {
    "province": f"CambodiaProvinceList{DATA_YEAR}.csv",
    "district": f"CambodiaDistrictList{DATA_YEAR}.csv",
    "commune": f"CambodiaCommuneList{DATA_YEAR}.csv",
    "village": f"CambodiaVillagesList{DATA_YEAR}.csv",
}
# Columns (besides <level>_code / _kh / _en) that point at the ancestors.
_PARENT_FIELDS: Dict[str, Tuple[str, ...]] = {
    "province": (),
    "district": ("province_code",),
    "commune": ("province_code", "district_code"),
    "village": ("province_code", "district_code", "commune_code"),
}

_IGNORED_CHARS = {ord(c): None for c in "\u200b\u200c\u200d\u2060\ufeff-'\u2019.,"}


# --------------------------------------------------------------------------- #
# Normalisation
# --------------------------------------------------------------------------- #
def _norm(text: Any) -> str:
    """Case-, space- and punctuation-insensitive form used for name matching."""
    text = unicodedata.normalize("NFC", str(text))
    return "".join(text.split()).translate(_IGNORED_CHARS).casefold()


def _code_key(code: Any) -> str:
    """Canonical form of a code: '01', '1', ' 1 ' and '០១' all become '1'."""
    code = str(code).strip()
    if code.isdecimal() and len(code) <= 32:
        return str(int(code))
    return _norm(code)


def _query_text(query: Any) -> Optional[str]:
    """Text of a ``str`` or non-negative ``int`` query. ``None`` for anything else
    (floats, booleans, negative numbers, ``None``, ...), which matches nothing."""
    if isinstance(query, bool):
        return None
    if isinstance(query, str):
        return query.strip()
    if isinstance(query, int) and query >= 0:
        return str(query)
    return None


# --------------------------------------------------------------------------- #
# Loading & indexing
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Entry:
    record: Any
    path: Tuple[str, ...]  # canonical codes: ancestors..., own code
    code_key: str
    kh: str  # normalised Khmer name
    en: str  # normalised English name


@dataclass(frozen=True)
class _Index:
    entries: Dict[str, Tuple[_Entry, ...]]
    by_code: Dict[str, Dict[str, List[_Entry]]]
    by_name: Dict[str, Dict[str, List[_Entry]]]
    children: Dict[str, Dict[Tuple[str, ...], List[_Entry]]]


def _level_of(record: Any) -> str:
    for level in LEVELS:
        if isinstance(record, _CLASSES[level]):
            return level
    raise TypeError(f"not a cambodia_geo record: {type(record).__name__}")


def _path_of(record: Any) -> Tuple[str, ...]:
    level = _level_of(record)
    parents = tuple(_code_key(getattr(record, f)) for f in _PARENT_FIELDS[level])
    return parents + (_code_key(record.code),)


def _read_rows(level: str) -> List[Dict[str, str]]:
    name = _FILES[level]
    resource = resources.files(__package__).joinpath("data").joinpath(name)
    try:
        with resource.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise ValueError(f"cambodia_geo: data/{name} is empty")
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
            required = {f"{level}_code", f"{level}_kh", f"{level}_en", *_PARENT_FIELDS[level]}
            missing = required - set(reader.fieldnames)
            if missing:
                raise ValueError(
                    f"cambodia_geo: data/{name} is missing column(s): {', '.join(sorted(missing))}"
                )
            return list(reader)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"cambodia_geo: bundled data file not found: data/{name}") from exc


def _make_record(level: str, row: Dict[str, str]) -> Any:
    def cell(column: str) -> str:
        return (row.get(column) or "").strip()

    values = {
        "code": cell(f"{level}_code"),
        "name_kh": cell(f"{level}_kh"),
        "name_en": cell(f"{level}_en"),
    }
    for parent in _PARENT_FIELDS[level]:
        values[parent] = cell(parent)
    return _CLASSES[level](**values)


@lru_cache(maxsize=None)
def _index() -> _Index:
    entries: Dict[str, Tuple[_Entry, ...]] = {}
    by_code: Dict[str, Dict[str, List[_Entry]]] = {}
    by_name: Dict[str, Dict[str, List[_Entry]]] = {}
    children: Dict[str, Dict[Tuple[str, ...], List[_Entry]]] = {}

    for level in LEVELS:
        items: List[_Entry] = []
        codes: Dict[str, List[_Entry]] = {}
        names: Dict[str, List[_Entry]] = {}
        kids: Dict[Tuple[str, ...], List[_Entry]] = {}
        for row in _read_rows(level):
            record = _make_record(level, row)
            if not record.code:
                continue  # skip blank / malformed lines
            path = _path_of(record)
            entry = _Entry(record, path, path[-1], _norm(record.name_kh), _norm(record.name_en))
            items.append(entry)
            codes.setdefault(entry.code_key, []).append(entry)
            for name in {entry.kh, entry.en}:
                if name:
                    names.setdefault(name, []).append(entry)
            kids.setdefault(path[:-1], []).append(entry)
        entries[level] = tuple(items)
        by_code[level] = codes
        by_name[level] = names
        children[level] = kids

    return _Index(entries, by_code, by_name, children)


# --------------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------------- #
def _pool(level: str, scope: Any) -> List[_Entry]:
    """Entries of *level* that live somewhere below *scope*."""
    index = _index()
    scope_path = _path_of(scope)
    if LEVELS.index(_level_of(scope)) + 1 == LEVELS.index(level):
        return index.children[level].get(scope_path, [])
    n = len(scope_path)
    return [e for e in index.entries[level] if e.path[:n] == scope_path]


def _resolve(level: str, query: Any, scope: Any = None) -> Optional[Any]:
    """Find one record of *level* by code / Khmer name / English name.

    Without a *scope* a match must be unambiguous, otherwise ``None`` is returned.
    """
    if isinstance(query, _CLASSES[level]):
        return query
    text = _query_text(query)
    if text is None:
        return None
    name_key = _norm(text)
    if not name_key:
        return None
    code_key = _code_key(text)

    if scope is None:
        index = _index()
        for table, key in ((index.by_code[level], code_key), (index.by_name[level], name_key)):
            hits = table.get(key)
            if hits:
                return hits[0].record if len(hits) == 1 else None
        return None

    for entry in _pool(level, scope):
        if entry.code_key == code_key or entry.kh == name_key or entry.en == name_key:
            return entry.record
    return None


def _scope(province: Any = None, district: Any = None, commune: Any = None) -> Tuple[bool, Any]:
    """Resolve the given ancestors. Returns ``(ok, deepest_resolved_or_None)``."""
    scope = None
    for level, query in (("province", province), ("district", district), ("commune", commune)):
        if query is None:
            continue
        scope = _resolve(level, query, scope)
        if scope is None:
            return False, None
    return True, scope


def _children(level: str, parent: Any) -> List[Any]:
    entries = _index().children[level].get(_path_of(parent), [])
    return [e.record for e in entries]


# --------------------------------------------------------------------------- #
# Public functions (re-exported from the package root)
# --------------------------------------------------------------------------- #
def provinces() -> List[Province]:
    """All provinces."""
    return [e.record for e in _index().entries["province"]]


def districts(province: Query) -> List[District]:
    """Districts of a province. Returns ``[]`` if the province is not found."""
    p = _resolve("province", province)
    return [] if p is None else _children("district", p)


def communes(province: Query, district: Query) -> List[Commune]:
    """Communes of a district. Returns ``[]`` if a parent is not found."""
    p = _resolve("province", province)
    if p is None:
        return []
    d = _resolve("district", district, p)
    return [] if d is None else _children("commune", d)


def villages(province: Query, district: Query, commune: Query) -> List[Village]:
    """Villages of a commune. Returns ``[]`` if a parent is not found."""
    p = _resolve("province", province)
    if p is None:
        return []
    d = _resolve("district", district, p)
    if d is None:
        return []
    c = _resolve("commune", commune, d)
    return [] if c is None else _children("village", c)


def get_province(query: Query) -> Optional[Province]:
    """One province by code, Khmer name or English name; ``None`` if not found."""
    return _resolve("province", query)


def get_district(query: Query, *, province: Optional[Query] = None) -> Optional[District]:
    """One district; give *province* to disambiguate names. ``None`` if not found."""
    ok, scope = _scope(province)
    return _resolve("district", query, scope) if ok else None


def get_commune(
    query: Query, *, district: Optional[Query] = None, province: Optional[Query] = None
) -> Optional[Commune]:
    """One commune; give *district* / *province* to disambiguate names."""
    ok, scope = _scope(province, district)
    return _resolve("commune", query, scope) if ok else None


def get_village(
    query: Query,
    *,
    commune: Optional[Query] = None,
    district: Optional[Query] = None,
    province: Optional[Query] = None,
) -> Optional[Village]:
    """One village; give *commune* / *district* / *province* to disambiguate names."""
    ok, scope = _scope(province, district, commune)
    return _resolve("village", query, scope) if ok else None


def search(query: Query, *, level: Optional[str] = None, limit: Optional[int] = 50) -> List[Record]:
    """Search names (Khmer / English) and codes across levels.

    Results are ordered: exact matches, then prefix matches, then substring
    matches; ties are ordered province -> village, then by data order.
    *level* may be ``"province"``, ``"district"``, ``"commune"`` or ``"village"``.
    """
    if level is not None and level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS} or None, got {level!r}")
    if limit is not None and limit < 0:
        raise ValueError("limit must be >= 0 or None")
    text = _query_text(query)
    if text is None:
        return []
    name_key = _norm(text)
    if not name_key:
        return []
    code_key = _code_key(text)

    index = _index()
    scored: List[Tuple[int, int, int, Any]] = []
    for level_pos, lv in enumerate(LEVELS if level is None else (level,)):
        for pos, e in enumerate(index.entries[lv]):
            if e.code_key == code_key or name_key == e.kh or name_key == e.en:
                rank = 0
            elif e.kh.startswith(name_key) or e.en.startswith(name_key):
                rank = 1
            elif name_key in e.kh or name_key in e.en:
                rank = 2
            else:
                continue
            scored.append((rank, level_pos, pos, e.record))
    scored.sort(key=lambda t: t[:3])
    found = [t[3] for t in scored]
    return found if limit is None else found[:limit]
