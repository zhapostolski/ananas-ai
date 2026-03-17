"use client";

import { useState } from "react";
import { Globe } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import type { Language } from "@/lib/i18n";

const OPTIONS: { code: Language; label: string; native: string }[] = [
  { code: "en", label: "English", native: "EN" },
  { code: "sr", label: "Srpski", native: "SR" },
  { code: "mk", label: "Македонски", native: "MK" },
];

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();
  const [open, setOpen] = useState(false);

  const current = OPTIONS.find((o) => o.code === language) ?? OPTIONS[0];

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex h-8 items-center gap-1.5 rounded-lg px-2 hover:bg-accent transition-colors text-muted-foreground hover:text-foreground text-xs font-medium"
        title="Switch language"
        aria-label="Switch language"
      >
        <Globe className="h-3.5 w-3.5" />
        <span>{current.native}</span>
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full z-50 mt-1 w-36 rounded-xl border bg-white dark:bg-gray-900 shadow-xl py-1">
            {OPTIONS.map((opt) => (
              <button
                key={opt.code}
                onClick={() => {
                  setLanguage(opt.code);
                  setOpen(false);
                }}
                className={`flex w-full items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-accent ${
                  language === opt.code ? "font-semibold text-foreground" : "text-muted-foreground"
                }`}
              >
                <span
                  className="w-6 text-center text-xs font-bold rounded"
                  style={
                    language === opt.code
                      ? { color: "#FE5000" }
                      : {}
                  }
                >
                  {opt.native}
                </span>
                <span>{opt.label}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
