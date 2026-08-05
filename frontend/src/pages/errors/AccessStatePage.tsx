import { ArrowLeft, LockKeyhole, ShieldX } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { paths } from "@/routes/paths";

export default function AccessStatePage() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isUnauthorized = pathname === paths.unauthorized;
  const Icon = isUnauthorized ? LockKeyhole : ShieldX;

  return (
    <section className="mx-auto grid min-h-[calc(100vh-12rem)] max-w-xl place-items-center py-8" aria-labelledby="access-state-title">
      <div className="w-full rounded-lg border border-border bg-card p-7 text-center shadow-subtle sm:p-9">
        <div className="mx-auto flex size-12 items-center justify-center rounded-md border border-warning/25 bg-warning/10 text-warning">
          <Icon className="size-6" aria-hidden="true" />
        </div>
        <p className="mt-6 text-xs font-semibold uppercase tracking-[0.16em] text-warning">
          {isUnauthorized ? "Session required" : "Access restricted"}
        </p>
        <h1 id="access-state-title" className="mt-2 text-2xl font-semibold tracking-tight">
          {isUnauthorized ? "Sign in to continue" : "This destination is outside your scope"}
        </h1>
        <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-muted-foreground">
          {isUnauthorized
            ? "A trusted session is required. Authentication is delivered in Frontend Phase 2."
            : "Your role or assigned factory scope does not permit this route. No protected data was requested."}
        </p>
        <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-center">
          <Button variant="secondary" onClick={() => navigate(-1)}><ArrowLeft aria-hidden="true" /> Go back</Button>
          <Button asChild><Link to={isUnauthorized ? paths.login : paths.dashboard}>{isUnauthorized ? "Go to sign in" : "Go to Dashboard"}</Link></Button>
        </div>
      </div>
    </section>
  );
}
