import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

const badgeVariants = cva(
  "inline-flex min-h-6 items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold leading-4",
  {
    variants: {
      variant: {
        neutral: "border-border bg-muted text-muted-foreground",
        primary: "border-primary/30 bg-primary/10 text-primary-hover",
        info: "border-info/30 bg-info/10 text-info",
        warning: "border-warning/30 bg-warning/10 text-warning",
        critical: "border-status-critical/30 bg-status-critical/10 text-status-critical",
      },
    },
    defaultVariants: {
      variant: "neutral",
    },
  },
);

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
