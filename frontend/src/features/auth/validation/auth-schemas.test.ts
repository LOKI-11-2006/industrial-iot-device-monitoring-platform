import { describe, expect, it } from "vitest";

import {
  forgotPasswordSchema,
  loginSchema,
} from "@/features/auth/validation/auth-schemas";

describe("authentication form schemas", () => {
  it("normalizes a valid work email and accepts a complete login", () => {
    const result = loginSchema.parse({
      email: "  operator@example.com ",
      password: "secure-password",
      rememberDevice: true,
    });

    expect(result.email).toBe("operator@example.com");
    expect(result.rememberDevice).toBe(true);
  });

  it("rejects malformed email addresses and short passwords", () => {
    const result = loginSchema.safeParse({
      email: "not-an-email",
      password: "short",
      rememberDevice: false,
    });

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.flatten().fieldErrors.email).toContain("Enter a valid work email.");
      expect(result.error.flatten().fieldErrors.password).toContain(
        "Password must contain at least 8 characters.",
      );
    }
  });

  it("uses the same non-enumerating email validation for account recovery", () => {
    expect(forgotPasswordSchema.safeParse({ email: "viewer@example.com" }).success).toBe(true);
    expect(forgotPasswordSchema.safeParse({ email: "" }).success).toBe(false);
  });
});
