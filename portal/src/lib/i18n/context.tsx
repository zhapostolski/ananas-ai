"use client";

import { createContext, useContext, useEffect, useState } from "react";
import type { Language, Translations } from "./types";
import { en } from "./translations/en";
import { sr } from "./translations/sr";
import { mk } from "./translations/mk";

const TRANSLATIONS: Record<Language, Translations> = { en, sr, mk };
const STORAGE_KEY = "ananas_language";

interface LanguageContextValue {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextValue>({
  language: "en",
  setLanguage: () => {},
  t: en,
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");

  // Load persisted preference on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as Language | null;
      if (stored && (stored === "en" || stored === "sr" || stored === "mk")) {
        setLanguageState(stored);
      }
    } catch {
      // localStorage not available
    }
  }, []);

  function setLanguage(lang: Language) {
    setLanguageState(lang);
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      // ignore
    }
    // Persist to user preferences API (fire and forget)
    fetch("/api/user/preferences", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language: lang }),
    }).catch(() => {});
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t: TRANSLATIONS[language] }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}

// Hook for just the translation object (t)
export function useT() {
  return useContext(LanguageContext).t;
}
