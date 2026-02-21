"""Individual mapping row widget."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from barulho.config import Mapping


# MIDI note names for dropdown
NOTE_NAMES = []
for octave in range(-1, 10):
    for name in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]:
        note_num = (octave + 1) * 12 + ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"].index(name)
        if 0 <= note_num <= 127:
            NOTE_NAMES.append((note_num, f"{name}{octave}"))


class MappingRow(Gtk.Box):
    """A single mapping row with all controls."""

    def __init__(self, mapping: Mapping, on_change, on_delete, on_test, on_record):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_start(4)
        self.set_margin_end(4)

        self.mapping = mapping
        self._on_change = on_change
        self._on_delete = on_delete
        self._on_test = on_test
        self._on_record = on_record
        self._recording = False

        # Note dropdown
        self.note_dropdown = Gtk.DropDown()
        note_strings = Gtk.StringList()
        selected_idx = 0
        for i, (note_num, note_name) in enumerate(NOTE_NAMES):
            note_strings.append(note_name)
            if note_num == mapping.note:
                selected_idx = i
        self.note_dropdown.set_model(note_strings)
        self.note_dropdown.set_selected(selected_idx)
        self.note_dropdown.connect("notify::selected", self._on_note_changed)
        self.note_dropdown.set_size_request(80, -1)
        self.append(self.note_dropdown)

        # Record button
        self.record_btn = Gtk.Button(label="Rec")
        self.record_btn.set_tooltip_text("Record next MIDI note")
        self.record_btn.connect("clicked", self._on_record_clicked)
        self.append(self.record_btn)

        # File path
        self.file_btn = Gtk.Button()
        self._update_file_button_label()
        self.file_btn.set_hexpand(True)
        self.file_btn.set_tooltip_text(mapping.file_path or "Click to select file")
        self.file_btn.connect("clicked", self._on_file_clicked)
        self.append(self.file_btn)

        # Volume slider
        vol_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        vol_label = Gtk.Label(label="Vol:")
        vol_box.append(vol_label)
        self.volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.volume_scale.set_value(mapping.volume * 100)
        self.volume_scale.set_size_request(80, -1)
        self.volume_scale.set_draw_value(False)
        self.volume_scale.connect("value-changed", self._on_volume_changed)
        vol_box.append(self.volume_scale)
        self.append(vol_box)

        # Velocity sensitivity toggle
        self.vel_check = Gtk.CheckButton(label="Vel")
        self.vel_check.set_active(mapping.velocity_sensitive)
        self.vel_check.set_tooltip_text("Velocity sensitivity")
        self.vel_check.connect("toggled", self._on_vel_toggled)
        self.append(self.vel_check)

        # Test button
        test_btn = Gtk.Button(label="Test")
        test_btn.set_tooltip_text("Play sample")
        test_btn.connect("clicked", self._on_test_clicked)
        self.append(test_btn)

        # Delete button
        del_btn = Gtk.Button(label="Del")
        del_btn.add_css_class("destructive-action")
        del_btn.set_tooltip_text("Delete mapping")
        del_btn.connect("clicked", self._on_delete_clicked)
        self.append(del_btn)

    def _update_file_button_label(self):
        """Update file button to show filename or placeholder."""
        if self.mapping.file_path:
            # Show just the filename
            import os
            name = os.path.basename(self.mapping.file_path)
            self.file_btn.set_label(name)
        else:
            self.file_btn.set_label("(select file)")

    def _on_note_changed(self, dropdown, _param):
        """Handle note selection change."""
        idx = dropdown.get_selected()
        if 0 <= idx < len(NOTE_NAMES):
            self.mapping.note = NOTE_NAMES[idx][0]
            self._on_change()

    def _on_record_clicked(self, _btn):
        """Start recording mode."""
        self._recording = True
        self.record_btn.set_label("...")
        self.record_btn.add_css_class("suggested-action")
        self._on_record(self)

    def set_note_from_midi(self, note: int):
        """Set note from MIDI input (called during recording)."""
        self._recording = False
        self.record_btn.set_label("Rec")
        self.record_btn.remove_css_class("suggested-action")

        self.mapping.note = note
        # Update dropdown
        for i, (note_num, _) in enumerate(NOTE_NAMES):
            if note_num == note:
                self.note_dropdown.set_selected(i)
                break
        self._on_change()

    def is_recording(self) -> bool:
        return self._recording

    def _on_file_clicked(self, _btn):
        """Open file chooser."""
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Audio File")

        # Audio file filter
        audio_filter = Gtk.FileFilter()
        audio_filter.set_name("Audio Files")
        audio_filter.add_mime_type("audio/*")

        filters = Gtk.FilterListModel()
        filter_list = [audio_filter]

        dialog.open(self.get_root(), None, self._on_file_chosen)

    def _on_file_chosen(self, dialog, result):
        """Handle file selection."""
        try:
            file = dialog.open_finish(result)
            if file:
                self.mapping.file_path = file.get_path()
                self._update_file_button_label()
                self.file_btn.set_tooltip_text(self.mapping.file_path)
                self._on_change()
        except GLib.Error:
            pass  # User cancelled

    def _on_volume_changed(self, scale):
        """Handle volume change."""
        self.mapping.volume = scale.get_value() / 100
        self._on_change()

    def _on_vel_toggled(self, check):
        """Handle velocity sensitivity toggle."""
        self.mapping.velocity_sensitive = check.get_active()
        self._on_change()

    def _on_test_clicked(self, _btn):
        """Play the sample."""
        self._on_test(self.mapping)

    def _on_delete_clicked(self, _btn):
        """Delete this mapping."""
        self._on_delete(self)
