import { Navigate, Outlet } from "react-router-dom";

import { AuthenticationLoadingCard } from "@/features/auth/components/AuthenticationLoadingCard";
import { useSessionQuery } from "@/features/auth/hooks/use-session-query";
import { paths } from "@/routes/paths";

export function PublicOnlyRoute() {
  const session = useSessionQuery();

  if (session.isPending) {
    return <AuthenticationLoadingCard />;
  }

  if (session.data) {
    return <Navigate to={paths.dashboard} replace />;
  }

  return <Outlet />;
}
