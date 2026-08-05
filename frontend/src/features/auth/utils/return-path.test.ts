import { describe, expect, it } from "vitest";

import { resolveAuthorizedReturnPath } from "@/features/auth/utils/return-path";
import { paths } from "@/routes/paths";
import { USER_ROLES } from "@/types/user-role";

describe("resolveAuthorizedReturnPath", () => {
  it("returns an internal route allowed for the authenticated role", () => {
    expect(resolveAuthorizedReturnPath(paths.devices, USER_ROLES.viewer)).toBe(paths.devices);
  });

  it("falls back to the dashboard for external or unknown destinations", () => {
    expect(resolveAuthorizedReturnPath("//malicious.example", USER_ROLES.viewer)).toBe(
      paths.dashboard,
    );
    expect(resolveAuthorizedReturnPath("https://malicious.example", USER_ROLES.viewer)).toBe(
      paths.dashboard,
    );
    expect(resolveAuthorizedReturnPath("/not-a-route", USER_ROLES.viewer)).toBe(paths.dashboard);
  });

  it("does not return a destination forbidden to the authenticated role", () => {
    expect(resolveAuthorizedReturnPath(paths.roles, USER_ROLES.viewer)).toBe(paths.dashboard);
    expect(resolveAuthorizedReturnPath(paths.roles, USER_ROLES.superAdministrator)).toBe(
      paths.roles,
    );
  });
});
