import { accessTokenStore } from "@/api/access-token";
import { appConfig } from "@/config/env";
import type { ApiProblem } from "@/types/api";

export class ApiClientError extends Error {
  readonly status: number;
  readonly problem: ApiProblem;

  constructor(status: number, problem: ApiProblem) {
    super(problem.detail || problem.title || "The request could not be completed.");
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
      detail: "The service returned an unexpected response.",
      status: response.status,
      title: "Unexpected service response",
    };
  }
}

export async function apiRequest<TData>(
  path: string,
  init?: RequestInit,
): Promise<TData> {
  const accessToken = accessTokenStore.get();
  const response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiClientError(response.status, await parseProblem(response));
  }

  return (await response.json()) as TData;
}
