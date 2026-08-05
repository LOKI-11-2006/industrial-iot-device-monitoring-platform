import { z } from "zod";

const workEmail = z
  .string()
  .trim()
  .min(1, "Enter your work email.")
  .max(254, "Email must be 254 characters or fewer.")
  .email("Enter a valid work email.");

export const loginSchema = z.object({
  email: workEmail,
  password: z
    .string()
    .min(1, "Enter your password.")
    .min(8, "Password must contain at least 8 characters.")
    .max(128, "Password must contain 128 characters or fewer."),
  rememberDevice: z.boolean(),
});

export const forgotPasswordSchema = z.object({
  email: workEmail,
});

export type LoginFormValues = z.infer<typeof loginSchema>;
export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;
