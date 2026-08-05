import { SearchX } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { paths } from "@/routes/paths";

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <main className="grid min-h-screen place-items-center bg-background px-4 py-10">
      <section className="w-full max-w-lg rounded-lg border border-border bg-card p-8 text-center shadow-dialog" aria-labelledby="not-found-title">
        <div className="mx-auto flex size-12 items-center justify-center rounded-md border border-border bg-surface text-muted-foreground">
          <SearchX className="size-6" aria-hidden="true" />
        </div>
        <p className="mt-6 text-xs font-semibold uppercase tracking-[0.18em] text-primary">Error 404</p>
        <h1 id="not-found-title" className="mt-2 text-2xl font-semibold tracking-tight">Page not found</h1>
        <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-muted-foreground">
          The destination may have moved or may not be available in your current scope.
        </p>
        <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-center">
          <Button variant="secondary" onClick={() => navigate(-1)}>Go back</Button>
          <Button asChild><Link to={paths.dashboard}>Go to Dashboard</Link></Button>
        </div>
      </section>
    </main>
  );
}
