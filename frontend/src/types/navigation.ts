import type { LucideIcon } from "lucide-react";

import type { UserRole } from "@/types/user-role";

export type NavigationGroup = "operations" | "insight" | "governance";

export interface NavigationItem {
  readonly label: string;
  readonly path: string;
  readonly icon: LucideIcon;
  readonly group: NavigationGroup;
  readonly allowedRoles: readonly UserRole[];
  readonly badgeKey?: "alerts" | "notifications";
}

export interface RouteMetadata {
  readonly title: string;
  readonly description: string;
  readonly path: string;
  readonly phase: number;
  readonly allowedRoles: readonly UserRole[];
  readonly parentPath?: string;
}
