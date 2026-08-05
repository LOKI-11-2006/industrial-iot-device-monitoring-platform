import { matchPath } from "react-router-dom";

import { paths } from "@/routes/paths";
import { routeRegistry } from "@/routes/route-registry";
import type { UserRole } from "@/types/user-role";

export function resolveAuthorizedReturnPath(candidate: unknown, role: UserRole) {
  if (typeof candidate !== "string" || !candidate.startsWith("/") || candidate.startsWith("//")) {
    return paths.dashboard;
  }

  const route = routeRegistry.find((metadata) => matchPath({ path: metadata.path, end: true }, candidate));
  if (!route || !route.allowedRoles.includes(role)) {
    return paths.dashboard;
  }

  return candidate;
}
