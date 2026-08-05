import { apiRequest } from "@/api/client";
import { appConfig } from "@/config/env";
import type { SessionSnapshot } from "@/features/auth/model/session";
import { USER_ROLES } from "@/types/user-role";

const mockSession: SessionSnapshot = {
  user: {
    id: "usr_demo_super_admin",
    displayName: "Avery Chen",
    email: "avery.chen@example.com",
    role: USER_ROLES.superAdministrator,
    factoryScopes: [
      { id: "fac_demo_bengaluru", name: "Bengaluru Plant" },
      { id: "fac_demo_pune", name: "Pune Works" },
    ],
  },
  expiresAt: "2099-01-01T00:00:00.000Z",
};

export async function getCurrentSession(): Promise<SessionSnapshot> {
  if (appConfig.enableMockApi) {
    return Promise.resolve(mockSession);
  }

  const response = await apiRequest<SessionSnapshot>("/me/session");
  return response.data;
}
