"""Main application window."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from barulho.midi_handler import MidiHandler, MidiEvent
from barulho.midi_log import MidiLogWidget
from barulho.audio_player import AudioPlayer
from barulho.mapping_list import MappingListWidget


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Barulho")
        self.set_default_size(700, 550)

        # Main vertical layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.set_child(main_box)

        # MIDI event log
        self.midi_log = MidiLogWidget()
        main_box.append(self.midi_log)

        # Audio player
        self.audio_player = AudioPlayer()

        # Mapping list
        self.mapping_list = MappingListWidget(self.audio_player)
        self.mapping_list.set_vexpand(True)
        main_box.append(self.mapping_list)

        # Load default config
        self.mapping_list.load_from_file()

        # MIDI handler
        self.midi_handler = MidiHandler(self._on_midi_event)
        self.midi_handler.start()

        # Connect scan button
        self.midi_log.scan_btn.connect("clicked", self._on_scan_midi)

        # Clean up on close
        self.connect("close-request", self._on_close)

    def _on_midi_event(self, event: MidiEvent):
        """Handle incoming MIDI event."""
        # Add to log
        self.midi_log.add_event(event)

        # Handle on main thread
        GLib.idle_add(self._process_midi_event, event)

    def _process_midi_event(self, event: MidiEvent):
        """Process MIDI event on main thread."""
        # Check if we're recording
        self.mapping_list.handle_midi_event(event.note)

        # Trigger audio on note-on
        if event.is_note_on:
            self._trigger_audio(event)

        return False

    def _trigger_audio(self, event: MidiEvent):
        """Trigger audio for a MIDI event."""
        # Find matching mapping
        for mapping in self.mapping_list.config.mappings:
            if mapping.note == event.note and mapping.file_path:
                velocity_factor = 1.0
                if mapping.velocity_sensitive:
                    velocity_factor = event.velocity / 127.0

                self.audio_player.play(
                    note=event.note,
                    file_path=mapping.file_path,
                    volume=mapping.volume,
                    velocity_factor=velocity_factor,
                )
                break  # One mapping per note

    def _on_scan_midi(self, _btn):
        """Rescan for MIDI devices."""
        self.midi_handler.rescan()

    def _on_close(self, _window):
        """Handle window close - auto-save and cleanup."""
        self.mapping_list.save_to_file()
        self.midi_handler.stop()
        self.audio_player.stop_all()
        return False
