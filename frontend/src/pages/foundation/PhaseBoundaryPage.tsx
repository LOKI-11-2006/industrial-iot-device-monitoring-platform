import { Boxes, CheckCircle2, FileLock2, Route } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { findRouteMetadata } from "@/routes/route-registry";
import { paths } from "@/routes/paths";

const foundationItems = [
  { icon: Route, label: "Route registered", detail: "Lazy-loaded and typed" },
  { icon: Boxes, label: "Shell integrated", detail: "Responsive and role-aware" },
  { icon: FileLock2, label: "Contract preserved", detail: "No premature feature data" },
] as const;

export default function PhaseBoundaryPage() {
  const { pathname } = useLocation();
  const route = findRouteMetadata(pathname);

  if (!route) {
    return null;
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-12rem)] max-w-5xl items-center py-8" aria-labelledby="phase-page-title">
      <div className="w-full overflow-hidden rounded-lg border border-border/80 bg-card shadow-subtle">
        <div className="border-b border-border/70 bg-gradient-to-br from-primary/10 via-card to-card px-6 py-8 sm:px-8 sm:py-10">
          <div className="mb-5 flex flex-wrap items-center gap-3">
            <Badge variant="primary">Route foundation ready</Badge>
            <Badge>Frontend phase {route.phase}</Badge>
          </div>
          <h1 id="phase-page-title" className="max-w-3xl text-balance text-2xl font-semibold tracking-tight sm:text-[32px] sm:leading-10">
            {route.title}
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground sm:text-base">
            {route.description}
          </p>
        </div>

        <div className="grid gap-4 p-6 sm:grid-cols-3 sm:p-8">
          {foundationItems.map(({ icon: Icon, label, detail }) => (
            <div key={label} className="rounded-md border border-border/70 bg-surface p-4">
              <div className="mb-4 flex size-9 items-center justify-center rounded-sm border border-primary/20 bg-primary/10 text-primary-hover">
                <Icon className="size-5" aria-hidden="true" />
              </div>
              <p className="text-sm font-semibold">{label}</p>
              <p className="mt-1 text-xs leading-5 text-muted-foreground">{detail}</p>
            </div>
          ))}
        </div>

        <div className="flex flex-col gap-4 border-t border-border/70 bg-surface/60 px-6 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" aria-hidden="true" />
            <div>
              <p className="text-sm font-medium">Protected by the delivery phase gate</p>
              <p className="mt-1 text-xs leading-5 text-muted-foreground">
                Feature UI and data behavior begin only in the approved phase shown above.
              </p>
            </div>
          </div>
          {pathname !== paths.dashboard ? (
            <Button asChild variant="secondary">
              <Link to={paths.dashboard}>Return to Dashboard</Link>
            </Button>
          ) : null}
        </div>
      </div>
    </section>
  );
}
