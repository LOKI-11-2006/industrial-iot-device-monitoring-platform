import { Navigate, Outlet, useLocation } from "react-router-dom";

import { RouteLoadingScreen } from "@/components/feedback/RouteLoadingScreen";
import { SessionErrorScreen } from "@/components/feedback/SessionErrorScreen";
import { useSessionQuery } from "@/features/auth/hooks/use-session-query";
import { paths } from "@/routes/paths";
import { findRouteMetadata } from "@/routes/route-registry";

export function ProtectedRoute() {
  const location = useLocation();
  const session = useSessionQuery();

  if (session.isPending) {
    return <RouteLoadingScreen />;
  }

  if (session.isError) {
    return <SessionErrorScreen onRetry={() => void session.refetch()} />;
  }

  if (!session.data) {
    return <Navigate to={paths.unauthorized} replace state={{ from: location.pathname }} />;
  }

  const metadata = findRouteMetadata(location.pathname);
  if (metadata && !metadata.allowedRoles.includes(session.data.user.role)) {
    return <Navigate to={paths.forbidden} replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
