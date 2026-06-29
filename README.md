# Handsfree

Push-to-talk **local** speech-to-text for macOS. Hold a key, speak, release — your words are
transcribed on-device and pasted at the cursor in whatever app is focused (terminal, editor,
browser…). No audio ever leaves your machine.

Powered by [MLX Whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) on Apple
Silicon. Handles **English, Korean, and Japanese**, switchable from a menu bar icon.

---

## Requirements

- **Apple Silicon Mac** (M1 or later) — the model runs on Apple's MLX/Metal backend.
- **macOS 13.5 or later.**
- **[uv](https://docs.astral.sh/uv/)** (Python toolchain + runner). Install it with:
  ```sh
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **~2 GB free disk** (dependencies + speech model) and an internet connection for the first run.

## Install

```sh
git clone <repository-url> handsfree
cd handsfree
uv sync                      # fetches CPython 3.12 + dependencies (incl. torch, ~1–2 GB)
./packaging/build_app.sh     # builds ~/Applications/Handsfree.app
open ~/Applications/Handsfree.app
```

> **You build the app on your own machine — there's no prebuilt download.** The bundle is created
> in *alias mode*: it references your local clone instead of copying the (large) dependencies in,
> so a `Handsfree.app` from one Mac won't run on another. Everyone clones and runs
> `build_app.sh`. (It's quick — it doesn't re-bundle torch/mlx.)

On first launch the speech model (`whisper-large-v3-turbo-q4`, ~0.46 GB) downloads automatically,
then macOS prompts for permissions.

## Grant permissions (one-time)

Handsfree needs to watch a global hotkey and paste text, so macOS requires two permissions.
Open **System Settings → Privacy & Security** and enable **Handsfree** under **both**:

- **Accessibility** — to paste (synthesize ⌘V) and run the global hotkey listener.
- **Input Monitoring** — for the push-to-talk key.

If `Handsfree` isn't listed, click **+** and choose `~/Applications/Handsfree.app`.
**Microphone** is requested separately the first time you dictate — allow it.

⚠️ **Permissions only take effect on a fresh launch.** After enabling them, quit Handsfree
(**Quit Handsfree** in the menu) and reopen it:

```sh
open ~/Applications/Handsfree.app
```

## Usage

Hold **Right Command**, speak, then release — the transcription is pasted at the cursor.

A **🎙 menu bar icon** lets you switch language live (**English / 한국어 / 日本語**); the choice
applies to the next utterance and the icon shows the active code (e.g. `🎙 KO`). **Quit Handsfree**
is in the same menu.

## Configuration (environment variables)

| Variable | Default | Notes |
|---|---|---|
| `HANDSFREE_PTT_KEY` | `cmd_r` | Push-to-talk key: `cmd_r`, `cmd_l`, `alt_r`, `ctrl_r`, `f8`, `f9` |
| `HANDSFREE_MODEL` | `mlx-community/whisper-large-v3-turbo-q4` | Any MLX Whisper repo, e.g. `…/whisper-large-v3-turbo` for higher accuracy |
| `HANDSFREE_LANGUAGE` | `en` | Startup language: `en`, `ko`, or `ja` |

## Troubleshooting

- **No 🎙 in the menu bar?** On MacBooks with a notch, extra menu bar icons hide *behind* the
  notch when the bar is crowded. Quit a few other menu bar apps (or use an icon manager) to reveal it.
- **Holding the key does nothing / nothing pastes.** The permissions above aren't granted to
  **Handsfree**, or they were granted before the last (re)build. Re-enable Handsfree under
  Accessibility + Input Monitoring and **relaunch**. If a stale entry refuses to work, reset it:
  ```sh
  tccutil reset Accessibility com.handsfree.dictation
  tccutil reset ListenEvent  com.handsfree.dictation
  ```
  then re-grant.
- **Want to see logs / errors.** Run the bundle's binary in the foreground:
  ```sh
  ~/Applications/Handsfree.app/Contents/MacOS/Handsfree   # Ctrl-C to stop
  ```
- **Quick test without building the app:** `uv run handsfree` — but note this dictates into the
  *launching terminal only* (macOS scopes the hotkey to the process unless it has the app's stable,
  signed identity). Use it for a fast check before granting the app permissions.

## How it works

| Stage | What |
|---|---|
| Trigger | Global push-to-talk hotkey via `pynput` |
| Capture | Mic → 16 kHz mono buffer via `sounddevice` |
| Transcribe | Local MLX Whisper (`mlx-whisper`), Metal-accelerated |
| Inject | Set clipboard (`NSPasteboard`) → ⌘V → restore previous clipboard |
| UI | Menu bar language picker via `rumps` |

The `.app` is a [py2app](https://py2app.readthedocs.io/) **alias** bundle: a tiny signed stub
runs Python in-process so the app has its own identity (it shows as **Handsfree** in Privacy
settings, and the grant survives Python/uv updates). Rebuild with `./packaging/build_app.sh`
after changing the bundle id, `Info.plist`, or Python version — day-to-day code edits run live
without a rebuild.
