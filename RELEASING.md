# Releasing & maintenance

## One-time setup

1. **PyPI (Trusted Publishing, no token needed).**
   PyPI -> *Your account* -> *Publishing* -> **Add a new pending publisher**:
   - PyPI project name: `cambodia-geo`
   - Owner: `bsthen`, Repository: `cambodia-geo` (change if your repo name differs)
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
2. **GitHub.** Repo -> *Settings -> Environments -> New environment* named `pypi`
   (optionally add yourself as *required reviewer* for a manual approval before each publish).
3. Put the four CSV files in `src/cambodia_geo/data/` **with their original MEF names**:
   `CambodiaProvinceList2025.csv`, `CambodiaDistrictList2025.csv`,
   `CambodiaCommuneList2025.csv`, `CambodiaVillagesList2025.csv`.

   Expected columns: `province_code, province_kh, province_en` (districts also `province_code`;
   communes also `province_code, district_code`; villages also `province_code, district_code, commune_code`).
   Extra columns are ignored.

## Every release (code or data)

1. Edit `version` in `pyproject.toml` and add a section to `CHANGELOG.md`.
2. Commit and push to `main` (or merge a PR). The **Publish to PyPI** workflow then runs tests,
   builds, publishes, and creates the tag `v<version>` plus a GitHub Release.
   If the version was not changed, nothing is published.

## Yearly data refresh (the only routine task)

1. Download the new CSVs and replace the old files in `src/cambodia_geo/data/` (delete the old-year files).
2. Set `DATA_YEAR` in `src/cambodia_geo/_meta.py` (e.g. `2026`). The file names are built from it
   (`CambodiaProvinceList{DATA_YEAR}.csv`, ...), so the CSVs must be named accordingly.
3. Run `python -m pytest`. `tests/test_data_integrity.py` catches duplicate codes and orphaned rows.
   If `tests/test_api.py` fails because a code or name changed (e.g. a district was reorganised),
   update the examples in the tests, not the library.
4. Bump the **MINOR** version (e.g. `1.0.0` -> `1.1.0`), update `CHANGELOG.md`, push to `main`.

## Rules that keep users safe from breaking changes

- Never remove or rename anything in `cambodia_geo.__all__` or a record field without a MAJOR bump.
  `tests/test_public_api.py` fails if you do it by accident.
- New optional parameters must be keyword-only and have defaults; new record fields go at the end with defaults.
- Deprecate first (emit `DeprecationWarning`, document it in the changelog), remove only in the next MAJOR.
- Never re-upload a version to PyPI. Fix forward with a PATCH release (use "yank" on PyPI for bad releases).
- Security: Dependabot keeps GitHub Actions up to date. The package has no runtime dependencies.