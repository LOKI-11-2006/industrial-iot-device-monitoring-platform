import { Outlet } from "react-router-dom";

import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import { AppNavbar } from "@/components/navigation/AppNavbar";
import { AppSidebar } from "@/components/navigation/AppSidebar";
import { useShell } from "@/hooks/use-shell";
import { cn } from "@/utils/cn";

export default function AppShell() {
  const { isSidebarCollapsed } = useShell();

  return (
    <div className="min-h-screen bg-background">
      <a
        href="#main-content"
        className="fixed left-4 top-3 z-[70] -translate-y-20 rounded-sm bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-transform focus:translate-y-0"
      >
        Skip to main content
      </a>
      <AppSidebar />
      <div
        className={cn(
          "min-w-0 transition-[padding] duration-panel lg:pl-60",
          isSidebarCollapsed && "lg:pl-[72px]",
        )}
      >
        <AppNavbar />
        <main id="main-content" tabIndex={-1} className="mx-auto w-full max-w-[1600px] px-3 py-5 sm:px-5 md:py-6 xl:px-6 2xl:px-8">
          <Breadcrumbs />
          <Outlet />
        </main>
      </div>
    </div>
  );
}
