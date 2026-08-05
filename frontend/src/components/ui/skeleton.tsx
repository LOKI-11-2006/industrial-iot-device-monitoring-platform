import type { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

export function Skeleton({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-sm bg-muted motion-reduce:animate-none", className)}
      aria-hidden="true"
      {...props}
    />
  );
}
