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

### Option 1: Install as Ubuntu package (recommended)

```bash
./build-deb.sh
sudo dpkg -i barulho_0.1.0.deb
```

Then launch from your application menu or run `barulho` from the terminal.

### Option 2: Run from source

```bash
./install.sh
./run.sh
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
