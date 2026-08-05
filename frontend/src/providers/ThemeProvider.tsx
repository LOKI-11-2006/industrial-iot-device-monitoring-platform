import { createContext, useCallback, useContext, useEffect, useMemo, useState, type PropsWithChildren } from "react";

export type ThemePreference = "dark" | "system";

interface ThemeContextValue {
  readonly preference: ThemePreference;
  readonly setPreference: (preference: ThemePreference) => void;
}

const THEME_STORAGE_KEY = "forgesight.theme.preference";
const ThemeContext = createContext<ThemeContextValue | null>(null);

function readThemePreference(): ThemePreference {
  return window.localStorage.getItem(THEME_STORAGE_KEY) === "system" ? "system" : "dark";
}

export function ThemeProvider({ children }: PropsWithChildren) {
  const [preference, setPreferenceState] = useState<ThemePreference>(readThemePreference);

  useEffect(() => {
    // The approved visual system currently defines a dark palette. The preference
    // value is retained so a future approved light palette can honor system mode.
    document.documentElement.dataset.theme = "dark";
    document.documentElement.dataset.themePreference = preference;
  }, [preference]);

  const setPreference = useCallback((nextPreference: ThemePreference) => {
    window.localStorage.setItem(THEME_STORAGE_KEY, nextPreference);
    setPreferenceState(nextPreference);
  }, []);

  const value = useMemo(() => ({ preference, setPreference }), [preference, setPreference]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error("useTheme must be used inside ThemeProvider.");
  }

  return context;
}
