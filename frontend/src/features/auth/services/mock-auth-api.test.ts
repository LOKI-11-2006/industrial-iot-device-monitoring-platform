import { afterEach, beforeEach, describe, expect, it } from "vitest";

import {
  clearMockSession,
  getMockSession,
  loginWithMock,
  logoutFromMock,
  requestPasswordResetFromMock,
} from "@/features/auth/services/mock-auth-api";
import { USER_ROLES } from "@/types/user-role";

describe("mock authentication service", () => {
  beforeEach(clearMockSession);
  afterEach(clearMockSession);

  it("creates, restores, and closes a browser session", async () => {
    const result = await loginWithMock({
      email: "viewer@example.com",
      password: "secure-password",
      rememberDevice: false,
    });

    expect(result.session.user.role).toBe(USER_ROLES.viewer);
    await expect(getMockSession()).resolves.toEqual(result.session);

    await logoutFromMock();
    await expect(getMockSession()).resolves.toBeNull();
  });

  it("persists a remembered session without exposing credentials", async () => {
    await loginWithMock({
      email: "operator@example.com",
      password: "not-persisted",
      rememberDevice: true,
    });

    const storedSession = window.localStorage.getItem("forgesight.mock.session.persisted");
    expect(storedSession).toContain("operator@example.com");
    expect(storedSession).not.toContain("not-persisted");
  });

  it("returns typed, generic sign-in failure states", async () => {
    await expect(
      loginWithMock({
        email: "invalid@forgesight.demo",
        password: "secure-password",
        rememberDevice: false,
      }),
    ).rejects.toMatchObject({ code: "INVALID_CREDENTIALS" });

    await expect(
      loginWithMock({
        email: "rate-limit@forgesight.demo",
        password: "secure-password",
        rememberDevice: false,
      }),
    ).rejects.toMatchObject({ code: "RATE_LIMITED", retryAfterSeconds: 45 });
  });

  it("accepts reset requests without disclosing account membership", async () => {
    await expect(
      requestPasswordResetFromMock({ email: "unknown@example.com" }),
    ).resolves.toEqual({ accepted: true });
  });
});
