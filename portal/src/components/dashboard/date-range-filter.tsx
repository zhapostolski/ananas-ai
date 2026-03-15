"use client";

import { useState } from "react";
import { Calendar, ChevronDown } from "lucide-react";

export type DatePreset =
  | "today"
  | "yesterday"
  | "last_7d"
  | "last_30d"
  | "mtd"
  | "last_month"
  | "qtd"
  | "ytd"
  | "custom";

export interface DateRange {
  preset: DatePreset;
  from?: string; // ISO date string YYYY-MM-DD (for custom)
  to?: string;
}

const PRESETS: Array<{ value: DatePreset; label: string }> = [
  { value: "today", label: "Today" },
  { value: "yesterday", label: "Yesterday" },
  { value: "last_7d", label: "Last 7 Days" },
  { value: "last_30d", label: "Last 30 Days" },
  { value: "mtd", label: "This Month" },
  { value: "last_month", label: "Last Month" },
  { value: "qtd", label: "This Quarter" },
  { value: "ytd", label: "Year to Date" },
  { value: "custom", label: "Custom Range" },
];

function presetLabel(range: DateRange): string {
  if (range.preset === "custom" && range.from && range.to) {
    return `${range.from} — ${range.to}`;
  }
  return PRESETS.find((p) => p.value === range.preset)?.label ?? range.preset;
}

interface DateRangeFilterProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
}

export function DateRangeFilter({ value, onChange }: DateRangeFilterProps) {
  const [open, setOpen] = useState(false);
  const [customFrom, setCustomFrom] = useState(value.from ?? "");
  const [customTo, setCustomTo] = useState(value.to ?? "");

  function selectPreset(preset: DatePreset) {
    if (preset !== "custom") {
      onChange({ preset });
      setOpen(false);
    } else {
      onChange({ preset: "custom", from: customFrom, to: customTo });
    }
  }

  function applyCustom() {
    if (customFrom && customTo) {
      onChange({ preset: "custom", from: customFrom, to: customTo });
      setOpen(false);
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded-lg border bg-background px-3 py-1.5 text-sm hover:bg-accent transition-colors"
      >
        <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="font-medium">{presetLabel(value)}</span>
        <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full z-50 mt-2 w-52 rounded-xl border bg-white dark:bg-gray-900 shadow-xl">
            <div className="py-1">
              {PRESETS.filter((p) => p.value !== "custom").map((p) => (
                <button
                  key={p.value}
                  onClick={() => selectPreset(p.value)}
                  className={`flex w-full items-center px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${
                    value.preset === p.value
                      ? "font-semibold text-orange-600"
                      : ""
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Custom range */}
            <div className="border-t px-4 py-3 space-y-2">
              <p className="text-xs font-medium text-muted-foreground">Custom Range</p>
              <div className="flex flex-col gap-1.5">
                <input
                  type="date"
                  value={customFrom}
                  onChange={(e) => setCustomFrom(e.target.value)}
                  className="rounded-md border bg-background px-2 py-1 text-xs focus:outline-none w-full"
                />
                <input
                  type="date"
                  value={customTo}
                  onChange={(e) => setCustomTo(e.target.value)}
                  className="rounded-md border bg-background px-2 py-1 text-xs focus:outline-none w-full"
                />
                <button
                  onClick={applyCustom}
                  disabled={!customFrom || !customTo}
                  className="mt-1 rounded-md px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-40"
                  style={{ backgroundColor: "#FE5000" }}
                >
                  Apply
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

/** Utility: convert a DateRange preset to { from, to } Date objects */
export function resolveDateRange(range: DateRange): { from: Date; to: Date } {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  switch (range.preset) {
    case "today":
      return { from: today, to: today };
    case "yesterday":
      return { from: yesterday, to: yesterday };
    case "last_7d": {
      const from = new Date(today);
      from.setDate(today.getDate() - 6);
      return { from, to: today };
    }
    case "last_30d": {
      const from = new Date(today);
      from.setDate(today.getDate() - 29);
      return { from, to: today };
    }
    case "mtd": {
      const from = new Date(today.getFullYear(), today.getMonth(), 1);
      return { from, to: today };
    }
    case "last_month": {
      const from = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      const to = new Date(today.getFullYear(), today.getMonth(), 0);
      return { from, to };
    }
    case "qtd": {
      const q = Math.floor(today.getMonth() / 3);
      const from = new Date(today.getFullYear(), q * 3, 1);
      return { from, to: today };
    }
    case "ytd": {
      const from = new Date(today.getFullYear(), 0, 1);
      return { from, to: today };
    }
    case "custom": {
      const from = range.from ? new Date(range.from) : today;
      const to = range.to ? new Date(range.to) : today;
      return { from, to };
    }
  }
}
