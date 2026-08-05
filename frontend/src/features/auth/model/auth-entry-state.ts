export type AuthEntryReason = "authentication-required" | "session-expired" | "signed-out";

let pendingAuthEntryReason: AuthEntryReason | null = null;

export function setPendingAuthEntryReason(reason: AuthEntryReason) {
  pendingAuthEntryReason = reason;
}

export function getPendingAuthEntryReason() {
  return pendingAuthEntryReason;
}

export function clearPendingAuthEntryReason() {
  pendingAuthEntryReason = null;
}
