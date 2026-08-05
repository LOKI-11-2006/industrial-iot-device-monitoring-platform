import { CloudOff } from "lucide-react";

import { Button } from "@/components/ui/button";

interface SessionErrorScreenProps {
  readonly onRetry: () => void;
}

export function SessionErrorScreen({ onRetry }: SessionErrorScreenProps) {
  return (
    <main className="grid min-h-screen place-items-center bg-background px-4">
      <section className="w-full max-w-lg rounded-lg border border-border bg-card p-8 text-center shadow-dialog" aria-labelledby="session-error-title">
        <div className="mx-auto flex size-12 items-center justify-center rounded-md border border-info/25 bg-info/10 text-info">
          <CloudOff className="size-6" aria-hidden="true" />
        </div>
        <h1 id="session-error-title" className="mt-6 text-xl font-semibold">We could not restore your session</h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          The operations console has not loaded protected data. Check your connection and try again safely.
        </p>
        <Button className="mt-6" onClick={onRetry}>Retry session</Button>
      </section>
    </main>
  );
}
