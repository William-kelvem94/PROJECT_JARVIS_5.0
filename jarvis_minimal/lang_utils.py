"""Utilities to detect device language and detect text language.

- Uses the system locale as the authoritative "device language".
- Optionally uses `langdetect` (se instalado) to detect language of incoming text.
- All functions are best-effort and fall back gracefully when libs are missing.
"""
import locale


def get_device_language() -> str:
    """Return a normalized language code for the device (e.g. 'pt' or 'en')."""
    try:
        loc = locale.getdefaultlocale()[0] or ""
        if not loc:
            return "pt"  # safe default: Portuguese (user preference)
        # examples: 'pt_BR', 'en_US'
        return loc.split("_")[0].lower()
    except Exception:
        return "pt"


def detect_language(text: str) -> str:
    """Detect language of `text`. Returns ISO 639-1 code (e.g. 'pt', 'en') or 'unknown'.

    - Uses `langdetect` if available.
    - For very short inputs (< 3 words) returns 'unknown' to avoid misclassification.
    """
    if not text:
        return "unknown"
    # avoid false positives on very short strings
    if len(text.split()) < 3:
        return "unknown"
    try:
        from langdetect import detect

        code = detect(text)
        return code.lower()
    except Exception:
        return "unknown"


def code_to_name(code: str) -> str:
    """Return a Portuguese language name for a short code."""
    mapping = {
        "pt": "Português",
        "pt-br": "Português (pt‑BR)",
        "en": "Inglês",
        "es": "Espanhol",
        "fr": "Francês",
    }
    if not code:
        return "Desconhecido"
    return mapping.get(code.lower(), code)
