import { Skeleton } from "@/components/ui/skeleton";

export function AuthenticationLoadingCard() {
  return (
    <div className="rounded-lg border border-border bg-card p-7 shadow-dialog" role="status" aria-label="Restoring secure session">
      <span className="sr-only">Restoring secure session</span>
      <Skeleton className="h-3 w-24" />
      <Skeleton className="mt-4 h-8 w-48" />
      <Skeleton className="mt-3 h-4 w-full" />
      <Skeleton className="mt-8 h-11 w-full" />
      <Skeleton className="mt-5 h-11 w-full" />
      <Skeleton className="mt-6 h-11 w-full" />
    </div>
  );
}
