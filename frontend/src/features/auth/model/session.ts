import type { UserRole } from "@/types/user-role";

export interface FactoryScope {
  readonly id: string;
  readonly name: string;
}

export interface SessionUser {
  readonly id: string;
  readonly displayName: string;
  readonly email: string;
  readonly role: UserRole;
  readonly factoryScopes: readonly FactoryScope[];
}

export interface SessionSnapshot {
  readonly user: SessionUser;
  readonly expiresAt: string;
}
