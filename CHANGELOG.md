# Changelog

All notable changes are documented here. The project follows [Semantic Versioning](https://semver.org/):
the **code/API** drives MAJOR.MINOR.PATCH, and every yearly data refresh is a **MINOR** release.
The dataset year is available at runtime as `cambodia_geo.DATA_YEAR`.

## [1.0.1] - 2026-10-21
### Fixed
- Negative numbers, floats and booleans no longer match anything. `get_province(-1)` used to return province `01`
  because the minus sign was ignored, and `search(1.5)` searched for `15`. `search(None)` now returns `[]`.

### Added
- `NOTICE` with the attribution of the MEF data (also included in the wheel).
- `SPEC.md` and `spec/conformance.json`: the behaviour shared with the JavaScript (`cambodia-geo` on npm) and
  PHP (`bsthen/cambodia-geo` on Packagist) packages, with a test that runs it against this implementation.

## [1.0.0] - 2026-10-19
### Added
- First stable release. Bundled MEF dataset: **2025**.
- `provinces()`, `districts()`, `communes()`, `villages()` list functions.
- `get_province()`, `get_district()`, `get_commune()`, `get_village()` single lookups.
- `search()` across all levels.
- Lookups accept codes, Khmer names or English names (case / space insensitive).
- Immutable, typed `Province`, `District`, `Commune`, `Village` records with `.to_dict()`.
- Zero runtime dependencies. Python 3.9+.
