"""Insert transcribed text at the cursor via clipboard paste (⌘V).

Uses AppKit's NSPasteboard rather than pbcopy/pbpaste. The shell tools encode using the
process locale (LANG/LC_CTYPE), which is absent when Handsfree is launched as a .app by
LaunchServices — that makes pbcopy mangle UTF-8 Korean/Japanese into mojibake. NSPasteboard
works with native NSStrings, so it round-trips any Unicode regardless of locale.
"""

from __future__ import annotations

import time

from AppKit import NSPasteboard, NSPasteboardTypeString
from pynput.keyboard import Controller, Key

# Time for the pasteboard to settle / the target app to read it before we restore.
_PASTEBOARD_SETTLE = 0.05
_PASTE_GRACE = 0.15


def _get_clipboard() -> str:
    pb = NSPasteboard.generalPasteboard()
    return pb.stringForType_(NSPasteboardTypeString) or ""


def _set_clipboard(text: str) -> None:
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setString_forType_(text, NSPasteboardTypeString)


class Injector:
    """Paste text at the cursor, restoring the user's previous (text) clipboard.

    Clipboard + ⌘V is more reliable than synthetic typing for non-Latin text and long
    passages. Restore only round-trips plain text — a previously-copied image/RTF is lost.
    """

    def __init__(self):
        self._keyboard = Controller()

    def inject(self, text: str) -> None:
        if not text:
            return
        saved = _get_clipboard()
        _set_clipboard(text)
        time.sleep(_PASTEBOARD_SETTLE)
        with self._keyboard.pressed(Key.cmd):
            self._keyboard.tap("v")
        time.sleep(_PASTE_GRACE)
        _set_clipboard(saved)
