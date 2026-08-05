import { ArrowRight, CheckCircle2, LockKeyhole } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { paths } from "@/routes/paths";
import { findRouteMetadata } from "@/routes/route-registry";

export default function AuthenticationPhaseBoundaryPage() {
  const { pathname } = useLocation();
  const route = findRouteMetadata(pathname);

  if (!route) {
    return null;
  }

  return (
    <section className="overflow-hidden rounded-lg border border-border bg-card shadow-dialog" aria-labelledby="auth-phase-title">
      <div className="border-b border-border/70 bg-gradient-to-br from-primary/10 via-card to-card p-6 sm:p-8">
        <div className="flex size-11 items-center justify-center rounded-md border border-primary/20 bg-primary/10 text-primary-hover">
          <LockKeyhole className="size-5" aria-hidden="true" />
        </div>
        <Badge variant="primary" className="mt-6">Route foundation ready</Badge>
        <h2 id="auth-phase-title" className="mt-4 text-2xl font-semibold tracking-tight">{route.title}</h2>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">{route.description}</p>
      </div>
      <div className="p-6 sm:p-8">
        <div className="flex items-start gap-3 rounded-md border border-border/70 bg-surface p-4">
          <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" aria-hidden="true" />
          <div>
            <p className="text-sm font-semibold">Authentication begins in Frontend Phase 2</p>
            <p className="mt-1 text-xs leading-5 text-muted-foreground">
              Routing, secure shell boundaries, theme, and validation dependencies are ready. No temporary form is presented as finished work.
            </p>
          </div>
        </div>
        <Button asChild variant="secondary" className="mt-5 w-full">
          <Link to={pathname === paths.login ? paths.forgotPassword : paths.login}>
            View the related route <ArrowRight aria-hidden="true" />
          </Link>
        </Button>
      </div>
    </section>
  );
}
