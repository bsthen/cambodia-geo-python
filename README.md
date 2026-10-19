# cambodia-geo

Lightweight, **zero-dependency** Python library for Cambodia's administrative divisions:
**provinces (ខេត្ត), districts (ស្រុក/ខណ្ឌ), communes (ឃុំ/សង្កាត់) and villages (ភូមិ)**.
Look things up by **code**, **Khmer name** or **English name**, in any mix.

Data source: [data.mef.gov.kh](https://data.mef.gov.kh) (bundled dataset year: see `cambodia_geo.DATA_YEAR`).

```bash
pip install cambodia-geo
```

Python 3.9+. No runtime dependencies. Data is bundled and loaded lazily on first use.

## Quick start

```python
import cambodia_geo as kh

kh.provinces()                                 # all provinces
kh.districts("Siemreap")                       # districts of a province
kh.communes("17", "Angkor Thum")               # communes of a district
kh.villages("សៀមរាប", 1702, "ជប់តាត្រាវ")        # villages of a commune

p = kh.get_province("សៀមរាប")                   # Province(code='17', name_kh=..., name_en=...)
p.code, p.name_kh, p.name_en
p.to_dict()                                    # plain dict, ready for JSON

kh.get_district("Angkor Thum", province="Siemreap")
kh.get_commune("170201")
kh.search("angkor")                            # across all levels, best matches first
```

Records can be passed straight back in:

```python
for province in kh.provinces():
    for district in kh.districts(province):
        ...
```

## API

| Function | Returns | Not found |
|---|---|---|
| `provinces()` | `list[Province]` | - |
| `districts(province)` | `list[District]` | `[]` |
| `communes(province, district)` | `list[Commune]` | `[]` |
| `villages(province, district, commune)` | `list[Village]` | `[]` |
| `get_province(query)` | `Province` | `None` |
| `get_district(query, *, province=None)` | `District` | `None` |
| `get_commune(query, *, district=None, province=None)` | `Commune` | `None` |
| `get_village(query, *, commune=None, district=None, province=None)` | `Village` | `None` |
| `search(query, *, level=None, limit=50)` | `list[Province \| District \| Commune \| Village]` | `[]` |

Also: `DATA_YEAR` (int) and `__version__` (str).

Records are frozen dataclasses (hashable, typed, `py.typed` included):

| Type | Fields |
|---|---|
| `Province` | `code, name_kh, name_en` |
| `District` | `code, name_kh, name_en, province_code` |
| `Commune` | `code, name_kh, name_en, province_code, district_code` |
| `Village` | `code, name_kh, name_en, province_code, district_code, commune_code` |

### Matching rules

- A *query* is a code (`"17"`, `17`, `"017"` and Khmer digits `"១៧"` are equal), a Khmer name or an English name.
- Names ignore case, spaces and `- ' . ,` : `"Siem Reap"` == `"siemreap"`.
- With a parent (`province=`, `district=`, ...) the first match inside it is returned.
- **Without** a parent, a name must be unambiguous; if several places share the name, `None` is returned
  instead of guessing. Codes are always safe to use alone.

## Data notes

The bundled MEF files are shipped exactly as published. The 2025 dataset contains a few upstream quirks:

- Some village codes are shared by several villages of the same commune (e.g. `08120101`, and the placeholder `0506140-`).
  Listing functions return all of them; `get_village(code)` without a parent returns `None` for these codes
  instead of guessing, and a scoped `get_village(name, commune=...)` returns the first match.
- Commune `120913` (Phnom Penh, district `1209`) has villages but is missing from the commune list, so
  `villages("12", "1209", "120913")` returns `[]`.

## Stability (no surprise breaking changes)

- [Semantic Versioning](https://semver.org/). Only names in `cambodia_geo.__all__` are public.
- Within a major version, functions, parameters and record fields are never removed or renamed;
  new options are keyword-only with defaults, new record fields are appended.
- Removals are announced with a `DeprecationWarning` and a changelog entry first.
- **Data updates** (once a year) ship as a MINOR release. Government reorganisations can change
  codes or names between years; pin the version (`cambodia-geo~=1.0`) if you store codes long-term,
  and check `DATA_YEAR`.

## Data & licence

The code is MIT licensed. The bundled data comes from the Ministry of Economy and Finance
([data.mef.gov.kh](https://data.mef.gov.kh), [terms of use](https://data.mef.gov.kh/terms-of-use)) and remains subject to its terms.

## ភាសាខ្មែរ (សង្ខេប)

បណ្ណាល័យ Python ស្រាល គ្មាន dependency សម្រាប់ស្វែងរក ខេត្ត ស្រុក ឃុំ ភូមិ នៃកម្ពុជា តាមលេខកូដ ឈ្មោះខ្មែរ ឬឈ្មោះអង់គ្លេស។
ដំឡើងដោយ `pip install cambodia-geo` ហើយប្រើ `import cambodia_geo as kh`។ ទិន្នន័យអាប់ដេតរៀងរាល់ឆ្នាំ (មើល `kh.DATA_YEAR`)។

## Contributing

`pip install -e ".[dev]"` then `pytest`. See [RELEASING.md](RELEASING.md).
