import { accessTokenStore } from "@/api/access-token";
import { apiRequest, ApiClientError } from "@/api/client";
import { appConfig } from "@/config/env";
import {
  getMockAuthServiceStatus,
  getMockSession,
  loginWithMock,
  logoutFromMock,
  requestPasswordResetFromMock,
} from "@/features/auth/services/mock-auth-api";
import type {
  AuthServiceStatus,
  LoginCredentials,
  LoginResponse,
  PasswordResetAccepted,
  PasswordResetRequest,
  SessionSnapshot,
  SessionUser,
} from "@/features/auth/model/session";
import type { UserRole } from "@/types/user-role";

interface AccessTokenResponse {
  readonly accessToken: string;
  readonly expiresIn: number;
}

interface CurrentUserApiResponse {
  readonly id: string;
  readonly displayName?: string;
  readonly name?: string;
  readonly email?: string;
  readonly role: UserRole;
  readonly factoryScopes?: SessionUser["factoryScopes"];
  readonly factoryIds?: readonly string[];
}

function normalizeSessionUser(user: CurrentUserApiResponse, fallbackEmail = ""): SessionUser {
  const email = user.email ?? fallbackEmail;
  return {
    id: user.id,
    displayName: user.displayName ?? user.name ?? (email || user.id),
    email,
    role: user.role,
    factoryScopes:
      user.factoryScopes ??
      user.factoryIds?.map((factoryId) => ({ id: factoryId, name: factoryId })) ??
      [],
  };
}

async function loadCurrentUser(fallbackEmail?: string): Promise<SessionUser> {
  return normalizeSessionUser(
    await apiRequest<CurrentUserApiResponse>("/me"),
    fallbackEmail,
  );
}

async function refreshAccessToken() {
  const response = await apiRequest<AccessTokenResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({}),
  });
  accessTokenStore.set(response.accessToken);
  return response;
}

export async function getCurrentSession(): Promise<SessionSnapshot | null> {
  if (appConfig.enableMockApi) {
    return getMockSession();
  }

  try {
    const token = await refreshAccessToken();
    return {
      user: await loadCurrentUser(),
      expiresAt: new Date(Date.now() + token.expiresIn * 1_000).toISOString(),
    };
  } catch (error) {
    accessTokenStore.clear();
    if (error instanceof ApiClientError && error.status === 401) {
      return null;
    }
    throw error;
  }
}

export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  if (appConfig.enableMockApi) {
    return loginWithMock(credentials);
  }

  const token = await apiRequest<AccessTokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email: credentials.email, password: credentials.password }),
  });
  accessTokenStore.set(token.accessToken);

  return {
    session: {
      user: await loadCurrentUser(credentials.email),
      expiresAt: new Date(Date.now() + token.expiresIn * 1_000).toISOString(),
    },
  };
}

export async function logout() {
  if (appConfig.enableMockApi) {
    return logoutFromMock();
  }

  try {
    await apiRequest<{ readonly revoked: boolean }>("/auth/logout", {
      method: "POST",
      body: JSON.stringify({}),
    });
  } finally {
    accessTokenStore.clear();
  }
}

export async function requestPasswordReset(
  request: PasswordResetRequest,
): Promise<PasswordResetAccepted> {
  if (appConfig.enableMockApi) {
    return requestPasswordResetFromMock(request);
  }

  return apiRequest<PasswordResetAccepted>("/auth/password-reset/request", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getAuthServiceStatus(): Promise<AuthServiceStatus> {
  if (appConfig.enableMockApi) {
    return getMockAuthServiceStatus();
  }

  const response = await apiRequest<{ readonly status: "alive" | "degraded" | "ok" }>(
    "/health/live",
  );
  return { status: response.status === "degraded" ? "degraded" : "available" };
}
