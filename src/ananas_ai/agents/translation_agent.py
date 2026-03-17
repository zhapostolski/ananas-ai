"""Translation Agent — translates agent outputs and user content between
English, Serbian, and Macedonian.

This agent does not call external AI models for translation. It uses the
platform's translation module (deep-translator / Google Translate) and
wraps the result in a structured output compatible with the agent pipeline.

Typical uses:
  - Translate the daily cross-channel brief to MK or SR for Teams posting
  - Translate a user question from MK/SR to EN before sending to the LLM
  - Produce bilingual output (EN + MK/SR side-by-side)
"""

from __future__ import annotations

from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.translation import (
    Language,
    detect_language,
    is_supported,
    language_label,
    translate,
    translate_report,
)


class TranslationAgent(BaseAgent):
    """Specialist agent for EN / SR / MK translation."""

    name = "translation-agent"
    module_name = "translation"
    output_type = "translation"

    def __init__(self) -> None:
        super().__init__(
            name="translation-agent",
            module_name="translation",
            output_type="translation",
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def translate_text(
        self,
        text: str,
        target: str,
        source: str | None = None,
    ) -> dict[str, Any]:
        """Translate a single text block.

        Args:
            text:   Input text.
            target: Target language ('en', 'sr', 'mk').
            source: Source language (auto-detected if None).

        Returns:
            Dict with keys: original, translated, source_lang, target_lang,
            source_label, target_label, char_count.
        """
        if not is_supported(target):
            return self._error(f"Unsupported target language: {target}")

        detected_source: Language = (
            source if (source and is_supported(source)) else detect_language(text)  # type: ignore[assignment]
        )
        translated = translate(text, target, detected_source)  # type: ignore[arg-type]

        return {
            "status": "ok",
            "original": text,
            "translated": translated,
            "source_lang": detected_source,
            "target_lang": target,
            "source_label": language_label(detected_source),
            "target_label": language_label(target),
            "char_count": len(text),
        }

    def translate_report_output(
        self,
        report: str,
        target: str,
    ) -> dict[str, Any]:
        """Translate a multi-paragraph agent report to target language.

        Preserves paragraph structure. Returns both original and translated.
        """
        if not is_supported(target):
            return self._error(f"Unsupported target language: {target}")

        translated = translate_report(report, target)  # type: ignore[arg-type]
        return {
            "status": "ok",
            "original": report,
            "translated": translated,
            "target_lang": target,
            "target_label": language_label(target),
            "paragraphs": len([p for p in report.split("\n\n") if p.strip()]),
        }

    def bilingual_report(
        self,
        report: str,
        secondary: str,
    ) -> dict[str, Any]:
        """Produce a bilingual report (English + secondary language).

        Returns side-by-side sections: EN first, then translated version.
        """
        if not is_supported(secondary):
            return self._error(f"Unsupported secondary language: {secondary}")

        translated = translate_report(report, secondary)  # type: ignore[arg-type]
        label = language_label(secondary)
        combined = f"--- English ---\n\n{report}\n\n--- {label} ---\n\n{translated}"
        return {
            "status": "ok",
            "combined": combined,
            "english": report,
            "translated": translated,
            "secondary_lang": secondary,
            "secondary_label": label,
        }

    def detect(self, text: str) -> dict[str, Any]:
        """Detect the language of a text string."""
        lang = detect_language(text)
        return {
            "status": "ok",
            "detected": lang,
            "label": language_label(lang),
            "text_preview": text[:80] + ("..." if len(text) > 80 else ""),
        }

    def supported_languages(self) -> dict[str, Any]:
        """Return list of supported languages."""
        return {
            "status": "ok",
            "languages": [
                {"code": "en", "label": "English", "native": "English"},
                {"code": "sr", "label": "Serbian", "native": "Srpski"},
                {"code": "mk", "label": "Macedonian", "native": "Македонски"},
            ],
        }

    # ------------------------------------------------------------------
    # BaseAgent interface
    # ------------------------------------------------------------------

    def run(self, date_from: str, date_to: str) -> dict[str, Any]:  # noqa: ARG002
        return {
            "agent": self.name,
            "status": "ready",
            "supported_languages": self.supported_languages()["languages"],
            "note": "Translation agent is on-demand — call translate_text() or translate_report_output() directly.",
        }

    def sample_summary(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "en_sample": "Marketing performance summary for today.",
            "sr_sample": translate("Marketing performance summary for today.", "sr", "en"),
            "mk_sample": translate("Marketing performance summary for today.", "mk", "en"),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _error(message: str) -> dict[str, Any]:
        return {"status": "error", "message": message}
