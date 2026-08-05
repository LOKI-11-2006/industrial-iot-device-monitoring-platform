import { describe, expect, it } from "vitest";

import { navigationItems } from "@/constants/navigation";
import { paths } from "@/routes/paths";
import { authenticationRoutes, findRouteMetadata, routeRegistry } from "@/routes/route-registry";
import { ALL_USER_ROLES, USER_ROLES } from "@/types/user-role";

const requiredPagePaths = [
  paths.login,
  paths.dashboard,
  paths.factories,
  paths.machines,
  paths.devices,
  paths.deviceDetails,
  paths.liveMonitoring,
  paths.analytics,
  paths.alerts,
  paths.alertDetails,
  paths.reports,
  paths.auditLogs,
  paths.deviceLogs,
  paths.notifications,
  paths.securityCenter,
  paths.users,
  paths.roles,
  paths.settings,
  paths.profile,
] as const;

describe("route registry", () => {
  it("registers every named frontend page before the 404 fallback", () => {
    const registeredPaths = new Set([...authenticationRoutes, ...routeRegistry].map((route) => route.path));
    expect(requiredPagePaths.every((path) => registeredPaths.has(path))).toBe(true);
  });

  it("matches dynamic device and alert routes", () => {
    expect(findRouteMetadata("/devices/dev_123")?.title).toBe("Device details");
    expect(findRouteMetadata("/alerts/alt_123")?.title).toBe("Alert details");
  });

  it("declares all six approved roles", () => {
    expect(ALL_USER_ROLES).toHaveLength(6);
  });

  it("keeps role administration limited to administrators", () => {
    const roleNavigation = navigationItems.find((item) => item.path === paths.roles);
    expect(roleNavigation?.allowedRoles).toEqual([
      USER_ROLES.superAdministrator,
      USER_ROLES.factoryAdministrator,
    ]);
  });
});
