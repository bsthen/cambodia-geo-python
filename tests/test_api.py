import dataclasses

import pytest

import cambodia_geo as kh


def test_provinces_are_returned():
    result = kh.provinces()
    assert result and all(isinstance(p, kh.Province) for p in result)


def test_province_lookup_accepts_code_khmer_english_and_int():
    by_code = kh.get_province("17")
    assert by_code is not None
    assert kh.get_province(17) == by_code
    assert kh.get_province("សៀមរាប") == by_code
    assert kh.get_province("Siemreap") == by_code
    assert kh.get_province("  SIEM reap ") == by_code


def test_unknown_and_empty_queries():
    assert kh.get_province("does-not-exist") is None
    assert kh.get_province("") is None
    assert kh.get_province("   ") is None
    assert kh.get_province(None) is None  # type: ignore[arg-type]
    assert kh.districts("does-not-exist") == []
    assert kh.communes("17", "does-not-exist") == []
    assert kh.villages("17", "1702", "does-not-exist") == []


def test_hierarchy_with_mixed_query_styles():
    districts = kh.districts("Siemreap")
    assert "1702" in {d.code for d in districts}

    communes = kh.communes("17", "Angkor Thum")
    assert "170201" in {c.code for c in communes}
    assert kh.communes("សៀមរាប", "1702") == communes

    villages = kh.villages("17", "1702", "ជប់តាត្រាវ")
    assert villages
    assert all(v.commune_code == "170201" for v in villages)
    assert kh.villages("Siemreap", "Angkor Thum", "170201") == villages


def test_record_objects_can_be_passed_back_in():
    province = kh.get_province("17")
    district = kh.get_district("1702")
    commune = kh.communes(province, district)[0]
    assert kh.villages(province, district, commune) == kh.villages(
        province.code, district.code, commune.code
    )


def test_get_district_scoped_and_unscoped():
    d = kh.get_district("1702")
    assert d is not None and d.province_code == "17"
    assert kh.get_district("Angkor Thum", province="Siemreap") == d
    assert kh.get_district("1702", province="does-not-exist") is None


def test_get_commune_and_village():
    c = kh.get_commune("170201")
    assert c is not None and c.district_code == "1702"
    assert kh.get_commune("ជប់តាត្រាវ", district="Angkor Thum", province="17") == c
    assert kh.get_commune("ជប់តាត្រាវ", province="17") == c  # skipping a level is fine

    v = kh.villages("17", "1702", "170201")[0]
    assert kh.get_village(v.code) == v
    assert kh.get_village(v.name_kh, commune="170201", district="1702", province="17") == v


def test_code_padding_is_forgiving():
    assert kh.get_province("017") == kh.get_province("17")
    assert kh.get_province("១៧") == kh.get_province("17")  # Khmer digits


def test_search_orders_exact_matches_first_and_respects_limits():
    hits = kh.search("Siemreap")
    assert hits and hits[0] == kh.get_province("17")
    assert kh.search("Siemreap", limit=1) == hits[:1]
    assert kh.search("Siemreap", limit=0) == []
    assert kh.search("") == []
    assert all(isinstance(r, kh.Province) for r in kh.search("Siemreap", level="province"))
    with pytest.raises(ValueError):
        kh.search("x", level="country")
    with pytest.raises(ValueError):
        kh.search("x", limit=-1)


def test_results_are_independent_copies():
    first = kh.provinces()
    first.clear()
    assert kh.provinces()


def test_records_are_immutable_and_serialisable():
    p = kh.get_province("17")
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.code = "00"  # type: ignore[misc]
    assert p.to_dict() == {"code": p.code, "name_kh": p.name_kh, "name_en": p.name_en}
    hash(p)  # usable in sets / dict keys


def test_metadata():
    assert isinstance(kh.DATA_YEAR, int)
    assert isinstance(kh.__version__, str)
