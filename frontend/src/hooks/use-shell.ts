import { useContext } from "react";

import { ShellContext } from "@/contexts/shell-context";

export function useShell() {
  const context = useContext(ShellContext);

  if (!context) {
    throw new Error("useShell must be used inside ShellProvider.");
  }

  return context;
}
