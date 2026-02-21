# Barulho

A Linux desktop app that plays audio samples in response to MIDI events. Supports MIDI over Bluetooth.

## Features

- **MIDI Event Log**: Scrollable log showing all incoming MIDI events with note, velocity, and channel
- **Flexible Mappings**: Map any MIDI note to any audio file
- **Record Mode**: Capture MIDI input to quickly create mappings
- **Per-Mapping Controls**: Volume slider and velocity sensitivity toggle for each mapping
- **Polyphonic Playback**: Different notes layer; same note retriggered restarts
- **Global Volume**: Master volume control
- **Persistence**: Auto-saves config on exit, with custom save/load locations

## Requirements

- Ubuntu Linux (or similar)
- Python 3.10+
- GTK 4
- GStreamer

## Installation

```bash
# Install system dependencies
sudo apt install libgtk-4-dev libgirepository1.0-dev \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    python3-gi python3-gi-cairo gir1.2-gtk-4.0

# Create virtual environment and install Python dependencies
python3 -m venv --system-site-packages .venv
.venv/bin/pip install python-rtmidi

# Run
.venv/bin/python run.py
```

## Usage

1. Connect your MIDI device (including Bluetooth MIDI via system settings)
2. Run Barulho
3. Click **+** to add a new mapping - it will wait for MIDI input
4. Play a note on your MIDI device to assign it
5. Click the file button to select an audio sample
6. Adjust volume and velocity sensitivity as needed
7. Play!

Config is saved to `~/.config/barulho/config.json` on exit.
