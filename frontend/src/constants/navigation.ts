import {
  Activity,
  Bell,
  ChartNoAxesCombined,
  Cog,
  Cpu,
  Factory,
  FileChartColumn,
  LayoutDashboard,
  ScrollText,
  Settings,
  ShieldCheck,
  SquareTerminal,
  TriangleAlert,
  UserCog,
  UsersRound,
} from "lucide-react";

import { paths } from "@/routes/paths";
import type { NavigationItem } from "@/types/navigation";
import { ALL_USER_ROLES, USER_ROLES } from "@/types/user-role";

const operationalRoles = [
  USER_ROLES.superAdministrator,
  USER_ROLES.factoryAdministrator,
  USER_ROLES.factoryManager,
  USER_ROLES.maintenanceEngineer,
  USER_ROLES.operator,
] as const;

export const navigationItems: readonly NavigationItem[] = [
  { label: "Dashboard", path: paths.dashboard, icon: LayoutDashboard, group: "operations", allowedRoles: ALL_USER_ROLES },
  { label: "Factories", path: paths.factories, icon: Factory, group: "operations", allowedRoles: ALL_USER_ROLES },
  { label: "Machines", path: paths.machines, icon: Cog, group: "operations", allowedRoles: ALL_USER_ROLES },
  { label: "Devices", path: paths.devices, icon: Cpu, group: "operations", allowedRoles: ALL_USER_ROLES },
  { label: "Live monitoring", path: paths.liveMonitoring, icon: Activity, group: "operations", allowedRoles: ALL_USER_ROLES },
  { label: "Analytics", path: paths.analytics, icon: ChartNoAxesCombined, group: "insight", allowedRoles: ALL_USER_ROLES },
  { label: "Alerts", path: paths.alerts, icon: TriangleAlert, group: "insight", allowedRoles: ALL_USER_ROLES, badgeKey: "alerts" },
  { label: "Reports", path: paths.reports, icon: FileChartColumn, group: "insight", allowedRoles: ALL_USER_ROLES },
  { label: "Audit logs", path: paths.auditLogs, icon: ScrollText, group: "governance", allowedRoles: operationalRoles },
  { label: "Device logs", path: paths.deviceLogs, icon: SquareTerminal, group: "governance", allowedRoles: operationalRoles },
  { label: "Security center", path: paths.securityCenter, icon: ShieldCheck, group: "governance", allowedRoles: operationalRoles },
  {
    label: "Users",
    path: paths.users,
    icon: UsersRound,
    group: "governance",
    allowedRoles: [USER_ROLES.superAdministrator, USER_ROLES.factoryAdministrator, USER_ROLES.factoryManager],
  },
  {
    label: "Roles",
    path: paths.roles,
    icon: UserCog,
    group: "governance",
    allowedRoles: [USER_ROLES.superAdministrator, USER_ROLES.factoryAdministrator],
  },
  { label: "Settings", path: paths.settings, icon: Settings, group: "governance", allowedRoles: ALL_USER_ROLES },
  {
    label: "Notifications",
    path: paths.notifications,
    icon: Bell,
    group: "insight",
    allowedRoles: ALL_USER_ROLES,
    badgeKey: "notifications",
  },
] as const;

export const navigationGroupLabels = Object.freeze({
  operations: "Operations",
  insight: "Insight and response",
  governance: "Governance",
});
