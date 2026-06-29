"""Handsfree — push-to-talk local dictation that types at your cursor.

Hold the push-to-talk key (default: Right Command), speak, release. The audio is
transcribed locally with MLX Whisper and pasted at the cursor of whatever app is
focused — including a terminal running Claude Code.
"""

from __future__ import annotations

import os
import threading

from pynput import keyboard

from handsfree.injector import Injector
from handsfree.permissions import request_accessibility
from handsfree.recorder import Recorder
from handsfree.transcriber import DEFAULT_MODEL, Transcriber

# Keys that do nothing on their own → safe push-to-talk defaults.
PTT_KEYS: dict[str, keyboard.Key] = {
    "cmd_r": keyboard.Key.cmd_r,
    "cmd_l": keyboard.Key.cmd_l,
    "alt_r": keyboard.Key.alt_r,
    "ctrl_r": keyboard.Key.ctrl_r,
    "f8": keyboard.Key.f8,
    "f9": keyboard.Key.f9,
}
DEFAULT_PTT = "cmd_r"
DEFAULT_LANGUAGE = "en"  # startup language when HANDSFREE_LANGUAGE is unset


class HandsfreeApp:
    def __init__(self, ptt_key: keyboard.Key, model: str, language: str | None):
        self.ptt_key = ptt_key
        self.recorder = Recorder()
        self.transcriber = Transcriber(model=model, language=language)
        self.injector = Injector()
        self._recording = False
        self._busy = threading.Lock()
        self._listener: keyboard.Listener | None = None

    def _on_press(self, key) -> None:  # noqa: ANN001
        # on_press repeats while the key is held; the flag guards against re-entry.
        if key == self.ptt_key and not self._recording:
            self._recording = True
            print("🎙️  listening… (release to transcribe)", flush=True)
            self.recorder.start()

    def _on_release(self, key) -> None:  # noqa: ANN001
        if key == self.ptt_key and self._recording:
            self._recording = False
            audio = self.recorder.stop()
            # Transcribe off the listener thread so the hotkey stays responsive.
            threading.Thread(target=self._process, args=(audio,), daemon=True).start()

    def _process(self, audio) -> None:  # noqa: ANN001
        # Serialize so a fast second utterance can't race the first.
        with self._busy:
            if audio.size == 0:
                return
            print("⏳ transcribing…", flush=True)
            text = self.transcriber.transcribe(audio)
            if not text:
                print("…(no speech detected)", flush=True)
                return
            print(f"📝 {text}", flush=True)
            self.injector.inject(text)

    def start(self) -> None:
        """Request permissions, warm up the model, and start the (non-blocking) listener.

        Returns once Handsfree is ready — the caller (the menu bar) then runs the main loop.
        """
        key_name = _key_name(self.ptt_key)
        if not request_accessibility(prompt=True):
            print(
                "⚠️  Accessibility not granted yet. Approve the dialog, or enable 'Handsfree'\n"
                "    in System Settings → Privacy & Security → Accessibility, then relaunch.",
                flush=True,
            )
        print(f"Loading model {self.transcriber.model!r} (first run downloads it)…", flush=True)
        self.transcriber.warmup()
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()
        print(f"✅ Handsfree ready. Hold [{key_name}] to dictate.", flush=True)

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None


def _key_name(key: keyboard.Key) -> str:
    for name, value in PTT_KEYS.items():
        if value == key:
            return name
    return str(key)


def main() -> None:
    key_name = os.environ.get("HANDSFREE_PTT_KEY", DEFAULT_PTT)
    ptt_key = PTT_KEYS.get(key_name)
    if ptt_key is None:
        print(
            f"⚠️  unknown HANDSFREE_PTT_KEY={key_name!r}; using {DEFAULT_PTT}. "
            f"Valid: {', '.join(PTT_KEYS)}",
            flush=True,
        )
        ptt_key = PTT_KEYS[DEFAULT_PTT]
    model = os.environ.get("HANDSFREE_MODEL", DEFAULT_MODEL)
    language = os.environ.get("HANDSFREE_LANGUAGE") or DEFAULT_LANGUAGE

    engine = HandsfreeApp(ptt_key=ptt_key, model=model, language=language)
    engine.start()

    # Menu bar owns the main thread; the listener runs on its own thread.
    from handsfree.menubar import run as run_menubar

    run_menubar(engine)


if __name__ == "__main__":
    main()
