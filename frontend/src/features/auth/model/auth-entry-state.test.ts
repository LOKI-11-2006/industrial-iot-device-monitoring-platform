import { afterEach, describe, expect, it } from "vitest";

import {
  clearPendingAuthEntryReason,
  getPendingAuthEntryReason,
  setPendingAuthEntryReason,
} from "@/features/auth/model/auth-entry-state";

describe("authentication entry state", () => {
  afterEach(clearPendingAuthEntryReason);

  it("carries a one-page session transition reason until the login page clears it", () => {
    setPendingAuthEntryReason("signed-out");
    expect(getPendingAuthEntryReason()).toBe("signed-out");

    clearPendingAuthEntryReason();
    expect(getPendingAuthEntryReason()).toBeNull();
  });
});
