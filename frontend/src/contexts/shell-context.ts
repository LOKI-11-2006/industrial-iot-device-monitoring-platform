import { createContext } from "react";

export interface ShellContextValue {
  readonly isSidebarCollapsed: boolean;
  readonly isMobileNavigationOpen: boolean;
  readonly closeMobileNavigation: () => void;
  readonly openMobileNavigation: () => void;
  readonly toggleSidebar: () => void;
}

export const ShellContext = createContext<ShellContextValue | null>(null);
