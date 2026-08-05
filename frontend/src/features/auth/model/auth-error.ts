import { ApiClientError } from "@/api/client";

export type AuthErrorCode =
  | "INVALID_CREDENTIALS"
  | "ACCOUNT_LOCKED"
  | "RATE_LIMITED"
  | "NETWORK_ERROR"
  | "UNEXPECTED_ERROR";

export class AuthError extends Error {
  readonly code: AuthErrorCode;
  readonly retryAfterSeconds?: number;

  constructor(code: AuthErrorCode, message: string, retryAfterSeconds?: number) {
    super(message);
    this.name = "AuthError";
    this.code = code;
    this.retryAfterSeconds = retryAfterSeconds;
  }
}

export function normalizeAuthError(error: unknown) {
  if (error instanceof AuthError) {
    return error;
  }

  if (error instanceof ApiClientError) {
    if (error.status === 401) {
      return new AuthError("INVALID_CREDENTIALS", "Email or password is incorrect.");
    }
    if (error.status === 423) {
      return new AuthError("ACCOUNT_LOCKED", "Sign-in is temporarily unavailable for this request.");
    }
    if (error.status === 429) {
      return new AuthError(
        "RATE_LIMITED",
        "Too many attempts. Try again later.",
        error.problem.retryAfterSeconds,
      );
    }
  }

  if (error instanceof TypeError) {
    return new AuthError("NETWORK_ERROR", "The authentication service could not be reached.");
  }

  return new AuthError("UNEXPECTED_ERROR", "Sign-in could not be completed safely.");
}
