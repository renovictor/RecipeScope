# RecipeScope Release Checklist v1.0.0

- [ ] Confirm `version.py` values (`APP_NAME`, `VERSION`, `RELEASE_DATE`, metadata).
- [ ] Run tests: `python -m pytest -q`.
- [ ] Build executable: `build_release.bat`.
- [ ] Verify executable name from `get_executable_name()` equals `RecipeScope_v1.0.0.exe`.
- [ ] Launch EXE on clean Windows machine with mandatory modules available.
- [ ] Validate sample recipe load and waveform expansion.
- [ ] Validate project save/load round trip.
- [ ] Validate CSV/Excel/PNG/SVG/PDF exports.
- [ ] Confirm logs written to `%LOCALAPPDATA%\RecipeScope\logs\recipescope.log`.
- [ ] Archive release artifacts and checksums.
