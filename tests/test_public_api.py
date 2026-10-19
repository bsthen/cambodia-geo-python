"""Guards against accidental breaking changes.

If one of these tests fails, you are changing the public API. Removing or
renaming anything here requires a MAJOR version bump (see README: Stability).
Adding new names is fine: extend the expected sets below in the same commit.
"""
import dataclasses
import inspect

import cambodia_geo as kh

EXPECTED_NAMES = {
    "DATA_YEAR", "Commune", "District", "Province", "Village", "__version__",
    "communes", "districts", "get_commune", "get_district", "get_province",
    "get_village", "provinces", "search", "villages",
}

EXPECTED_FIELDS = {
    "Province": ["code", "name_kh", "name_en"],
    "District": ["code", "name_kh", "name_en", "province_code"],
    "Commune": ["code", "name_kh", "name_en", "province_code", "district_code"],
    "Village": ["code", "name_kh", "name_en", "province_code", "district_code", "commune_code"],
}

EXPECTED_SIGNATURES = {
    "provinces": "()",
    "districts": "(province)",
    "communes": "(province, district)",
    "villages": "(province, district, commune)",
    "get_province": "(query)",
    "get_district": "(query, *, province=None)",
    "get_commune": "(query, *, district=None, province=None)",
    "get_village": "(query, *, commune=None, district=None, province=None)",
    "search": "(query, *, level=None, limit=50)",
}


def test_exported_names_are_not_removed():
    assert EXPECTED_NAMES <= set(kh.__all__)
    for name in kh.__all__:
        assert hasattr(kh, name)


def test_record_fields_are_not_removed_or_reordered():
    for cls_name, expected in EXPECTED_FIELDS.items():
        actual = [f.name for f in dataclasses.fields(getattr(kh, cls_name))]
        assert actual[: len(expected)] == expected, cls_name


def test_function_signatures_are_stable():
    import re

    for name, expected in EXPECTED_SIGNATURES.items():
        sig = str(inspect.signature(getattr(kh, name)))
        # drop annotations, keep names / defaults / keyword-only markers
        sig = re.sub(r":\s*[^,=)]+(\[[^\]]*\])?", "", sig)
        sig = re.sub(r"\s*->.*$", "", sig)
        assert sig.replace(" ", "") == expected.replace(" ", ""), name
