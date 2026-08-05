import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import { App } from "@/app/App";
import { clearPendingAuthEntryReason } from "@/features/auth/model/auth-entry-state";
import { clearMockSession } from "@/features/auth/services/mock-auth-api";
import { queryClient } from "@/services/query-client";

describe("authentication journey", () => {
  afterEach(() => {
    cleanup();
    queryClient.clear();
    clearMockSession();
    clearPendingAuthEntryReason();
    window.history.replaceState({}, "", "/");
  });

  it("signs in, reaches the protected shell, and signs out with confirmation", async () => {
    window.history.replaceState({}, "", "/login");
    const user = userEvent.setup();
    render(<App />);

    expect(
      await screen.findByRole("heading", { name: "Sign in to ForgeSight" }),
    ).toBeVisible();

    await user.type(screen.getByLabelText("Work email"), "operator@example.com");
    await user.type(screen.getByLabelText("Password", { selector: "input" }), "secure-password");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Open profile menu" }));
    await user.click(await screen.findByRole("menuitem", { name: "Sign out" }));

    expect(await screen.findByText("You are signed out")).toBeVisible();
    expect(window.location.pathname).toBe("/login");
  });
});
