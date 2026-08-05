import { Bell, Check, ChevronDown, CircleHelp, Menu, MonitorCog, Moon, Search } from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { GlobalSearchDialog } from "@/components/navigation/GlobalSearchDialog";
import { TIME_RANGE_OPTIONS, type TimeRange } from "@/constants/time-ranges";
import { useSessionQuery } from "@/features/auth/hooks/use-session-query";
import { useShell } from "@/hooks/use-shell";
import { useTheme, type ThemePreference } from "@/providers/ThemeProvider";
import { paths } from "@/routes/paths";
import { findRouteMetadata } from "@/routes/route-registry";
import { ROLE_LABELS } from "@/types/user-role";

function initials(displayName: string) {
  return displayName
    .split(" ")
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export function AppNavbar() {
  const { pathname } = useLocation();
  const { openMobileNavigation } = useShell();
  const { preference, setPreference } = useTheme();
  const session = useSessionQuery();
  const route = findRouteMetadata(pathname);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [factoryScope, setFactoryScope] = useState("all");
  const [timeRange, setTimeRange] = useState<TimeRange>("24h");

  if (!session.data) {
    return null;
  }

  const { user } = session.data;
  const selectedTimeRange = TIME_RANGE_OPTIONS.find((option) => option.value === timeRange);
  const selectedFactory = user.factoryScopes.find((factory) => factory.id === factoryScope);

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-2 border-b border-border/70 bg-background/95 px-3 backdrop-blur md:h-16 md:px-5 xl:px-6">
      <Button variant="quiet" size="icon" className="lg:hidden" onClick={openMobileNavigation} aria-label="Open primary navigation">
        <Menu aria-hidden="true" />
      </Button>

      <div className="min-w-0 flex-1 lg:max-w-56">
        <p className="truncate text-sm font-semibold sm:text-base">{route?.title ?? "ForgeSight"}</p>
        <p className="hidden truncate text-[11px] text-muted-foreground sm:block">Industrial operations console</p>
      </div>

      <div className="hidden items-center gap-2 xl:flex">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="secondary" className="max-w-56 justify-between font-medium">
              <span className="truncate">{selectedFactory?.name ?? "All authorized factories"}</span>
              <ChevronDown aria-hidden="true" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-64">
            <DropdownMenuLabel>Factory scope</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem onSelect={() => setFactoryScope("all")}>
                <span className="flex-1">All authorized factories</span>
                {factoryScope === "all" ? <Check className="text-primary" aria-hidden="true" /> : null}
              </DropdownMenuItem>
              {user.factoryScopes.map((factory) => (
                <DropdownMenuItem key={factory.id} onSelect={() => setFactoryScope(factory.id)}>
                  <span className="flex-1">{factory.name}</span>
                  {factoryScope === factory.id ? <Check className="text-primary" aria-hidden="true" /> : null}
                </DropdownMenuItem>
              ))}
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="secondary" className="min-w-40 justify-between font-medium">
              {selectedTimeRange?.label}
              <ChevronDown aria-hidden="true" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>Time range · local timezone</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuRadioGroup value={timeRange} onValueChange={(value) => setTimeRange(value as TimeRange)}>
              {TIME_RANGE_OPTIONS.map((option) => (
                <DropdownMenuRadioItem key={option.value} value={option.value}>{option.label}</DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <button
        type="button"
        onClick={() => setIsSearchOpen(true)}
        className="hidden min-h-10 min-w-48 items-center gap-2 rounded-sm border border-border bg-card px-3 text-left text-[13px] text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring md:flex xl:min-w-60"
      >
        <Search className="size-[18px]" aria-hidden="true" />
        <span className="flex-1">Search</span>
        <kbd className="rounded-xs border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px]">Ctrl K</kbd>
      </button>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="quiet" size="icon" className="md:hidden" onClick={() => setIsSearchOpen(true)} aria-label="Open global search">
            <Search aria-hidden="true" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Search</TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button asChild variant="quiet" size="icon">
            <Link to={paths.notifications} aria-label="Open notifications"><Bell aria-hidden="true" /></Link>
          </Button>
        </TooltipTrigger>
        <TooltipContent>Notifications</TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="quiet" size="icon" aria-label="Open help and support"><CircleHelp aria-hidden="true" /></Button>
        </TooltipTrigger>
        <TooltipContent>Help and support</TooltipContent>
      </Tooltip>

      <DropdownMenu>
        <Tooltip>
          <TooltipTrigger asChild>
            <DropdownMenuTrigger asChild>
              <Button variant="quiet" size="icon" aria-label={`Theme preference: ${preference}`}>
                {preference === "dark" ? <Moon aria-hidden="true" /> : <MonitorCog aria-hidden="true" />}
              </Button>
            </DropdownMenuTrigger>
          </TooltipTrigger>
          <TooltipContent>Theme preference</TooltipContent>
        </Tooltip>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>Theme preference</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuRadioGroup value={preference} onValueChange={(value) => setPreference(value as ThemePreference)}>
            <DropdownMenuRadioItem value="dark">Dark</DropdownMenuRadioItem>
            <DropdownMenuRadioItem value="system">System</DropdownMenuRadioItem>
          </DropdownMenuRadioGroup>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="rounded-full focus-visible:ring-2 focus-visible:ring-ring" aria-label="Open profile menu">
          <Avatar><AvatarFallback>{initials(user.displayName)}</AvatarFallback></Avatar>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-64">
          <DropdownMenuLabel>
            <span className="block truncate text-sm text-foreground">{user.displayName}</span>
            <span className="mt-0.5 block truncate font-normal">{user.email}</span>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild><Link to={paths.profile}>Profile</Link></DropdownMenuItem>
          <DropdownMenuItem asChild><Link to={paths.settings}>Preferences</Link></DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuLabel>{ROLE_LABELS[user.role]}</DropdownMenuLabel>
          <DropdownMenuItem disabled>Sign out arrives in Frontend Phase 2</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <GlobalSearchDialog isOpen={isSearchOpen} onOpenChange={setIsSearchOpen} role={user.role} />
    </header>
  );
}
