"""py2app build config for Handsfree.app.

Built in ALIAS mode (`py2app -A`): py2app produces a real .app whose main executable is
an in-process Python stub (so NSBundle.mainBundle and macOS TCC both resolve to Handsfree.app,
not the interpreter), while *referencing* the existing venv instead of copying torch/mlx in.
The app therefore stays tiny and shows up as "Handsfree" in Privacy settings.

Build via packaging/build_app.sh (which runs this under the project's venv python).
"""

import os

from setuptools import setup

# Absolute so the build can run from a scratch CWD (avoids setuptools reading the
# project's pyproject.toml [project].dependencies, which py2app rejects).
_PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = [os.path.join(_PROJECT, "handsfree", "__main__.py")]

OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "Handsfree",
        "CFBundleDisplayName": "Handsfree",
        "CFBundleIdentifier": "com.handsfree.dictation",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "LSUIElement": True,  # menu-bar agent, no Dock icon
        "NSMicrophoneUsageDescription": (
            "Handsfree transcribes your speech locally for push-to-talk dictation."
        ),
    },
}

setup(
    name="Handsfree",
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
