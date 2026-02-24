# Music Player V1 (PyQt + Python + Rust) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a cross-platform desktop music player with PyQt UI, Python orchestration, and Rust-accelerated metadata/library operations.

**Architecture:** PyQt6 handles all UI and user interaction. Python controls application flow, state, and database access. Rust (via `pyo3`/`maturin`) provides high-performance library scanning and metadata/artwork operations.

**Tech Stack:** Python 3.12+, PyQt6, Pydantic v2, SQLite, Pytest, Rust, pyo3, maturin, lofty (Rust tag parsing), image crate.

---

## Delivery Model (Required by User)

- Implement one feature at a time.
- For each feature:
  1. Explain feature scope and implementation approach.
  2. Ask for explicit approval.
  3. Implement with TDD (`RED -> GREEN -> REFACTOR`).
  4. Run automated tests and show evidence.
  5. Run manual verification checklist.
  6. Report results and ask permission for next feature.

## Virtual Environment Policy (Required by User)

- Create environment with: `python3 -m venv venv`
- Install Python dependencies only through this environment.
- Run all Python commands through: `venv/bin/python`
- Preferred install commands:
  - `venv/bin/python -m pip install --upgrade pip`
  - `venv/bin/python -m pip install -e .[dev]`

---

### Task 1: Scaffold Project Layout and Tooling

**Files:**
- Create: `pyproject.toml`
- Create: `src/main.py`
- Create: `src/app/__init__.py`
- Create: `src/app/front_end/__init__.py`
- Create: `src/app/back_end/__init__.py`
- Create: `src/app/back_end/controllers/__init__.py`
- Create: `src/app/back_end/services/__init__.py`
- Create: `src/app/back_end/data/__init__.py`
- Create: `src/app/back_end/data/database_handler/__init__.py`
- Create: `src/app/back_end/data/repositories/__init__.py`
- Create: `src/app/back_end/utils/__init__.py`
- Create: `rust_back_end/Cargo.toml`
- Create: `rust_back_end/src/lib.rs`
- Create: `tests/conftest.py`
- Create: `tests/test_project_structure.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_required_directories_exist():
    required = [
        "src/app/front_end",
        "src/app/back_end/controllers",
        "src/app/back_end/services",
        "src/app/back_end/data/database_handler",
        "src/app/back_end/data/repositories",
        "src/app/back_end/utils",
        "rust_back_end/src",
    ]
    for rel in required:
        assert Path(rel).exists(), rel
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/test_project_structure.py::test_required_directories_exist -v`
Expected: FAIL with missing path assertions.

**Step 3: Write minimal implementation**

Create the folders/files listed above and minimal Python/Rust package stubs.
Create virtualenv and install dependencies:

```bash
python3 -m venv venv
venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -e .[dev]
```

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/test_project_structure.py::test_required_directories_exist -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml src rust_back_end tests
git commit -m "chore: scaffold pyqt python rust project structure"
```

---

### Task 2: Add Global Message Enums and Typed Response Models

**Files:**
- Create: `src/app/back_end/utils/success_messages.py`
- Create: `src/app/back_end/utils/error_messages.py`
- Create: `src/app/back_end/utils/class_method_request_models.py`
- Create: `src/app/back_end/utils/class_method_response_models.py`
- Create: `tests/back_end/utils/test_response_models.py`

**Step 1: Write the failing test**

```python
from app.back_end.utils.class_method_response_models import SuccessResponse, ErrorResponse
from app.back_end.utils.success_messages import SuccessMessage
from app.back_end.utils.error_messages import ErrorMessage


def test_success_response_has_expected_shape():
    response = SuccessResponse[dict](message=SuccessMessage.GENERAL_SUCCESS, data={"id": 1})
    assert response.status is True
    assert response.data == {"id": 1}


def test_error_response_has_expected_shape():
    response = ErrorResponse(message=ErrorMessage.UNKNOWN_ERROR)
    assert response.status is False
    assert response.data is None
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/utils/test_response_models.py -v`
Expected: FAIL with import/model missing errors.

**Step 3: Write minimal implementation**

Define:
- `SuccessMessage(Enum)`
- `ErrorMessage(Enum)`
- `BaseModel` request types in `class_method_request_models.py`
- `SuccessResponse[T]`, `ErrorResponse`, `MethodResponse[T]` in `class_method_response_models.py`

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/utils/test_response_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/back_end/utils tests/back_end/utils
git commit -m "feat: add global message enums and typed method response models"
```

---

### Task 3: Rust Bridge Baseline (Python <-> Rust Integration)

**Files:**
- Create: `src/app/back_end/services/rust_bridge.py`
- Modify: `rust_back_end/Cargo.toml`
- Modify: `rust_back_end/src/lib.rs`
- Create: `tests/back_end/services/test_rust_bridge.py`

**Step 1: Write the failing test**

```python
from app.back_end.services.rust_bridge import get_rust_backend_version


def test_rust_bridge_returns_version_string():
    version = get_rust_backend_version()
    assert isinstance(version, str)
    assert version
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/services/test_rust_bridge.py -v`
Expected: FAIL (module/function missing).

