import { QueryClientProvider } from "@tanstack/react-query";
import type { PropsWithChildren } from "react";
import { Toaster } from "sonner";

import { TooltipProvider } from "@/components/ui/tooltip";
import { queryClient } from "@/services/query-client";
import { ShellProvider } from "@/providers/ShellProvider";
import { ThemeProvider } from "@/providers/ThemeProvider";

export function AppProviders({ children }: PropsWithChildren) {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider delayDuration={450}>
          <ShellProvider>
            {children}
            <Toaster
              position="bottom-right"
              theme="dark"
              toastOptions={{
                classNames: {
                  toast: "!border-border !bg-elevated !text-foreground !shadow-popover",
                  description: "!text-muted-foreground",
                },
              }}
            />
          </ShellProvider>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
