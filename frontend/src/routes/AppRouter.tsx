import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { RouteLoadingScreen } from "@/components/feedback/RouteLoadingScreen";
import { ProtectedRoute } from "@/routes/ProtectedRoute";
import { paths } from "@/routes/paths";
import { authenticationRoutes, routeRegistry } from "@/routes/route-registry";

const AppShell = lazy(() => import("@/layouts/AppShell"));
const AuthLayout = lazy(() => import("@/layouts/AuthLayout"));
const PhaseBoundaryPage = lazy(() => import("@/pages/foundation/PhaseBoundaryPage"));
const AuthenticationPhaseBoundaryPage = lazy(() => import("@/pages/foundation/AuthenticationPhaseBoundaryPage"));
const AccessStatePage = lazy(() => import("@/pages/errors/AccessStatePage"));
const NotFoundPage = lazy(() => import("@/pages/errors/NotFoundPage"));

const featureRoutes = routeRegistry.filter(
  (route) => route.path !== paths.unauthorized && route.path !== paths.forbidden,
);

export function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<RouteLoadingScreen />}>
        <Routes>
          <Route element={<AuthLayout />}>
            {authenticationRoutes.map((route) => (
              <Route key={route.path} path={route.path} element={<AuthenticationPhaseBoundaryPage />} />
            ))}
            <Route path={paths.unauthorized} element={<AccessStatePage />} />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route element={<AppShell />}>
              {featureRoutes.map((route) => (
                <Route key={route.path} path={route.path} element={<PhaseBoundaryPage />} />
              ))}
              <Route path={paths.forbidden} element={<AccessStatePage />} />
            </Route>
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
