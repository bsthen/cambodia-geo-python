"""Sanity checks that every yearly CSV update must pass before release.

The CSVs are published by MEF and are bundled *unmodified*. The 2025 files contain a few
known upstream quirks, listed below. The tests allow exactly those, so any *new* problem in a
future dataset fails the build and gets reviewed by a human (update the lists consciously).
"""
from collections import Counter

import cambodia_geo as kh
from cambodia_geo.core import LEVELS, _index

# --- Known quirks in the MEF 2025 dataset (do not "fix" the CSVs; they must stay as published) ---
# Village codes that are shared by several villages inside the same commune (incl. the
# placeholder code "0506140-"). Unscoped get_village(code) returns None for these by design.
KNOWN_SHARED_VILLAGE_CODES = {
    "0506140-", "08120101", "08120301", "08120501",
    "12091101", "12091301", "12091701", "12091801",
}
# Communes that have villages but are missing from the commune list.
KNOWN_MISSING_COMMUNES = {("12", "1209", "120913")}


def test_every_level_has_rows():
    for level in LEVELS:
        assert _index().entries[level], f"no rows for {level}"


def test_codes_and_khmer_names_are_present():
    for level in LEVELS:
        for entry in _index().entries[level]:
            assert entry.record.code, level
            assert entry.record.name_kh, (level, entry.record.code)


def test_province_district_commune_codes_are_unique():
    for level in ("province", "district", "commune"):
        paths = [e.path for e in _index().entries[level]]
        assert len(paths) == len(set(paths)), f"duplicate {level} code(s)"


def test_village_code_collisions_are_only_the_known_ones():
    counts = Counter(e.path for e in _index().entries["village"])
    colliding = {e.record.code for e in _index().entries["village"] if counts[e.path] > 1}
    assert colliding <= KNOWN_SHARED_VILLAGE_CODES, sorted(colliding - KNOWN_SHARED_VILLAGE_CODES)


def test_no_exact_duplicate_villages():
    keys = [(e.path, e.record.name_kh) for e in _index().entries["village"]]
    assert len(keys) == len(set(keys))


def test_no_orphans():
    for d in _index().entries["district"]:
        assert kh.get_province(d.record.province_code), d.record
    for c in _index().entries["commune"]:
        r = c.record
        assert kh.get_district(r.district_code, province=r.province_code), r

    missing = set()
    for v in _index().entries["village"]:
        r = v.record
        if kh.get_commune(r.commune_code, district=r.district_code, province=r.province_code) is None:
            missing.add(v.path[:-1])
    assert missing <= KNOWN_MISSING_COMMUNES, sorted(missing - KNOWN_MISSING_COMMUNES)
