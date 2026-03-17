"use client";

import { useState, useEffect, useRef } from "react";
import { useLanguage } from "./context";

/**
 * Translate dynamic content (agent output text) to the current portal language.
 * Returns the translated string and a loading flag.
 * If language is "en" or text is empty, returns text unchanged immediately.
 */
export function useTranslateContent(text: string | null | undefined): {
  translated: string;
  translating: boolean;
} {
  const { language } = useLanguage();
  const [translated, setTranslated] = useState(text ?? "");
  const [translating, setTranslating] = useState(false);
  const lastRef = useRef<string>("");

  useEffect(() => {
    const raw = text ?? "";
    const key = `${language}:${raw}`;

    if (!raw || language === "en") {
      setTranslated(raw);
      setTranslating(false);
      return;
    }

    if (key === lastRef.current) return;
    lastRef.current = key;

    setTranslating(true);
    fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: raw, target: language, source: "en" }),
    })
      .then((r) => r.json())
      .then((data: { translated?: string }) => {
        if (lastRef.current === key) {
          setTranslated(data.translated ?? raw);
          setTranslating(false);
        }
      })
      .catch(() => {
        if (lastRef.current === key) {
          setTranslated(raw);
          setTranslating(false);
        }
      });
  }, [text, language]);

  return { translated, translating };
}
