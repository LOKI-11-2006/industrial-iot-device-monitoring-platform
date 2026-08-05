import { Skeleton } from "@/components/ui/skeleton";

export function RouteLoadingScreen() {
  return (
    <div className="min-h-screen bg-background p-4" role="status" aria-label="Loading ForgeSight">
      <span className="sr-only">Loading ForgeSight</span>
      <div className="flex min-h-[calc(100vh-2rem)] gap-4">
        <Skeleton className="hidden w-60 shrink-0 lg:block" />
        <div className="flex-1 space-y-4">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-32 w-full" />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }, (_, index) => <Skeleton key={index} className="h-28" />)}
          </div>
        </div>
      </div>
    </div>
  );
}
