"""Microphone capture for push-to-talk dictation."""

from __future__ import annotations

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16_000  # what Whisper expects
CHANNELS = 1


class Recorder:
    """Records mic audio into a buffer between start() and stop().

    Capture runs on PortAudio's own thread via the stream callback, so start()
    returns immediately and recording continues until stop() is called.
    """

    def __init__(self, samplerate: int = SAMPLE_RATE, channels: int = CHANNELS):
        self.samplerate = samplerate
        self.channels = channels
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def start(self) -> None:
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="float32",
            callback=self._on_audio,
        )
        self._stream.start()

    def _on_audio(self, indata, frames, time_info, status) -> None:  # noqa: ANN001
        # Runs on the audio thread; just stash a copy (indata is reused by PortAudio).
        if status:
            print(f"⚠️  audio status: {status}", flush=True)
        self._frames.append(indata.copy())

    def stop(self) -> np.ndarray:
        """Stop recording and return mono float32 samples at self.samplerate."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._frames:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(self._frames, axis=0).reshape(-1)
