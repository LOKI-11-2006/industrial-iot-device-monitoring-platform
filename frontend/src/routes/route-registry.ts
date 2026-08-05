import { matchPath } from "react-router-dom";

import { paths } from "@/routes/paths";
import type { RouteMetadata } from "@/types/navigation";
import { ALL_USER_ROLES, USER_ROLES } from "@/types/user-role";

const adminRoles = [USER_ROLES.superAdministrator, USER_ROLES.factoryAdministrator] as const;
const operationalRoles = [
  USER_ROLES.superAdministrator,
  USER_ROLES.factoryAdministrator,
  USER_ROLES.factoryManager,
  USER_ROLES.maintenanceEngineer,
  USER_ROLES.operator,
] as const;

export const routeRegistry: readonly RouteMetadata[] = [
  {
    title: "Dashboard",
    description: "Authorized estate health, connectivity, risk, energy, and live operational context.",
    path: paths.dashboard,
    phase: 3,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Factories",
    description: "Find, compare, and govern factory sites within the active authorization scope.",
    path: paths.factories,
    phase: 4,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Machines",
    description: "Manage physical production assets, criticality, device attachment, and maintenance state.",
    path: paths.machines,
    phase: 4,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Devices",
    description: "Search and govern connected device identity, health, connectivity, and certificate posture.",
    path: paths.devices,
    phase: 4,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Device details",
    description: "Correlate device identity, live telemetry, health, alerts, certificates, logs, and maintenance.",
    path: paths.deviceDetails,
    phase: 4,
    parentPath: paths.devices,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Live monitoring",
    description: "Observe current device state with explicit freshness, quality, pause, and reconnect semantics.",
    path: paths.liveMonitoring,
    phase: 5,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Analytics",
    description: "Explore defensible environmental, energy, performance, fault, health, and connectivity patterns.",
    path: paths.analytics,
    phase: 5,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Alerts",
    description: "Triage, assign, acknowledge, investigate, and resolve operational exceptions.",
    path: paths.alerts,
    phase: 6,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Alert details",
    description: "Review complete condition evidence, ownership, response actions, and immutable history.",
    path: paths.alertDetails,
    phase: 6,
    parentPath: paths.alerts,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Reports",
    description: "Request, schedule, track, securely download, and audit bounded report artifacts.",
    path: paths.reports,
    phase: 6,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Audit logs",
    description: "Query immutable evidence of privileged and security-relevant actions.",
    path: paths.auditLogs,
    phase: 6,
    allowedRoles: operationalRoles,
  },
  {
    title: "Device logs",
    description: "Inspect authorized technical device events without exposing secrets or unsafe controls.",
    path: paths.deviceLogs,
    phase: 6,
    allowedRoles: operationalRoles,
  },
  {
    title: "Notifications",
    description: "Review the durable personal inbox for alerts, assignments, reports, and security events.",
    path: paths.notifications,
    phase: 6,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Security center",
    description: "Prioritize identity, certificate, device-trust, and access-control findings.",
    path: paths.securityCenter,
    phase: 6,
    allowedRoles: operationalRoles,
  },
  {
    title: "Users",
    description: "Govern human identities, roles, factory scopes, and active sessions within grantor bounds.",
    path: paths.users,
    phase: 6,
    allowedRoles: [...adminRoles, USER_ROLES.factoryManager],
  },
  {
    title: "Roles",
    description: "Inspect role capabilities and assignment boundaries for platform and factory administration.",
    path: paths.roles,
    phase: 6,
    allowedRoles: adminRoles,
  },
  {
    title: "Settings",
    description: "Configure personal, factory, and platform behavior within explicit policy inheritance.",
    path: paths.settings,
    phase: 6,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Profile",
    description: "Review personal identity and scope, preferences, active sessions, and security activity.",
    path: paths.profile,
    phase: 6,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Unauthorized",
    description: "A trusted session is required to access this destination.",
    path: paths.unauthorized,
    phase: 1,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Access restricted",
    description: "Your current role or factory scope does not permit this destination.",
    path: paths.forbidden,
    phase: 1,
    allowedRoles: ALL_USER_ROLES,
  },
] as const;

export const authenticationRoutes: readonly RouteMetadata[] = [
  {
    title: "Sign in",
    description: "Establish a trusted human session for the industrial operations console.",
    path: paths.login,
    phase: 2,
    allowedRoles: ALL_USER_ROLES,
  },
  {
    title: "Forgot password",
    description: "Request secure account recovery without disclosing account membership.",
    path: paths.forgotPassword,
    phase: 2,
    allowedRoles: ALL_USER_ROLES,
  },
] as const;

export function findRouteMetadata(pathname: string) {
  return [...authenticationRoutes, ...routeRegistry].find((route) =>
    matchPath({ path: route.path, end: true }, pathname),
  );
}
