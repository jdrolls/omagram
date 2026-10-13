"""Offline real-terminal probe: python -m telegram_tui.media_probe IMAGE."""

import sys

from PIL import Image
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from .native_media import cache_cell_geometry, sixel_widget


class MediaProbe(App):
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Static("Omagram native Sixel probe — q closes this test")
        with VerticalScroll():
            with Image.open(sys.argv[1]) as source:
                yield sixel_widget(source.convert("RGB"))
            yield Static("Native pixels above; no HalfCell renderer and no Telegram connection.")


if __name__ == "__main__":
    # Validate before entering Textual's run loop: App.run() swallows an
    # exception raised from compose() and still exits 0, so a bad path
    # or missing argument would otherwise print a traceback yet look
    # like success to any script checking the exit code.
    if len(sys.argv) != 2:
        print("usage: python -m telegram_tui.media_probe IMAGE", file=sys.stderr)
        sys.exit(1)
    try:
        with Image.open(sys.argv[1]):
            pass
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    cache_cell_geometry()
    MediaProbe().run()
