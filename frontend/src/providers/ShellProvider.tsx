import { useMemo, useState, type PropsWithChildren } from "react";

import { ShellContext } from "@/contexts/shell-context";

const SIDEBAR_STORAGE_KEY = "forgesight.sidebar.collapsed";

function readStoredSidebarPreference() {
  return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === "true";
}

export function ShellProvider({ children }: PropsWithChildren) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(readStoredSidebarPreference);
  const [isMobileNavigationOpen, setIsMobileNavigationOpen] = useState(false);

  const value = useMemo(
    () => ({
      isSidebarCollapsed,
      isMobileNavigationOpen,
      closeMobileNavigation: () => setIsMobileNavigationOpen(false),
      openMobileNavigation: () => setIsMobileNavigationOpen(true),
      toggleSidebar: () => {
        setIsSidebarCollapsed((current) => {
          const next = !current;
          window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(next));
          return next;
        });
      },
    }),
    [isMobileNavigationOpen, isSidebarCollapsed],
  );

  return <ShellContext.Provider value={value}>{children}</ShellContext.Provider>;
}
