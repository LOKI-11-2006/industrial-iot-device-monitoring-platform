export interface ApiProblem {
  readonly type?: string;
  readonly title: string;
  readonly status: number;
  readonly code: string;
  readonly detail: string;
  readonly instance?: string;
  readonly correlationId?: string;
  readonly fieldErrors?: Readonly<Record<string, readonly string[]>>;
  readonly retryAfterSeconds?: number;
}
