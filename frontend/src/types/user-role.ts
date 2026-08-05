export const USER_ROLES = {
  superAdministrator: "SUPER_ADMINISTRATOR",
  factoryAdministrator: "FACTORY_ADMINISTRATOR",
  factoryManager: "FACTORY_MANAGER",
  maintenanceEngineer: "MAINTENANCE_ENGINEER",
  operator: "OPERATOR",
  viewer: "VIEWER",
} as const;

export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];

export const ALL_USER_ROLES: readonly UserRole[] = Object.values(USER_ROLES);

export const ROLE_LABELS: Record<UserRole, string> = {
  SUPER_ADMINISTRATOR: "Super Administrator",
  FACTORY_ADMINISTRATOR: "Factory Administrator",
  FACTORY_MANAGER: "Factory Manager",
  MAINTENANCE_ENGINEER: "Maintenance Engineer",
  OPERATOR: "Operator",
  VIEWER: "Viewer",
};
