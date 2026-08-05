import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getAuthServiceStatus,
  login,
  logout,
  requestPasswordReset,
} from "@/features/auth/api/session-api";
import { normalizeAuthError } from "@/features/auth/model/auth-error";
import type { LoginCredentials, PasswordResetRequest } from "@/features/auth/model/session";
import { sessionQueryKey } from "@/features/auth/hooks/use-session-query";

export function useLoginMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginCredentials) => login(credentials).catch((error: unknown) => Promise.reject(normalizeAuthError(error))),
    onSuccess: ({ session }) => {
      queryClient.setQueryData(sessionQueryKey, session);
    },
  });
}

export function useLogoutMutation() {
  return useMutation({
    mutationFn: logout,
  });
}

export function usePasswordResetRequestMutation() {
  return useMutation({
    mutationFn: (request: PasswordResetRequest) =>
      requestPasswordReset(request).catch((error: unknown) => Promise.reject(normalizeAuthError(error))),
  });
}

export function useAuthServiceStatusQuery() {
  return useQuery({
    queryKey: ["auth-service-status"],
    queryFn: getAuthServiceStatus,
    retry: 1,
    staleTime: 60_000,
  });
}
