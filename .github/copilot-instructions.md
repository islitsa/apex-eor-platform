<!-- Copilot / AI agent instructions for the APEX EOR platform -->

This file gives concise, repository-specific guidance to automated coding agents (Copilot-style) so they can be immediately productive.

High-level architecture (quick):
- Core package: `src/apex` — small modular subpackages: `attribution`, `hypothesis`, `knowledge`, `linear_inflow`, `validation`.
- CLI / entrypoints: `setup.py` registers a console script `apex=apex.cli:main` (implementations live under `src/apex`).
- Data pipeline: raw downloads live in `data/raw/*`, processing code is under `src/apex/data_collection` and `scripts/` (example: `scripts/download_rrc_data.py`).

Important conventions and patterns:
- Single-responsibility modules: each subpackage focuses on a domain (e.g., `linear_inflow` implements `LinearInflowAnalyzer` exported from `src/apex/__init__.py`). Prefer adding functions/classes into the correct subpackage rather than creating cross-cutting modules.
- Minimal side-effects on import: modules are expected to be import-safe (use `if __name__ == '__main__'` for scripts). Follow `scripts/download_rrc_data.py` as the canonical script pattern.
- Data layout: raw -> interim -> processed under `data/`. Code should read from `data/raw` and write intermediate products into `data/interim` or `data/processed`.

Developer workflows (explicit commands and checks):
- Install: `pip install -r requirements.txt` (project uses setup.py with packages under `src/`).
- Run downloader example: `python scripts/download_rrc_data.py --list` or `python scripts/download_rrc_data.py --datasets production --extract`.
- Tests: check the `tests/` folder. Run tests using your preferred runner (`pytest`) from repo root: `pytest -q`.

Integration points & external dependencies:
- External data sources (network calls) are common: RRC, FracFocus, USGS. Code that downloads should handle network failures and avoid running during unit tests (mock requests or use vcr/fixtures).
- Persistent state lives under `data/` — avoid committing large files. Use metadata files (see downloader `metadata/` usage) when adding new downloaders.

Code style & PR hints for automated edits:
- Keep changes localized to a subpackage. Update `src/apex/__init__.py` exports when adding a top-level component class.
- Follow existing logging setup (module-level logger using `logging.getLogger(__name__)`); prefer `logger.info/debug/error` over prints in non-script modules.
- For scripts in `scripts/`, keep CLI parsing with `argparse` and a `main()` function guarded by `if __name__ == '__main__'`.

Examples from this repo to emulate:
- Downloader pattern: `scripts/download_rrc_data.py` — use `RRCRawDownloader.download_dataset()`, `save_metadata()` and `extract_if_zipped()` patterns for new data sources.
- Package exports: `src/apex/__init__.py` exposes `AttributionEngine`, `MultiAgentValidator`, `HypothesisGenerator`, `LinearInflowAnalyzer` — keep this file in sync when adding public classes.

Quick checklist for changes an AI assistant might make:
1. Add new analyzer: create `src/apex/<name>/...`, implement class, add import/export in `src/apex/__init__.py`, add tests under `tests/`.
2. Add data downloader: mirror `scripts/download_rrc_data.py`, write metadata to `data/raw/<provider>/metadata/`, add README note in `data/README` or `docs/`.
3. Fix network flakiness in tests: mock `requests.get` and verify metadata writing only when the file is fully downloaded.

When you're unsure:
- Prefer small, reversible PRs that modify a single package and include tests. Don't alter `data/` content in commits unless updating small metadata files.
- If adding long-running jobs or external credentials, add configuration to `.env` and document expected env vars in `README.md`.

If you need more repository orientation, open `README.md`, `setup.py`, and `scripts/download_rrc_data.py` first.

-- End of instructions --
