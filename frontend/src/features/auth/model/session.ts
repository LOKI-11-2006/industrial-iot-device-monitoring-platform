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

export interface LoginCredentials {
  readonly email: string;
  readonly password: string;
  readonly rememberDevice: boolean;
}

export interface LoginResponse {
  readonly session: SessionSnapshot;
}

export interface PasswordResetRequest {
  readonly email: string;
}

export interface PasswordResetAccepted {
  readonly accepted: true;
}

export interface AuthServiceStatus {
  readonly status: "available" | "degraded";
}
