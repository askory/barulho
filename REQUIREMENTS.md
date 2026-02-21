# Requirements

## Overview

Barulho is a Linux desktop application (Ubuntu) that plays audio samples in response to MIDI events, with support for MIDI over Bluetooth. Built with Python and GTK.

## User Interface

### Layout

Two-section GUI:
1. **Top**: MIDI event log
2. **Bottom**: Mapping list with global controls

### MIDI Event Log

- Scrollable list showing all MIDI events since app started
- Viewport displays ~5 events at a time
- Auto-scrolls to bottom when new events arrive
- Each event shows: note, velocity, channel, timestamp

### Mapping List

Each mapping row displays:
- **Trigger note**: Editable via dropdown, or "Record" button to capture next MIDI input
- **Audio file path**: File picker to select sample
- **Volume slider**: Default 50%, range 0-100%
- **Velocity sensitivity toggle**: When on, MIDI velocity scales playback volume
- **Test button**: Play sample without MIDI trigger
- **Delete button**: Remove mapping

Controls:
- **Add mapping button (+)**: Creates new mapping in "record" mode, waiting for MIDI input
- **Global volume knob**: Master volume control

## Audio Behavior

- **Polyphonic**: Different notes layer (play simultaneously)
- **Monophonic per note**: Same note retriggered restarts its sample
- **Format support**: All formats playable on the local system
- **Volume calculation**: `final_volume = global_volume * mapping_volume * velocity_factor`
  - `velocity_factor` = 1.0 if sensitivity off, else `midi_velocity / 127`

## MIDI Input

- Listen to all available MIDI inputs (no device selection UI)
- Bluetooth MIDI assumed to be paired/connected at OS level
- One mapping per note (simple model, no velocity ranges)

## Persistence

- **Default location**: `~/.config/barulho/config.json`
- **Custom location**: Save/load from user-specified path via file dialog
- **Auto-save**: Save to current config file on exit
- **Format**: JSON

### Config Schema

```json
{
  "global_volume": 0.8,
  "mappings": [
    {
      "note": 60,
      "file_path": "/path/to/sample.wav",
      "volume": 0.5,
      "velocity_sensitive": true
    }
  ]
}
```
