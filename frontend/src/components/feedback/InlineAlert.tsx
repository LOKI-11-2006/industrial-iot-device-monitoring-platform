import { AlertCircle, CheckCircle2, Info, TriangleAlert, type LucideIcon } from "lucide-react";
import type { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

const alertStyles = {
  info: { icon: Info, className: "border-info/25 bg-info/10 text-info" },
  success: { icon: CheckCircle2, className: "border-success/25 bg-success/10 text-success" },
  warning: { icon: TriangleAlert, className: "border-warning/25 bg-warning/10 text-warning" },
  danger: { icon: AlertCircle, className: "border-destructive/25 bg-destructive/10 text-destructive" },
} satisfies Record<string, { icon: LucideIcon; className: string }>;

interface InlineAlertProps extends HTMLAttributes<HTMLDivElement> {
  readonly title: string;
  readonly variant?: keyof typeof alertStyles;
}

export function InlineAlert({ children, className, title, variant = "info", ...props }: InlineAlertProps) {
  const { icon: Icon, className: variantClassName } = alertStyles[variant];

  return (
    <div className={cn("flex gap-3 rounded-md border p-3.5", variantClassName, className)} {...props}>
      <Icon className="mt-0.5 size-[18px] shrink-0" aria-hidden="true" />
      <div className="min-w-0">
        <p className="text-xs font-semibold text-foreground">{title}</p>
        {children ? <div className="mt-1 text-xs leading-5 text-muted-foreground">{children}</div> : null}
      </div>
    </div>
  );
}
