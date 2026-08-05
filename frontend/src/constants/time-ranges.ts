export const TIME_RANGE_OPTIONS = [
  { value: "1h", label: "Last hour" },
  { value: "8h", label: "Current shift" },
  { value: "24h", label: "Last 24 hours" },
  { value: "7d", label: "Last 7 days" },
  { value: "30d", label: "Last 30 days" },
] as const;

export type TimeRange = (typeof TIME_RANGE_OPTIONS)[number]["value"];
