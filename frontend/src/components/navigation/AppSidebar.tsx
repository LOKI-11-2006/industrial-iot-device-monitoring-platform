import { ChevronLeft, ChevronRight, HelpCircle, ShieldCheck } from "lucide-react";
import { Fragment } from "react";
import { NavLink, useLocation } from "react-router-dom";

import { ForgeSightBrand } from "@/components/brand/ForgeSightBrand";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { navigationGroupLabels, navigationItems } from "@/constants/navigation";
import { useSessionQuery } from "@/features/auth/hooks/use-session-query";
import { useShell } from "@/hooks/use-shell";
import { ROLE_LABELS } from "@/types/user-role";
import { cn } from "@/utils/cn";

interface SidebarContentProps {
  readonly collapsed: boolean;
  readonly onNavigate?: () => void;
}

function SidebarContent({ collapsed, onNavigate }: SidebarContentProps) {
  const { pathname } = useLocation();
  const session = useSessionQuery();

  if (session.isPending) {
    return (
      <div className="flex h-full flex-col gap-4 p-4" aria-label="Loading navigation">
        <Skeleton className="h-10 w-full" />
        {Array.from({ length: 9 }, (_, index) => <Skeleton key={index} className="h-10 w-full" />)}
      </div>
    );
  }

  if (!session.data) {
    return null;
  }

  const { user } = session.data;
  const authorizedItems = navigationItems.filter((item) => item.allowedRoles.includes(user.role));
  const groupedItems = (["operations", "insight", "governance"] as const).map((group) => ({
    group,
    items: authorizedItems.filter((item) => item.group === group && item.label !== "Notifications"),
  }));

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className={cn("flex h-16 shrink-0 items-center border-b border-border/70 px-4", collapsed && "justify-center px-0")}>
        <ForgeSightBrand compact={collapsed} />
      </div>

      <nav className="scrollbar-subtle flex-1 overflow-y-auto px-3 py-4" aria-label="Primary navigation">
        {groupedItems.map(({ group, items }) => (
          <Fragment key={group}>
            {!collapsed ? (
              <p className="mb-2 mt-5 px-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground first:mt-0">
                {navigationGroupLabels[group]}
              </p>
            ) : group !== "operations" ? (
              <div className="my-3 h-px bg-border/70" aria-hidden="true" />
            ) : null}
            <div className="space-y-1">
              {items.map(({ icon: Icon, label, path }) => {
                const active = path === "/" ? pathname === path : pathname.startsWith(path);
                const link = (
                  <NavLink
                    to={path}
                    onClick={onNavigate}
                    className={cn(
                      "relative flex min-h-10 items-center gap-3 rounded-sm px-3 text-[13px] font-medium text-muted-foreground transition-colors duration-control hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring",
                      active && "bg-primary/10 text-primary-hover before:absolute before:left-0 before:h-5 before:w-0.5 before:rounded-full before:bg-primary",
                      collapsed && "justify-center px-0",
                    )}
                    aria-current={active ? "page" : undefined}
                  >
                    <Icon className="size-5 shrink-0" strokeWidth={1.75} aria-hidden="true" />
                    {!collapsed ? <span className="truncate">{label}</span> : <span className="sr-only">{label}</span>}
                  </NavLink>
                );

                return collapsed ? (
                  <Tooltip key={path}>
                    <TooltipTrigger asChild>{link}</TooltipTrigger>
                    <TooltipContent side="right">{label}</TooltipContent>
                  </Tooltip>
                ) : (
                  <Fragment key={path}>{link}</Fragment>
                );
              })}
            </div>
          </Fragment>
        ))}
      </nav>

      <div className="shrink-0 border-t border-border/70 p-3">
        <div className={cn("mb-2 rounded-sm border border-border/70 bg-surface p-3", collapsed && "flex justify-center border-0 bg-transparent p-1")}>
          <div className="flex items-center gap-2 text-success">
            <ShieldCheck className="size-4 shrink-0" aria-hidden="true" />
            {!collapsed ? <span className="text-xs font-semibold">Protected session</span> : <span className="sr-only">Protected session</span>}
          </div>
          {!collapsed ? <p className="mt-1 truncate text-[11px] text-muted-foreground">{ROLE_LABELS[user.role]}</p> : null}
        </div>
        <Button variant="quiet" size={collapsed ? "icon" : "default"} className={cn("w-full", !collapsed && "justify-start px-3")}>
          <HelpCircle aria-hidden="true" />
          {!collapsed ? "Help and support" : <span className="sr-only">Help and support</span>}
        </Button>
      </div>
    </div>
  );
}

export function AppSidebar() {
  const { isSidebarCollapsed, isMobileNavigationOpen, closeMobileNavigation, toggleSidebar } = useShell();

  return (
    <>
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-nav hidden border-r border-border/70 bg-[#080D15] transition-[width] duration-panel lg:block",
          isSidebarCollapsed ? "w-[72px]" : "w-60",
        )}
      >
        <SidebarContent collapsed={isSidebarCollapsed} />
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="secondary"
              size="icon"
              onClick={toggleSidebar}
              className="absolute -right-5 top-[4.75rem] size-9 rounded-full bg-elevated shadow-popover"
              aria-label={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isSidebarCollapsed ? <ChevronRight aria-hidden="true" /> : <ChevronLeft aria-hidden="true" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">{isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}</TooltipContent>
        </Tooltip>
      </aside>

      <Dialog open={isMobileNavigationOpen} onOpenChange={(open) => !open && closeMobileNavigation()}>
        <DialogContent className="left-0 top-0 h-dvh w-[min(19rem,calc(100vw-2rem))] max-w-none translate-x-0 translate-y-0 gap-0 rounded-none border-y-0 border-l-0 bg-[#080D15] p-0 lg:hidden">
          <DialogHeader className="sr-only">
            <DialogTitle>Primary navigation</DialogTitle>
            <DialogDescription>Navigate between authorized ForgeSight modules.</DialogDescription>
          </DialogHeader>
          <SidebarContent collapsed={false} onNavigate={closeMobileNavigation} />
        </DialogContent>
      </Dialog>
    </>
  );
}
