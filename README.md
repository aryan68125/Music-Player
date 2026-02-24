# Music Player (PyQt + Python + Rust)

Cross-platform desktop music player with:
- PyQt6 frontend
- Python backend orchestration
- Rust acceleration for library scan/metadata/artwork operations

## Implemented Feature Scope

- Playback controls: play, pause, seek
- Queue controls: next, previous, shuffle, repeat one, repeat all
- Playback speed adjustment
- Album art display (Rust-first extraction, fallback path in UI layer)
- Metadata read/write/delete workflow (dialog -> controller -> Rust bridge)
- Favorites playlist behavior (backend)
- Playlist create/rename/delete/add/remove/reorder persistence (backend)

## Repository Layout

- `src/main.py` -> GUI entrypoint
- `src/app/front_end/` -> PyQt widgets and windows
- `src/app/back_end/` -> controllers, services, data layer, utils
- `rust_back_end/` -> Rust extension (`pyo3` + `maturin`)
- `tests/` -> backend, frontend, integration, and manual verification docs

## Setup

1. Create virtual environment:

```bash
python3 -m venv venv
```

2. Install Python dependencies:

```bash
venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -e .[dev]
```

3. Build/install Rust extension into the same venv:

```bash
venv/bin/python -m pip install maturin
venv/bin/python -m maturin develop --manifest-path rust_back_end/Cargo.toml
```

## Run the App

```bash
PYTHONPATH=src venv/bin/python src/main.py
```

In the app:
- Click `Add Songs`
- Pick local audio files
- Use the now-playing bar controls
- Use `Edit Metadata` from the toolbar on the current track

## Automated Verification

Run Python test suite:

```bash
venv/bin/python -m pytest -v
```

Run Rust test/build verification:

```bash
cargo test --manifest-path rust_back_end/Cargo.toml
```

Run Task 12 integration expectation:

```bash
venv/bin/python -m pytest tests/integration/test_end_to_end_playlist_reorder_and_playback_flow.py -v
```

## Manual Verification

Use:
- `tests/manual/manual_test_checklist.md`
