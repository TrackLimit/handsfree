"""macOS accessibility-permission helpers.

`pynput` only *checks* trust silently, so a freshly-built Handsfree.app never appears in
System Settings → Accessibility. Calling AXIsProcessTrustedWithOptions with the prompt
option makes macOS show the standard "control this computer" dialog AND register the app
(here, the responsible app — Handsfree.app) in the Accessibility list so it can be enabled.
"""

from __future__ import annotations


def request_accessibility(prompt: bool = True) -> bool:
    """Return whether this process may use the accessibility APIs.

    With prompt=True and trust not yet granted, macOS shows the permission dialog and
    adds the app to the Accessibility list. Returns True on non-macOS / if pyobjc is
    missing (nothing to gate on).
    """
    try:
        import ApplicationServices as A
    except Exception:  # noqa: BLE001 — not on macOS, or pyobjc absent
        return True
    if not prompt:
        return bool(A.AXIsProcessTrusted())
    options = {A.kAXTrustedCheckOptionPrompt: True}
    return bool(A.AXIsProcessTrustedWithOptions(options))
