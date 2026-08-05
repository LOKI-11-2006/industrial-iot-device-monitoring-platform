import { describe, expect, it } from "vitest";

import { ApiClientError } from "@/api/client";
import { normalizeAuthError } from "@/features/auth/model/auth-error";

describe("normalizeAuthError", () => {
  it("maps canonical API rate-limit metadata into a safe retry state", () => {
    const problem = new ApiClientError(429, {
      title: "Too many requests",
      status: 429,
      code: "RATE_LIMITED",
      detail: "Retry later.",
      retryAfterSeconds: 30,
    });

    expect(normalizeAuthError(problem)).toMatchObject({
      code: "RATE_LIMITED",
      retryAfterSeconds: 30,
    });
  });

  it("maps transport failures without exposing implementation details", () => {
    expect(normalizeAuthError(new TypeError("fetch failed"))).toMatchObject({
      code: "NETWORK_ERROR",
    });
  });
});
