import type {
  AuthServiceStatus,
  LoginCredentials,
  LoginResponse,
  PasswordResetAccepted,
  PasswordResetRequest,
  SessionSnapshot,
} from "@/features/auth/model/session";
import { AuthError } from "@/features/auth/model/auth-error";
import { USER_ROLES, type UserRole } from "@/types/user-role";

const PERSISTED_SESSION_KEY = "forgesight.mock.session.persisted";
const CURRENT_SESSION_KEY = "forgesight.mock.session.current";

const baseMockUser = {
  id: "usr_demo_authenticated",
  displayName: "Avery Chen",
  factoryScopes: [
    { id: "fac_demo_bengaluru", name: "Bengaluru Plant" },
    { id: "fac_demo_pune", name: "Pune Works" },
  ],
} as const;

function mockDelay() {
  if (import.meta.env.MODE === "test") {
    return Promise.resolve();
  }

  return new Promise<void>((resolve) => window.setTimeout(resolve, 650));
}

function roleForEmail(email: string): UserRole {
  const emailPrefix = email.split("@")[0]?.toLowerCase();
  const rolesByPrefix: Readonly<Record<string, UserRole>> = {
    viewer: USER_ROLES.viewer,
    operator: USER_ROLES.operator,
    engineer: USER_ROLES.maintenanceEngineer,
    manager: USER_ROLES.factoryManager,
    factoryadmin: USER_ROLES.factoryAdministrator,
    superadmin: USER_ROLES.superAdministrator,
  };

  return (emailPrefix && rolesByPrefix[emailPrefix]) || USER_ROLES.superAdministrator;
}

function buildMockSession(email: string): SessionSnapshot {
  return {
    user: {
      ...baseMockUser,
      email,
      role: roleForEmail(email),
    },
    expiresAt: new Date(Date.now() + 15 * 60_000).toISOString(),
  };
}

function saveMockSession(session: SessionSnapshot, rememberDevice: boolean) {
  clearMockSession();
  const storage = rememberDevice ? window.localStorage : window.sessionStorage;
  const key = rememberDevice ? PERSISTED_SESSION_KEY : CURRENT_SESSION_KEY;
  storage.setItem(key, JSON.stringify(session));
}

function readStoredSession(storage: Storage, key: string) {
  const stored = storage.getItem(key);
  if (!stored) {
    return null;
  }

  try {
    const session = JSON.parse(stored) as SessionSnapshot;
    if (Date.parse(session.expiresAt) <= Date.now()) {
      storage.removeItem(key);
      return null;
    }
    return session;
  } catch {
    storage.removeItem(key);
    return null;
  }
}

export function clearMockSession() {
  window.localStorage.removeItem(PERSISTED_SESSION_KEY);
  window.sessionStorage.removeItem(CURRENT_SESSION_KEY);
}

export async function getMockSession() {
  await mockDelay();
  return (
    readStoredSession(window.sessionStorage, CURRENT_SESSION_KEY) ??
    readStoredSession(window.localStorage, PERSISTED_SESSION_KEY)
  );
}

export async function loginWithMock(credentials: LoginCredentials): Promise<LoginResponse> {
  await mockDelay();
  const normalizedEmail = credentials.email.trim().toLowerCase();

  if (normalizedEmail === "network@forgesight.demo") {
    throw new AuthError("NETWORK_ERROR", "The authentication service could not be reached.");
  }
  if (normalizedEmail === "rate-limit@forgesight.demo") {
    throw new AuthError("RATE_LIMITED", "Too many sign-in attempts.", 45);
  }
  if (normalizedEmail === "locked@forgesight.demo") {
    throw new AuthError("ACCOUNT_LOCKED", "Sign-in is temporarily unavailable for this request.");
  }
  if (normalizedEmail === "invalid@forgesight.demo") {
    throw new AuthError("INVALID_CREDENTIALS", "Email or password is incorrect.");
  }

  const session = buildMockSession(normalizedEmail);
  saveMockSession(session, credentials.rememberDevice);
  return { session };
}

export async function logoutFromMock() {
  await mockDelay();
  clearMockSession();
}

export async function requestPasswordResetFromMock(
  request: PasswordResetRequest,
): Promise<PasswordResetAccepted> {
  await mockDelay();
  const normalizedEmail = request.email.trim().toLowerCase();

  if (normalizedEmail === "network@forgesight.demo") {
    throw new AuthError("NETWORK_ERROR", "The authentication service could not be reached.");
  }
  if (normalizedEmail === "rate-limit@forgesight.demo") {
    throw new AuthError("RATE_LIMITED", "Too many reset requests.", 60);
  }

  return { accepted: true };
}

export async function getMockAuthServiceStatus(): Promise<AuthServiceStatus> {
  await mockDelay();
  return { status: "available" };
}
