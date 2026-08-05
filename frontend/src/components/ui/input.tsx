import { forwardRef, type InputHTMLAttributes } from "react";

import { cn } from "@/utils/cn";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  readonly hasError?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({ className, hasError = false, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "flex h-11 w-full rounded-sm border border-input bg-surface px-3.5 text-sm text-foreground shadow-sm transition-colors duration-control placeholder:text-muted-foreground hover:border-border focus-visible:border-ring focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/30 disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground",
      hasError && "border-destructive focus-visible:border-destructive focus-visible:ring-destructive/25",
      className,
    )}
    aria-invalid={hasError || undefined}
    {...props}
  />
));
Input.displayName = "Input";
