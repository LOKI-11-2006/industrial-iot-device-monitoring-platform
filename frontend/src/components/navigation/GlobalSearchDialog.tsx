import { ArrowRight, Search } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { navigationItems } from "@/constants/navigation";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useKeyboardShortcut } from "@/hooks/use-keyboard-shortcut";
import type { UserRole } from "@/types/user-role";

interface GlobalSearchDialogProps {
  readonly isOpen: boolean;
  readonly onOpenChange: (isOpen: boolean) => void;
  readonly role: UserRole;
}

export function GlobalSearchDialog({ isOpen, onOpenChange, role }: GlobalSearchDialogProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const openSearch = useCallback(() => onOpenChange(true), [onOpenChange]);
  useKeyboardShortcut("k", openSearch);

  const results = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return navigationItems.filter(
      (item) =>
        item.allowedRoles.includes(role) &&
        (normalizedQuery.length === 0 || item.label.toLowerCase().includes(normalizedQuery)),
    );
  }, [query, role]);

  const chooseResult = (path: string) => {
    void navigate(path);
    onOpenChange(false);
    setQuery("");
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="top-[12vh] max-w-2xl translate-y-0 gap-0 overflow-hidden p-0 sm:top-[18vh]">
        <DialogHeader className="sr-only">
          <DialogTitle>Global search</DialogTitle>
          <DialogDescription>Find an authorized module. Asset search is connected in its approved feature phase.</DialogDescription>
        </DialogHeader>
        <div className="flex min-h-14 items-center gap-3 border-b border-border px-4 pr-14">
          <Search className="size-5 shrink-0 text-muted-foreground" aria-hidden="true" />
          <label htmlFor="global-search" className="sr-only">Search authorized destinations</label>
          <input
            id="global-search"
            autoFocus
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search modules; device and alert search follows its feature phase"
            className="h-12 min-w-0 flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
          />
          <kbd className="hidden rounded-xs border border-border bg-muted px-2 py-1 font-mono text-[10px] text-muted-foreground sm:inline-flex">ESC</kbd>
        </div>
        <div className="scrollbar-subtle max-h-[52vh] overflow-y-auto p-2" role="listbox" aria-label="Search results">
          <p className="px-3 pb-2 pt-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Authorized destinations
          </p>
          {results.length > 0 ? (
            results.map(({ icon: Icon, label, path }) => (
              <button
                key={path}
                type="button"
                role="option"
                aria-selected="false"
                onClick={() => chooseResult(path)}
                className="flex min-h-12 w-full items-center gap-3 rounded-sm px-3 text-left text-sm transition-colors hover:bg-accent focus-visible:bg-accent"
              >
                <span className="flex size-8 items-center justify-center rounded-sm border border-border bg-surface text-muted-foreground">
                  <Icon className="size-[18px]" aria-hidden="true" />
                </span>
                <span className="flex-1 font-medium">{label}</span>
                <ArrowRight className="size-4 text-muted-foreground" aria-hidden="true" />
              </button>
            ))
          ) : (
            <div className="px-3 py-10 text-center">
              <p className="text-sm font-medium">No authorized destination matches</p>
              <p className="mt-1 text-xs text-muted-foreground">Try a module name such as Devices or Alerts.</p>
            </div>
          )}
        </div>
        <div className="border-t border-border bg-surface/70 px-4 py-3 text-xs text-muted-foreground">
          Device, machine, alert, factory, and report records join this search in their approved feature phases.
        </div>
      </DialogContent>
    </Dialog>
  );
}