**Step 3: Write minimal implementation**

Expose Rust function `backend_version()` through `pyo3` and call it from Python bridge.

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/services/test_rust_bridge.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/back_end/services/rust_bridge.py rust_back_end tests/back_end/services
git commit -m "feat: add rust bridge with pyo3 baseline function"
```

---

### Task 4: Database Handler and Repository Foundation

**Files:**
- Create: `src/app/back_end/data/database_handler/database.py`
- Create: `src/app/back_end/data/repositories/repository.py`
- Create: `tests/back_end/data/test_database_schema.py`

**Step 1: Write the failing test**

```python
from app.back_end.data.database_handler.database import DatabaseHandler


def test_schema_tables_exist(tmp_path):
    db = DatabaseHandler(db_path=tmp_path / "app.db")
    db.initialize_schema()
    assert db.table_exists("tracks")
    assert db.table_exists("playlists")
    assert db.table_exists("playlist_tracks")
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/data/test_database_schema.py -v`
Expected: FAIL due to missing class/schema.

**Step 3: Write minimal implementation**

Implement database initialization with required tables and helper methods.

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/data/test_database_schema.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/back_end/data tests/back_end/data
git commit -m "feat: add sqlite database handler and base repository"
```

---

### Task 5: Feature 1 - Playback Core (Play/Pause/Seek/Speed)

**Files:**
- Create: `src/app/back_end/services/playback_service.py`
- Create: `tests/back_end/services/test_playback_service.py`

**Step 1: Write the failing test**

```python
def test_playback_speed_valid_range(playback_service):
    result = playback_service.set_playback_speed(1.25)
    assert result.status is True
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/services/test_playback_service.py -v`
Expected: FAIL due to missing playback methods.

**Step 3: Write minimal implementation**

Implement:
- `play()`
- `pause()`
- `seek(position_ms)`
- `set_playback_speed(rate)`

Return typed `MethodResponse`.

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/services/test_playback_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/back_end/services/playback_service.py tests/back_end/services/test_playback_service.py
git commit -m "feat: implement playback core with seek and speed control"
```

---

### Task 6: Feature 2 - Queue Modes (Next/Previous/Shuffle/Repeat)

**Files:**
- Create: `src/app/back_end/services/queue_service.py`
- Create: `tests/back_end/services/test_queue_service.py`

**Step 1: Write the failing test**

```python
def test_repeat_one_returns_same_track(queue_service, track_id):
    queue_service.set_repeat_one()
    assert queue_service.next_track(track_id) == track_id
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/services/test_queue_service.py -v`
Expected: FAIL due to missing queue behavior.

**Step 3: Write minimal implementation**

Implement next/previous logic with modes:
- normal
- shuffle
- repeat one
- repeat all

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/services/test_queue_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/back_end/services/queue_service.py tests/back_end/services/test_queue_service.py
git commit -m "feat: add queue service for next previous shuffle and repeat modes"
```

---

### Task 7: Feature 3 - Favorites Playlist

**Files:**
- Create: `src/app/back_end/controllers/favorites_controller.py`
- Create: `tests/back_end/controllers/test_favorites_controller.py`

**Step 1: Write the failing test**

```python
def test_favoriting_track_adds_it_to_favorites_playlist(controller, track_id):
    response = controller.mark_favorite(track_id)
    assert response.status is True
    assert controller.is_in_favorites(track_id) is True
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/controllers/test_favorites_controller.py -v`
Expected: FAIL due to missing controller methods.

**Step 3: Write minimal implementation**

Implement favorite toggle and smart playlist membership persistence.

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/controllers/test_favorites_controller.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/back_end/controllers/favorites_controller.py tests/back_end/controllers/test_favorites_controller.py
git commit -m "feat: add favorites playlist behavior"
```

---

### Task 8: Feature 4 - Playlist CRUD and Order Persistence

**Files:**
- Create: `src/app/back_end/controllers/playlist_controller.py`
- Modify: `src/app/back_end/data/repositories/repository.py`
- Create: `tests/back_end/controllers/test_playlist_controller.py`

**Step 1: Write the failing test**

```python
def test_reorder_playlist_tracks_persists_positions(controller, playlist_id, track_ids):
    controller.reorder_tracks(playlist_id, [track_ids[2], track_ids[0], track_ids[1]])
    saved = controller.get_playlist_track_ids(playlist_id)
    assert saved == [track_ids[2], track_ids[0], track_ids[1]]
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/controllers/test_playlist_controller.py -v`
Expected: FAIL due to missing CRUD/reorder logic.

**Step 3: Write minimal implementation**

Implement:
- create playlist
- edit playlist name
- delete playlist
- add/remove tracks
- reorder tracks with persistent `position`

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/controllers/test_playlist_controller.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/back_end/controllers/playlist_controller.py src/app/back_end/data/repositories/repository.py tests/back_end/controllers/test_playlist_controller.py
git commit -m "feat: add playlist crud and sequence ordering"
```

---

### Task 9: Feature 5 - Rust-Accelerated Scan, Metadata, Artwork

