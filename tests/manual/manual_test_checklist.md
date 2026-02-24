# Manual Test Checklist

Date:
Tester:
OS:

## Setup

- [ ] `venv` created and dependencies installed
- [ ] Rust extension built with `maturin develop`
- [ ] App launches with `PYTHONPATH=src venv/bin/python src/main.py`

## Playback Core

- [ ] Add at least 3 songs using `Add Songs`
- [ ] `Play` starts playback
- [ ] `Pause` pauses playback
- [ ] `Next` moves to next track in queue
- [ ] `Prev` moves to previous track in queue

## Seek Bar

- [ ] Drag seek slider while song is playing
- [ ] Confirm timeline updates during drag
- [ ] Confirm actual player seek is applied on release
- [ ] Confirm playback resumes from released timestamp

## Speed / Queue Modes

- [ ] Change playback speed (0.50x, 1.00x, 1.25x, 1.50x, 2.00x)
- [ ] Toggle shuffle and confirm order behavior changes
- [ ] Cycle repeat mode: Off -> All -> One -> Off

## Metadata Editor

- [ ] Open `Edit Metadata` for the currently selected track
- [ ] Edit title/artist/album/genre and save
- [ ] Confirm now-playing labels reflect updated metadata
- [ ] Clear one metadata field and save
- [ ] Confirm cleared field is persisted as deleted/empty on refresh

## Album Art

- [ ] Track with artwork shows artwork in now-playing area
- [ ] Track without artwork shows placeholder image

## Favorites / Playlist Persistence (backend-verified)

- [ ] `tests/back_end/controllers/test_favorites_controller.py` passes
- [ ] `tests/back_end/controllers/test_playlist_controller.py` passes
- [ ] `tests/integration/test_end_to_end_playlist_reorder_and_playback_flow.py` passes

## Result

- [ ] PASS
- [ ] FAIL (attach notes)

Notes:
