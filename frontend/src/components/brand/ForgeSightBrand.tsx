import { appConfig } from "@/config/env";
import { cn } from "@/utils/cn";

interface ForgeSightBrandProps {
  readonly compact?: boolean;
  readonly className?: string;
}

export function ForgeSightBrand({ compact = false, className }: ForgeSightBrandProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <img src="/assets/forgesight-mark.svg" alt="" className="size-9 shrink-0" />
      {!compact ? (
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold tracking-tight">{appConfig.appName}</p>
          <p className="truncate text-[11px] font-medium text-muted-foreground">Industrial IoT operations</p>
        </div>
      ) : null}
    </div>
  );
}
