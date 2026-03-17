"""Translation and language detection for the Ananas AI Platform.

Supports English (en), Serbian (sr), and Macedonian (mk).
Uses deep-translator (Google Translate free API) as the primary engine.
Language detection via langdetect.

Note: Serbian and Croatian/Bosnian share the same script and are mutually
intelligible — langdetect may return 'hr' or 'bs' for Serbian input.
All South-Slavic Cyrillic inputs are normalised to 'sr' for routing purposes.
"""

from __future__ import annotations

import functools
import logging
from typing import Literal

logger = logging.getLogger(__name__)

SUPPORTED = {"en", "sr", "mk"}
Language = Literal["en", "sr", "mk"]

# Terms that must never be translated or transliterated
_PRESERVED_TERMS = [
    "ROAS",
    "CAC",
    "LTV",
    "KPI",
    "CRM",
    "AOV",
    "CPC",
    "CPM",
    "CTR",
    "CVR",
    "GA4",
    "API",
    "SEO",
    "MKD",
    "ROI",
    "SLA",
    "OKR",
    "GMV",
    "SKU",
    "Ananas",
    "Google",
    "Meta",
    "Facebook",
    "Instagram",
    "TikTok",
    "LinkedIn",
    "Trustpilot",
    "Teams",
    "Jira",
    "Asana",
    "Confluence",
    "Sales Snap",
    "SharePoint",
    "Outlook",
]

# Codes that langdetect may return for Serbian/Croatian/Bosnian text
_SERBIAN_FAMILY = {"sr", "hr", "bs", "sh"}

# Google Translate codes
_GT_CODE: dict[str, str] = {
    "en": "en",
    "sr": "sr",
    "mk": "mk",
}

_LANG_LABELS: dict[str, str] = {
    "en": "English",
    "sr": "Serbian",
    "mk": "Macedonian",
}


def detect_language(text: str) -> Language:
    """Detect the language of a text string. Returns 'en', 'sr', or 'mk'.

    Falls back to 'en' if detection fails or returns an unsupported language.
    Serbian/Croatian/Bosnian family is normalised to 'sr'.
    """
    try:
        from langdetect import detect  # type: ignore[import-untyped]

        raw = detect(text)
        if raw == "mk":
            return "mk"
        if raw in _SERBIAN_FAMILY:
            return "sr"
        return "en"
    except Exception:
        logger.debug("Language detection failed, defaulting to 'en'")
        return "en"


def _protect_terms(text: str) -> tuple[str, dict[int, str]]:
    """Replace preserved terms with numeric tokens that survive Cyrillic translation."""
    tokens: dict[int, str] = {}
    result = text
    for term in _PRESERVED_TERMS:
        if term in result:
            idx = len(tokens)
            # Purely numeric token in brackets — Google Translate never touches digits
            tokens[idx] = term
            result = result.replace(term, f"[{idx}]")
    return result, tokens


def _restore_terms(text: str, tokens: dict[int, str]) -> str:
    """Restore preserved terms from numeric tokens after translation."""
    result = text
    for idx, term in tokens.items():
        result = result.replace(f"[{idx}]", term)
    return result


@functools.lru_cache(maxsize=512)
def translate(text: str, target: Language, source: Language | None = None) -> str:
    """Translate text to the target language.

    Args:
        text:   Input text to translate.
        target: Target language code ('en', 'sr', 'mk').
        source: Source language code. Auto-detected if None.

    Returns:
        Translated text string, or the original if translation fails.
    """
    if not text or not text.strip():
        return text

    if source is None:
        source = detect_language(text)

    if source == target:
        return text

    try:
        from deep_translator import GoogleTranslator  # type: ignore[import-untyped]

        protected, tokens = _protect_terms(text)
        raw_result = GoogleTranslator(
            source=_GT_CODE[source],
            target=_GT_CODE[target],
        ).translate(protected)
        result = _restore_terms(raw_result or text, tokens)
        return result
    except Exception as exc:
        logger.warning("Translation failed (%s -> %s): %s", source, target, exc)
        return text


def translate_auto(text: str, target: Language) -> str:
    """Translate text to target language with automatic source detection.

    Convenience wrapper around translate() that always auto-detects source.
    Does not cache (source detection is non-deterministic for short strings).
    """
    source = detect_language(text)
    if source == target:
        return text
    return translate(text, target, source)


def translate_report(report: str, target: Language) -> str:
    """Translate a multi-paragraph agent report to the target language.

    Splits by double newline to translate paragraph-by-paragraph, which
    preserves structure better than sending the full block in one request.
    """
    if target == "en":
        return report

    paragraphs = report.split("\n\n")
    translated = []
    for para in paragraphs:
        if para.strip():
            translated.append(translate_auto(para.strip(), target))
        else:
            translated.append("")
    return "\n\n".join(translated)


def language_label(code: str) -> str:
    """Return the human-readable label for a language code."""
    return _LANG_LABELS.get(code, code.upper())


def is_supported(code: str) -> bool:
    """Return True if the language code is supported."""
    return code in SUPPORTED
