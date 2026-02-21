"""Application entry point."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from barulho.window import MainWindow


class BarulhoApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.github.askory.barulho")
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = MainWindow(application=self)
        self.window.present()


def main():
    app = BarulhoApp()
    app.run(None)


if __name__ == "__main__":
    main()
