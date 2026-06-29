"""Menu bar UI: live language picker + Quit, backed by the dictation engine.

Runs a rumps (NSStatusItem) app on the main thread. Selecting a language just sets
`engine.transcriber.language`, which the worker thread reads at transcribe time — so the
choice takes effect on the next utterance with no restart.
"""

from __future__ import annotations

import signal

import rumps

# (menu label, Whisper language code).
LANGUAGES: list[tuple[str, str]] = [
    ("English", "en"),
    ("한국어 (Korean)", "ko"),
    ("日本語 (Japanese)", "ja"),
]


class HandsfreeMenuBar(rumps.App):
    def __init__(self, engine):
        super().__init__("Handsfree", title="🎙", quit_button=None)
        self.engine = engine
        self._items: dict[str, rumps.MenuItem] = {}
        for label, code in LANGUAGES:
            item = rumps.MenuItem(label, callback=self._setter(code))
            self._items[code] = item
            self.menu.add(item)
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Quit Handsfree", callback=self._quit))
        self._mark(engine.transcriber.language)

    def _setter(self, code: str):
        def _cb(_) -> None:  # noqa: ANN001
            self.engine.transcriber.language = code
            self._mark(code)
            print(f"🌐 language → {code}", flush=True)

        return _cb

    def _mark(self, code: str) -> None:
        for c, item in self._items.items():
            item.state = 1 if c == code else 0
        self.title = f"🎙 {code.upper()}"

    def _quit(self, _) -> None:  # noqa: ANN001
        self.engine.stop()
        rumps.quit_application()


def run(engine) -> None:
    """Run the menu bar on the main thread (blocks until Quit)."""
    app = HandsfreeMenuBar(engine)
    # A 1s no-op timer lets the NS run loop yield so Ctrl-C (SIGINT) is delivered too.
    signal.signal(signal.SIGINT, lambda *_: app._quit(None))
    rumps.Timer(lambda _: None, 1).start()
    app.run()
