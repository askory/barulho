"""MIDI input handling."""

from dataclasses import dataclass
from typing import Callable

import rtmidi


@dataclass
class MidiEvent:
    """Represents a MIDI note event."""

    note: int
    velocity: int
    channel: int
    port_name: str
    is_note_on: bool

    @property
    def note_name(self) -> str:
        """Convert MIDI note number to name (e.g., 60 -> C4)."""
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (self.note // 12) - 1
        name = names[self.note % 12]
        return f"{name}{octave}"


class MidiHandler:
    """Handles MIDI input from all available ports."""

    def __init__(self, callback: Callable[[MidiEvent], None]):
        self.callback = callback
        self.inputs: list[rtmidi.MidiIn] = []
        self._running = False

    def start(self):
        """Open all available MIDI input ports."""
        if self._running:
            return

        self._running = True
        probe = rtmidi.MidiIn()
        port_count = probe.get_port_count()

        for i in range(port_count):
            port_name = probe.get_port_name(i)
            midi_in = rtmidi.MidiIn()
            midi_in.open_port(i)
            midi_in.set_callback(self._make_callback(port_name))
            self.inputs.append(midi_in)

        probe.delete()

    def stop(self):
        """Close all MIDI inputs."""
        self._running = False
        for midi_in in self.inputs:
            midi_in.close_port()
            midi_in.delete()
        self.inputs.clear()

    def _make_callback(self, port_name: str):
        """Create a callback for a specific port."""

        def callback(event, _data):
            message, _delta = event
            if len(message) < 3:
                return

            status = message[0]
            channel = status & 0x0F
            msg_type = status & 0xF0

            # Note On (0x90) or Note Off (0x80)
            if msg_type == 0x90:
                note, velocity = message[1], message[2]
                # Note On with velocity 0 is treated as Note Off
                is_note_on = velocity > 0
                midi_event = MidiEvent(
                    note=note,
                    velocity=velocity,
                    channel=channel,
                    port_name=port_name,
                    is_note_on=is_note_on,
                )
                self.callback(midi_event)
            elif msg_type == 0x80:
                note, velocity = message[1], message[2]
                midi_event = MidiEvent(
                    note=note,
                    velocity=velocity,
                    channel=channel,
                    port_name=port_name,
                    is_note_on=False,
                )
                self.callback(midi_event)

        return callback
