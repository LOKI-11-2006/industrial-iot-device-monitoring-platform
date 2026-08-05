import { useQuery } from "@tanstack/react-query";

import { getCurrentSession } from "@/features/auth/api/session-api";

export const sessionQueryKey = ["session"] as const;

export function useSessionQuery() {
  return useQuery({
    queryKey: sessionQueryKey,
    queryFn: getCurrentSession,
    staleTime: 5 * 60_000,
  });
}
