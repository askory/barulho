# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Barulho is a Linux desktop app (Ubuntu) that plays audio samples in response to MIDI events. Python + GTK 4.

See REQUIREMENTS.md for full specs and PLAN.md for implementation details.

## Tech Stack

- **GUI**: GTK 4 via PyGObject
- **MIDI**: python-rtmidi
- **Audio**: GStreamer via PyGObject

## Development Commands

```bash
# Install system dependencies (Ubuntu)
sudo apt install libgtk-4-dev libgirepository1.0-dev gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly python3-gi python3-gi-cairo gir1.2-gtk-4.0

# Create venv with system site-packages (for GTK bindings)
python3 -m venv --system-site-packages .venv
.venv/bin/pip install python-rtmidi

# Run the app
.venv/bin/python run.py
```

## Architecture

- `barulho/main.py` - Entry point
- `barulho/window.py` - Main window layout
- `barulho/midi_handler.py` - MIDI input (runs on separate thread, use `GLib.idle_add()` for GTK updates)
- `barulho/audio_player.py` - GStreamer playback engine
- `barulho/config.py` - JSON config load/save

## Version Control

Mercurial (hg) primary VCS with git mirror at `git@github.com:askory/barulho`.
