"""Local speech-to-text via MLX Whisper (Metal-accelerated on Apple Silicon)."""

from __future__ import annotations

import mlx_whisper
import numpy as np

from handsfree.recorder import SAMPLE_RATE

# Multilingual turbo model, 4-bit quantized (~0.46 GB). Handles EN/KO/JA.
DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo-q4"


class Transcriber:
    """Wraps mlx-whisper. language=None auto-detects (handles EN/KO/JA switching)."""

    def __init__(self, model: str = DEFAULT_MODEL, language: str | None = None):
        self.model = model
        self.language = language

    def transcribe(self, audio: np.ndarray) -> str:
        if audio.size == 0:
            return ""
        result = mlx_whisper.transcribe(
            audio,
            path_or_hf_repo=self.model,
            language=self.language,
        )
        return result.get("text", "").strip()

    def warmup(self) -> None:
        """Load weights now (on 1s of silence) so the first utterance is fast."""
        try:
            self.transcribe(np.zeros(SAMPLE_RATE, dtype=np.float32))
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  warmup failed (will load lazily): {exc}", flush=True)
