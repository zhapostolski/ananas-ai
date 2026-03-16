"use client";

import { useState } from "react";
import { Calendar, ChevronDown } from "lucide-react";

export type DatePreset =
  | "today"
  | "yesterday"
  | "last_7d"
  | "last_week"
  | "mtd"
  | "last_month"
  | "last_30d"
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
  { value: "last_week", label: "Last Week" },
  { value: "mtd", label: "This Month" },
  { value: "last_month", label: "Last Month" },
  { value: "last_30d", label: "Last 30 Days" },
  { value: "qtd", label: "This Quarter" },
  { value: "ytd", label: "Year to Date" },
  { value: "custom", label: "Custom Range" },
];

function presetLabel(range: DateRange): string {
  if (range.preset === "custom" && range.from && range.to) {
    return `${range.from} - ${range.to}`;
  }
  return PRESETS.find((p) => p.value === range.preset)?.label ?? range.preset;
}

const QUICK_PRESETS: DatePreset[] = ["last_7d", "last_week", "mtd", "last_month"];

interface DateRangeFilterProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
}

export function DateRangeFilter({ value, onChange }: DateRangeFilterProps) {
  const [open, setOpen] = useState(false);
  const [customFrom, setCustomFrom] = useState(value.from ?? "");
  const [customTo, setCustomTo] = useState(value.to ?? "");

  function selectPreset(preset: DatePreset) {
    onChange({ preset });
    if (preset !== "custom") setOpen(false);
  }

  function applyCustom() {
    if (customFrom && customTo) {
      onChange({ preset: "custom", from: customFrom, to: customTo });
      setOpen(false);
    }
  }

  const activeLabel = presetLabel(value);

  return (
    <div className="relative flex items-center gap-1.5">
      {/* Quick preset chips */}
      {QUICK_PRESETS.map((p) => {
        const label = PRESETS.find((x) => x.value === p)?.label ?? p;
        const active = value.preset === p;
        return (
          <button
            key={p}
            onClick={() => selectPreset(p)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors border ${
              active
                ? "border-transparent text-white"
                : "border-border bg-background text-muted-foreground hover:text-foreground hover:border-foreground/30"
            }`}
            style={active ? { backgroundColor: "#FE5000", borderColor: "#FE5000" } : {}}
          >
            {label}
          </button>
        );
      })}

      {/* More options + custom range */}
      <div className="relative">
        <button
          onClick={() => setOpen((v) => !v)}
          className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-colors border ${
            !QUICK_PRESETS.includes(value.preset)
              ? "border-transparent text-white"
              : "border-border bg-background text-muted-foreground hover:text-foreground hover:border-foreground/30"
          }`}
          style={!QUICK_PRESETS.includes(value.preset) ? { backgroundColor: "#FE5000", borderColor: "#FE5000" } : {}}
        >
          <Calendar className="h-3 w-3" />
          {!QUICK_PRESETS.includes(value.preset) ? activeLabel : "More"}
          <ChevronDown className="h-3 w-3" />
        </button>

        {open && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
            <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-xl border bg-white dark:bg-gray-900 shadow-xl">
              <div className="py-1">
                {PRESETS.filter((p) => !QUICK_PRESETS.includes(p.value) && p.value !== "custom").map((p) => (
                  <button
                    key={p.value}
                    onClick={() => selectPreset(p.value)}
                    className={`flex w-full items-center px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${
                      value.preset === p.value ? "font-semibold text-orange-600" : ""
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
              <div className="border-t px-4 py-3 space-y-2">
                <p className="text-xs font-semibold text-muted-foreground">Custom Range</p>
                <div className="flex flex-col gap-1.5">
                  <div>
                    <p className="text-[10px] text-muted-foreground mb-0.5">From</p>
                    <input
                      type="date"
                      value={customFrom}
                      onChange={(e) => setCustomFrom(e.target.value)}
                      className="rounded-md border bg-background px-2 py-1 text-xs focus:outline-none w-full"
                    />
                  </div>
                  <div>
                    <p className="text-[10px] text-muted-foreground mb-0.5">To</p>
                    <input
                      type="date"
                      value={customTo}
                      onChange={(e) => setCustomTo(e.target.value)}
                      className="rounded-md border bg-background px-2 py-1 text-xs focus:outline-none w-full"
                    />
                  </div>
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
    case "last_week": {
      const dayOfWeek = today.getDay();
      const daysSinceThisMonday = (dayOfWeek + 6) % 7;
      const lastMonday = new Date(today);
      lastMonday.setDate(today.getDate() - daysSinceThisMonday - 7);
      const lastSunday = new Date(lastMonday);
      lastSunday.setDate(lastMonday.getDate() + 6);
      return { from: lastMonday, to: lastSunday };
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
