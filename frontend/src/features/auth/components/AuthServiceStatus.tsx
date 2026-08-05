import { CircleAlert, CircleCheck, LoaderCircle } from "lucide-react";

import { useAuthServiceStatusQuery } from "@/features/auth/hooks/use-auth-mutations";

export function AuthServiceStatus() {
  const status = useAuthServiceStatusQuery();

  if (status.isPending) {
    return (
      <div className="flex items-center gap-2 text-[11px] text-muted-foreground" role="status">
        <LoaderCircle className="size-3.5 animate-spin motion-reduce:animate-none" aria-hidden="true" />
        Checking secure session service
      </div>
    );
  }

  if (status.isError || status.data.status === "degraded") {
    return (
      <div className="flex items-center gap-2 text-[11px] text-warning" role="status">
        <CircleAlert className="size-3.5" aria-hidden="true" />
        Session service may be delayed
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-[11px] text-success" role="status">
      <CircleCheck className="size-3.5" aria-hidden="true" />
      Secure session service available
    </div>
  );
}
