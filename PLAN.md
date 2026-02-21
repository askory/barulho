# Implementation Plan

## Technology Stack

- **GUI**: GTK 4 via PyGObject (`gi`)
- **MIDI**: `python-rtmidi` (direct, low-latency MIDI access)
- **Audio**: GStreamer via PyGObject (GTK-native, supports all local codecs)
- **Config**: Standard library `json`

## Project Structure

```
barulho/
├── barulho/
│   ├── __init__.py
│   ├── main.py           # Entry point, application setup
│   ├── window.py         # Main window, layout
│   ├── midi_log.py       # MIDI event log widget
│   ├── mapping_list.py   # Mapping list widget
│   ├── mapping_row.py    # Individual mapping row widget
│   ├── midi_handler.py   # MIDI input processing
│   ├── audio_player.py   # Audio playback engine
│   └── config.py         # Config load/save
├── CLAUDE.md
├── REQUIREMENTS.md
├── PLAN.md
├── README.md
├── pyproject.toml
└── run.py                # Development runner
```

## Dependencies (pyproject.toml)

```toml
[project]
name = "barulho"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "PyGObject>=3.42",
    "python-rtmidi>=1.5",
]

[project.scripts]
barulho = "barulho.main:main"
```

System dependencies (Ubuntu):
- `libgtk-4-dev`
- `libgirepository1.0-dev`
- `gstreamer1.0-plugins-good`
- `gstreamer1.0-plugins-bad`
- `gstreamer1.0-plugins-ugly`

## Implementation Phases

### Phase 1: Project Setup
- Create pyproject.toml with dependencies
- Create package structure
- Implement basic GTK window that opens and closes cleanly

### Phase 2: MIDI Event Log
- Implement `midi_handler.py`: Connect to all MIDI inputs, emit events
- Implement `midi_log.py`: Scrollable list widget displaying events
- Wire up MIDI handler to log widget
- Verify events display and auto-scroll works

### Phase 3: Audio Playback Engine
- Implement `audio_player.py` using GStreamer
- Support playing a sample with volume parameter
- Handle polyphony (multiple simultaneous sounds)
- Handle retriggering (stop and restart same note)

### Phase 4: Config Management
- Implement `config.py`: Load/save JSON config
- Default path: `~/.config/barulho/config.json`
- Create config directory if missing

### Phase 5: Mapping List UI
- Implement `mapping_row.py`: Single mapping with all controls
  - Note dropdown + record button
  - File chooser
  - Volume slider
  - Velocity sensitivity toggle
  - Test button
  - Delete button
- Implement `mapping_list.py`: Container with add button and global volume
- Wire up to config (load on start, save on changes)

### Phase 6: MIDI-to-Audio Wiring
- Connect MIDI events to mapping lookup
- Trigger audio playback with correct volume calculation
- Handle velocity sensitivity

### Phase 7: Save/Load Custom Location
- Add menu or buttons for Save As / Load
- File dialogs for custom paths
- Track current config path for auto-save

### Phase 8: Polish
- Auto-save on window close
- Error handling (missing files, invalid config)
- Ensure clean shutdown (stop MIDI, stop audio)

## Key Technical Notes

### MIDI Threading
`python-rtmidi` callbacks run on a separate thread. Use `GLib.idle_add()` to safely update GTK widgets from MIDI callback.

### GStreamer Playback
For each active sound, create a `playbin` element. Set URI and volume, connect to "about-to-finish" or EOS to clean up. Keep a dict of active players keyed by note for retriggering.

### Note Representation
Store notes as MIDI numbers (0-127). Display as note names (C4, D#5, etc.) in UI. Helper function to convert between representations.
