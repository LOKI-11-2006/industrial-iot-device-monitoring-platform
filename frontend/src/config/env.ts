import { z } from "zod";

const environmentSchema = z.object({
  VITE_API_BASE_URL: z.string().min(1).default("/api/v1"),
  VITE_APP_NAME: z.string().min(1).default("ForgeSight"),
  VITE_ENABLE_MOCK_API: z.enum(["true", "false"]).default("true"),
});

const environment = environmentSchema.parse(import.meta.env);

export const appConfig = Object.freeze({
  apiBaseUrl: environment.VITE_API_BASE_URL,
  appName: environment.VITE_APP_NAME,
  enableMockApi: environment.VITE_ENABLE_MOCK_API === "true",
});
