import { appConfig } from "@/config/env";
import type { ApiEnvelope, ApiProblem } from "@/types/api";

export class ApiClientError extends Error {
  readonly status: number;
  readonly problem: ApiProblem;

  constructor(status: number, problem: ApiProblem) {
    super(problem.message);
    this.name = "ApiClientError";
    this.status = status;
    this.problem = problem;
  }
}

async function parseProblem(response: Response): Promise<ApiProblem> {
  try {
    return (await response.json()) as ApiProblem;
  } catch {
    return {
      code: "UNEXPECTED_RESPONSE",
      message: "The service returned an unexpected response.",
    };
  }
}

export async function apiRequest<TData>(
  path: string,
  init?: RequestInit,
): Promise<ApiEnvelope<TData>> {
  const response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiClientError(response.status, await parseProblem(response));
  }

  return (await response.json()) as ApiEnvelope<TData>;
}
