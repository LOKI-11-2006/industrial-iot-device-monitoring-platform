import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { RouteLoadingScreen } from "@/components/feedback/RouteLoadingScreen";
import { ProtectedRoute } from "@/routes/ProtectedRoute";
import { PublicOnlyRoute } from "@/routes/PublicOnlyRoute";
import { paths } from "@/routes/paths";
import { routeRegistry } from "@/routes/route-registry";

const AppShell = lazy(() => import("@/layouts/AppShell"));
const AuthLayout = lazy(() => import("@/layouts/AuthLayout"));
const PhaseBoundaryPage = lazy(() => import("@/pages/foundation/PhaseBoundaryPage"));
const LoginPage = lazy(() => import("@/pages/auth/LoginPage"));
const ForgotPasswordPage = lazy(() => import("@/pages/auth/ForgotPasswordPage"));
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
            <Route element={<PublicOnlyRoute />}>
              <Route path={paths.login} element={<LoginPage />} />
              <Route path={paths.forgotPassword} element={<ForgotPasswordPage />} />
            </Route>
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
