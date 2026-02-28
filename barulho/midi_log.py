"""MIDI event log widget."""

from datetime import datetime

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Pango

from barulho.midi_handler import MidiEvent


class MidiLogWidget(Gtk.Frame):
    """Scrollable log of MIDI events."""

    def __init__(self):
        super().__init__()

        # Frame header with label and scan button
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.append(Gtk.Label(label="MIDI Events"))
        self.scan_btn = Gtk.Button(label="Scan MIDI")
        self.scan_btn.set_tooltip_text("Rescan for MIDI devices")
        header.append(self.scan_btn)
        self.set_label_widget(header)

        # Scrolled window for the log
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(120)  # ~5 rows
        scrolled.set_vexpand(False)
        self.set_child(scrolled)

        # List box for events
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.set_child(self.list_box)

        self._scrolled = scrolled

    def add_event(self, event: MidiEvent):
        """Add a MIDI event to the log. Thread-safe via GLib.idle_add."""
        GLib.idle_add(self._add_event_impl, event)

    def _add_event_impl(self, event: MidiEvent):
        """Internal implementation - must run on main thread."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        event_type = "ON " if event.is_note_on else "OFF"
        text = (
            f"{timestamp}  {event_type}  {event.note_name:4}  "
            f"vel={event.velocity:3}  ch={event.channel + 1:2}"
        )

        label = Gtk.Label(label=text)
        label.set_halign(Gtk.Align.START)
        label.set_margin_start(8)
        label.set_margin_end(8)
        label.set_margin_top(2)
        label.set_margin_bottom(2)

        # Use monospace font
        attr_list = Pango.AttrList()
        attr_list.insert(Pango.attr_family_new("monospace"))
        label.set_attributes(attr_list)

        self.list_box.append(label)

        # Auto-scroll to bottom
        GLib.idle_add(self._scroll_to_bottom)

        return False  # Don't repeat

    def _scroll_to_bottom(self):
        """Scroll to show the most recent event."""
        adj = self._scrolled.get_vadjustment()
        adj.set_value(adj.get_upper())
        return False