**Files:**
- Modify: `rust_back_end/src/scanner.rs`
- Modify: `rust_back_end/src/metadata.rs`
- Modify: `rust_back_end/src/artwork.rs`
- Modify: `rust_back_end/src/lib.rs`
- Modify: `src/app/back_end/services/rust_bridge.py`
- Create: `tests/back_end/services/test_rust_metadata_bridge.py`

**Step 1: Write the failing test**

```python
def test_read_metadata_returns_expected_fields(rust_bridge, sample_audio_file):
    result = rust_bridge.read_metadata(sample_audio_file)
    assert result.status is True
    assert "title" in result.data
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/services/test_rust_metadata_bridge.py -v`
Expected: FAIL due to missing Rust-exported methods.

**Step 3: Write minimal implementation**

Implement Rust exports:
- `scan_library(paths)`
- `read_metadata(path)`
- `write_metadata(path, changes)`
- `extract_artwork(path)`

Map outputs to typed Python response models.

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/services/test_rust_metadata_bridge.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rust_back_end src/app/back_end/services/rust_bridge.py tests/back_end/services/test_rust_metadata_bridge.py
git commit -m "feat: add rust-accelerated scanning metadata and artwork bridge"
```

---

### Task 10: Feature 6 - PyQt Frontend Shell + Playback Bar + Smooth Seek Drag

**Files:**
- Create: `src/app/front_end/main_window.py`
- Create: `src/app/front_end/now_playing_bar.py`
- Create: `src/app/front_end/playlist_view.py`
- Create: `src/app/front_end/metadata_editor_dialog.py`
- Modify: `src/main.py`
- Create: `tests/front_end/test_now_playing_bar.py`

**Step 1: Write the failing test**

```python
def test_seek_slider_defers_seek_until_release(qtbot, now_playing_bar):
    now_playing_bar.start_drag()
    now_playing_bar.drag_to(45000)
    assert now_playing_bar.has_emitted_seek is False
    now_playing_bar.end_drag()
    assert now_playing_bar.last_seek_position == 45000
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/front_end/test_now_playing_bar.py -v`
Expected: FAIL due to missing widget behavior.

**Step 3: Write minimal implementation**

Implement Apple Music-inspired PyQt UI layout and bottom now-playing bar with controls:
- previous
- play/pause
- next
- seek bar with smooth drag behavior
- playback speed control
- repeat/shuffle toggles

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/front_end/test_now_playing_bar.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/front_end src/main.py tests/front_end/test_now_playing_bar.py
git commit -m "feat: add pyqt frontend shell with playback controls and smooth seek drag"
```

---

### Task 11: Feature 7 - Metadata Editor (Add/Edit/Delete Tags via Rust)

**Files:**
- Modify: `src/app/front_end/metadata_editor_dialog.py`
- Create: `src/app/back_end/controllers/metadata_controller.py`
- Create: `tests/back_end/controllers/test_metadata_controller.py`

**Step 1: Write the failing test**

```python
def test_metadata_update_persists_to_file(controller, sample_audio_file):
    response = controller.update_metadata(sample_audio_file, {"title": "New Title"})
    assert response.status is True
    refreshed = controller.read_metadata(sample_audio_file)
    assert refreshed.data["title"] == "New Title"
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/back_end/controllers/test_metadata_controller.py -v`
Expected: FAIL due to missing controller workflow.

**Step 3: Write minimal implementation**

Implement metadata CRUD controller methods routed through Rust bridge and return typed models.

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/back_end/controllers/test_metadata_controller.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/front_end/metadata_editor_dialog.py src/app/back_end/controllers/metadata_controller.py tests/back_end/controllers/test_metadata_controller.py
git commit -m "feat: add metadata editor workflow with rust-backed tag operations"
```

---

### Task 12: Full Verification Gate Before Any Completion Claim

**Files:**
- Modify: `README.md`
- Create: `tests/manual/manual_test_checklist.md`

**Step 1: Write failing integration expectation tests**

```python
def test_end_to_end_playlist_reorder_and_playback_flow(app_bootstrap):
    # user creates playlist, reorders tracks, plays next/previous
    # expected order and playback state are correct
    ...
```

**Step 2: Run tests to verify failures (if missing paths/features)**

Run: `venv/bin/python -m pytest -v`
Expected: initial FAIL for missing e2e steps.

**Step 3: Implement minimal missing glue**

Add wiring gaps found by integration tests.

**Step 4: Run complete verification suite**

Run: `venv/bin/python -m pytest -v`
Expected: all tests PASS, no failures.

**Step 5: Manual verification**

Run app and verify checklist:
- play/pause works
- next/previous works
- playback speed works
- shuffle/repeat one/repeat all work
- seek bar drag is smooth and seeks on release
- favorite toggle updates favorites playlist
- playlist create/edit/delete works
- drag/drop reorder persists
- album art displays when embedded
- metadata add/edit/delete persists to file

**Step 6: Commit**

```bash
git add README.md tests/manual/manual_test_checklist.md
git commit -m "docs: add verification checklist and usage guidance"
```
