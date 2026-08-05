export interface ApiEnvelope<TData> {
  readonly data: TData;
  readonly requestId?: string;
}

export interface ApiProblem {
  readonly code: string;
  readonly message: string;
  readonly requestId?: string;
  readonly fieldErrors?: Readonly<Record<string, readonly string[]>>;
}
