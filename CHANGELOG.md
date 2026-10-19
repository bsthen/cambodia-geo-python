# Changelog

All notable changes are documented here. The project follows [Semantic Versioning](https://semver.org/):
the **code/API** drives MAJOR.MINOR.PATCH, and every yearly data refresh is a **MINOR** release.
The dataset year is available at runtime as `cambodia_geo.DATA_YEAR`.

## [1.0.0] - 2026-10-19
### Added
- First stable release. Bundled MEF dataset: **2025**.
- `provinces()`, `districts()`, `communes()`, `villages()` list functions.
- `get_province()`, `get_district()`, `get_commune()`, `get_village()` single lookups.
- `search()` across all levels.
- Lookups accept codes, Khmer names or English names (case / space insensitive).
- Immutable, typed `Province`, `District`, `Commune`, `Village` records with `.to_dict()`.
- Zero runtime dependencies. Python 3.9+.
