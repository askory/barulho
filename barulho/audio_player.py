"""Audio playback engine using GStreamer."""

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)


class AudioPlayer:
    """Handles audio sample playback with polyphony support."""

    def __init__(self):
        # Track active players by note for retriggering
        self._active: dict[int, Gst.Element] = {}
        self._global_volume = 1.0

    @property
    def global_volume(self) -> float:
        return self._global_volume

    @global_volume.setter
    def global_volume(self, value: float):
        self._global_volume = max(0.0, min(1.0, value))

    def play(self, note: int, file_path: str, volume: float, velocity_factor: float = 1.0):
        """
        Play an audio sample.

        Args:
            note: MIDI note number (used for retriggering logic)
            file_path: Path to the audio file
            volume: Mapping volume (0.0 to 1.0)
            velocity_factor: Velocity-based volume factor (0.0 to 1.0)
        """
        # Stop any existing playback of this note
        self.stop_note(note)

        # Create playbin
        player = Gst.ElementFactory.make("playbin", f"player_{note}")
        if not player:
            return

        # Set file URI
        uri = file_path if file_path.startswith("file://") else f"file://{file_path}"
        player.set_property("uri", uri)

        # Calculate final volume
        final_volume = self._global_volume * volume * velocity_factor
        player.set_property("volume", final_volume)

        # Connect to end-of-stream to clean up
        bus = player.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self._on_eos, note)
        bus.connect("message::error", self._on_error, note)

        # Start playback
        self._active[note] = player
        player.set_state(Gst.State.PLAYING)

    def stop_note(self, note: int):
        """Stop playback of a specific note."""
        if note in self._active:
            player = self._active.pop(note)
            player.set_state(Gst.State.NULL)

    def stop_all(self):
        """Stop all playback."""
        for note in list(self._active.keys()):
            self.stop_note(note)

    def _on_eos(self, _bus, _message, note: int):
        """Handle end of stream."""
        if note in self._active:
            player = self._active.pop(note)
            player.set_state(Gst.State.NULL)

    def _on_error(self, _bus, message, note: int):
        """Handle playback error."""
        err, debug = message.parse_error()
        print(f"Audio error for note {note}: {err.message}")
        if note in self._active:
            player = self._active.pop(note)
            player.set_state(Gst.State.NULL)
