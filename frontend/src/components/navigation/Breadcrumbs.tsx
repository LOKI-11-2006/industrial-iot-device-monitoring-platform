import { ChevronRight } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

import { findRouteMetadata, routeRegistry } from "@/routes/route-registry";

export function Breadcrumbs() {
  const { pathname } = useLocation();
  const currentRoute = findRouteMetadata(pathname);

  if (!currentRoute?.parentPath) {
    return null;
  }

  const parentRoute = routeRegistry.find((route) => route.path === currentRoute.parentPath);
  if (!parentRoute) {
    return null;
  }

  return (
    <nav aria-label="Breadcrumb" className="mb-4">
      <ol className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <li>
          <Link className="rounded-xs transition-colors hover:text-foreground" to={parentRoute.path}>
            {parentRoute.title}
          </Link>
        </li>
        <li aria-hidden="true"><ChevronRight className="size-3.5" /></li>
        <li className="font-medium text-foreground" aria-current="page">{currentRoute.title}</li>
      </ol>
    </nav>
  );
}
