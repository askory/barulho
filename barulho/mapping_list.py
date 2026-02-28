"""Mapping list widget."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from barulho.config import (
    Mapping, Config, save_config, load_config,
    save_last_config_path, load_last_config_path,
)
from barulho.mapping_row import MappingRow
from barulho.audio_player import AudioPlayer
from pathlib import Path


class MappingListWidget(Gtk.Box):
    """Container for all mappings with global controls."""

    def __init__(self, audio_player: AudioPlayer):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.audio_player = audio_player
        self.config: Config = Config()
        self.config_path: Path | None = None
        self._recording_row: MappingRow | None = None
        self._rows: list[MappingRow] = []

        # Header with global controls
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.set_margin_start(4)
        header.set_margin_end(4)

        # Title
        title = Gtk.Label(label="Mappings")
        title.add_css_class("heading")
        title.set_hexpand(True)
        title.set_halign(Gtk.Align.START)
        header.append(title)

        # Global volume
        vol_label = Gtk.Label(label="Master:")
        header.append(vol_label)
        self.global_volume = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.global_volume.set_value(80)
        self.global_volume.set_size_request(100, -1)
        self.global_volume.set_draw_value(False)
        self.global_volume.connect("value-changed", self._on_global_volume_changed)
        header.append(self.global_volume)

        # Save/Load buttons
        load_btn = Gtk.Button(label="Load")
        load_btn.set_tooltip_text("Load config from file")
        load_btn.connect("clicked", self._on_load_clicked)
        header.append(load_btn)

        save_btn = Gtk.Button(label="Save As")
        save_btn.set_tooltip_text("Save config to file")
        save_btn.connect("clicked", self._on_save_clicked)
        header.append(save_btn)

        # Add mapping button
        add_btn = Gtk.Button(label="+")
        add_btn.add_css_class("suggested-action")
        add_btn.set_tooltip_text("Add new mapping")
        add_btn.connect("clicked", self._on_add_clicked)
        header.append(add_btn)

        self.append(header)

        # Separator
        self.append(Gtk.Separator())

        # Scrollable list of mappings
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scrolled.set_child(self.list_box)
        self.append(scrolled)

    def load_from_file(self, path: Path | None = None):
        """Load config from file. Uses last-used path if none given."""
        if path is None:
            path = load_last_config_path()
        self.config, self.config_path = load_config(path)
        save_last_config_path(self.config_path)
        self.global_volume.set_value(self.config.global_volume * 100)
        self.audio_player.global_volume = self.config.global_volume

        # Clear existing rows
        while self._rows:
            row = self._rows.pop()
            self.list_box.remove(row)

        # Add rows for each mapping
        for mapping in self.config.mappings:
            self._add_row(mapping)

    def save_to_file(self, path: Path | None = None):
        """Save config to file."""
        save_path = path or self.config_path
        self.config_path = save_config(self.config, save_path)
        save_last_config_path(self.config_path)

    def handle_midi_event(self, note: int):
        """Handle MIDI note for recording mode."""
        if self._recording_row:
            self._recording_row.set_note_from_midi(note)
            self._recording_row = None

    def _add_row(self, mapping: Mapping) -> MappingRow:
        """Add a mapping row."""
        row = MappingRow(
            mapping=mapping,
            on_change=self._on_mapping_changed,
            on_delete=self._on_delete_row,
            on_test=self._on_test_mapping,
            on_record=self._on_record_start,
        )
        self._rows.append(row)
        self.list_box.append(row)
        return row

    def _on_add_clicked(self, _btn):
        """Add a new mapping."""
        mapping = Mapping(note=60, file_path="", volume=0.8, velocity_sensitive=True)
        self.config.mappings.append(mapping)
        row = self._add_row(mapping)
        # Start recording mode for new mapping
        self._recording_row = row
        row._on_record_clicked(None)

    def _on_delete_row(self, row: MappingRow):
        """Delete a mapping row."""
        if row in self._rows:
            self._rows.remove(row)
            self.config.mappings.remove(row.mapping)
            self.list_box.remove(row)
            self._on_mapping_changed()

    def _on_test_mapping(self, mapping: Mapping):
        """Test play a mapping."""
        if mapping.file_path:
            self.audio_player.play(
                note=mapping.note,
                file_path=mapping.file_path,
                volume=mapping.volume,
                velocity_factor=1.0,
            )

    def _on_record_start(self, row: MappingRow):
        """Start recording on a row."""
        # Cancel any other recording
        if self._recording_row and self._recording_row != row:
            self._recording_row.set_note_from_midi(self._recording_row.mapping.note)
        self._recording_row = row

    def _on_mapping_changed(self):
        """Called when any mapping changes - trigger auto-save."""
        # Could debounce this, but for simplicity just save
        pass  # Auto-save happens on close

    def _on_global_volume_changed(self, scale):
        """Handle global volume change."""
        self.config.global_volume = scale.get_value() / 100
        self.audio_player.global_volume = self.config.global_volume

    def _on_load_clicked(self, _btn):
        """Open file chooser to load config."""
        dialog = Gtk.FileDialog()
        dialog.set_title("Load Config")

        json_filter = Gtk.FileFilter()
        json_filter.set_name("JSON Files")
        json_filter.add_pattern("*.json")

        dialog.open(self.get_root(), None, self._on_load_chosen)

    def _on_load_chosen(self, dialog, result):
        """Handle load file selection."""
        try:
            file = dialog.open_finish(result)
            if file:
                self.load_from_file(Path(file.get_path()))
        except GLib.Error:
            pass  # User cancelled

    def _on_save_clicked(self, _btn):
        """Open file chooser to save config."""
        dialog = Gtk.FileDialog()
        dialog.set_title("Save Config")
        dialog.set_initial_name("config.json")
        dialog.save(self.get_root(), None, self._on_save_chosen)

    def _on_save_chosen(self, dialog, result):
        """Handle save file selection."""
        try:
            file = dialog.save_finish(result)
            if file:
                self.save_to_file(Path(file.get_path()))
        except GLib.Error:
            pass  # User cancelled
