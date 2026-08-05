import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useRef } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { FormField } from "@/components/forms/FormField";
import { fieldDescriptionIds } from "@/components/forms/form-field-ids";
import { PasswordInput } from "@/components/forms/PasswordInput";
import { InlineAlert } from "@/components/feedback/InlineAlert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AuthCard } from "@/features/auth/components/AuthCard";
import { AuthServiceStatus } from "@/features/auth/components/AuthServiceStatus";
import { useLoginMutation } from "@/features/auth/hooks/use-auth-mutations";
import { AuthError } from "@/features/auth/model/auth-error";
import {
  clearPendingAuthEntryReason,
  type AuthEntryReason,
} from "@/features/auth/model/auth-entry-state";
import { resolveAuthorizedReturnPath } from "@/features/auth/utils/return-path";
import { loginSchema, type LoginFormValues } from "@/features/auth/validation/auth-schemas";
import { useCountdown } from "@/hooks/use-countdown";
import { paths } from "@/routes/paths";

interface LoginLocationState {
  readonly reason?: AuthEntryReason;
  readonly returnTo?: string;
}

function loginErrorContent(error: AuthError, secondsRemaining: number) {
  switch (error.code) {
    case "INVALID_CREDENTIALS":
      return { title: "Sign-in was not accepted", detail: "Email or password is incorrect. Check both fields and try again." };
    case "ACCOUNT_LOCKED":
      return { title: "Sign-in is temporarily unavailable", detail: "Wait before trying again, or contact your factory administrator if access is urgent." };
    case "RATE_LIMITED":
      return {
        title: "Too many sign-in attempts",
        detail: secondsRemaining > 0 ? `Try again in ${secondsRemaining} seconds.` : "You can try again now.",
      };
    case "NETWORK_ERROR":
      return { title: "Authentication service unavailable", detail: "Check your connection. Your email remains in the form so you can retry safely." };
    default:
      return { title: "Sign-in could not be completed", detail: "No session was created. Retry, or contact your factory administrator." };
  }
}

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const locationState = location.state as LoginLocationState | null;
  const loginMutation = useLoginMutation();
  const { secondsRemaining, start: startCountdown } = useCountdown();
  const serverErrorRef = useRef<HTMLDivElement>(null);
  const {
    formState: { errors },
    handleSubmit,
    register,
    setFocus,
    setValue,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "", rememberDevice: false },
    mode: "onBlur",
  });

  const serverError = loginMutation.error instanceof AuthError ? loginMutation.error : null;
  const serverErrorContent = serverError ? loginErrorContent(serverError, secondsRemaining) : null;

  useEffect(() => {
    clearPendingAuthEntryReason();
  }, []);

  useEffect(() => {
    if (serverError) {
      serverErrorRef.current?.focus();
      if (serverError.code === "RATE_LIMITED" && serverError.retryAfterSeconds) {
        startCountdown(serverError.retryAfterSeconds);
      }
    }
  }, [serverError, startCountdown]);

  const onSubmit = handleSubmit((values) => {
    loginMutation.mutate(values, {
      onError: (error) => {
        if (error instanceof AuthError && error.code !== "NETWORK_ERROR") {
          setValue("password", "");
          setFocus("password");
        }
      },
      onSuccess: ({ session }) => {
        const destination = resolveAuthorizedReturnPath(locationState?.returnTo, session.user.role);
        void navigate(destination, { replace: true });
      },
    });
  });

  return (
    <AuthCard
      title="Sign in to ForgeSight"
      description="Use your work account to enter the authorized industrial operations console."
      footer={
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <AuthServiceStatus />
          <a id="support-guidance" href="#support-guidance" className="text-[11px] font-medium text-secondary hover:underline">Contact administrator</a>
        </div>
      }
    >
      {locationState?.reason === "session-expired" ? (
        <InlineAlert title="Your session expired" className="mb-5">Sign in again to restore your authorized workspace.</InlineAlert>
      ) : null}
      {locationState?.reason === "authentication-required" ? (
        <InlineAlert title="Sign in required" className="mb-5">Authenticate to continue to the requested authorized destination.</InlineAlert>
      ) : null}
      {locationState?.reason === "signed-out" ? (
        <InlineAlert title="You are signed out" variant="success" className="mb-5">Your active browser session was closed.</InlineAlert>
      ) : null}

      {serverErrorContent ? (
        <div ref={serverErrorRef} tabIndex={-1} role="alert" className="mb-5 outline-none">
          <InlineAlert title={serverErrorContent.title} variant={serverError?.code === "NETWORK_ERROR" ? "warning" : "danger"}>
            {serverErrorContent.detail}
          </InlineAlert>
        </div>
      ) : null}

      <form onSubmit={(event) => void onSubmit(event)} noValidate>
        <div className="space-y-5">
          <FormField inputId="login-email" label="Work email" error={errors.email?.message}>
            <Input
              id="login-email"
              type="email"
              autoComplete="username"
              inputMode="email"
              placeholder="name@company.com"
              disabled={loginMutation.isPending}
              hasError={Boolean(errors.email)}
              aria-describedby={fieldDescriptionIds("login-email", false, Boolean(errors.email))}
              {...register("email")}
            />
          </FormField>

          <FormField
            inputId="login-password"
            label="Password"
            error={errors.password?.message}
            hint={<Link to={paths.forgotPassword} className="font-medium text-secondary hover:underline">Forgot password?</Link>}
          >
            <PasswordInput
              id="login-password"
              autoComplete="current-password"
              disabled={loginMutation.isPending}
              hasError={Boolean(errors.password)}
              aria-describedby={fieldDescriptionIds("login-password", true, Boolean(errors.password))}
              {...register("password")}
            />
          </FormField>
        </div>

        <label className="mt-5 flex min-h-11 cursor-pointer items-center gap-3 rounded-sm text-xs text-muted-foreground">
          <input
            type="checkbox"
            className="size-4 rounded-xs border-border accent-primary focus-visible:ring-2 focus-visible:ring-ring"
            disabled={loginMutation.isPending}
            {...register("rememberDevice")}
          />
          <span><span className="font-medium text-foreground">Remember this device</span> on this trusted browser</span>
        </label>

        <Button
          type="submit"
          className="mt-5 w-full"
          size="large"
          disabled={secondsRemaining > 0}
          isLoading={loginMutation.isPending}
        >
          {loginMutation.isPending
            ? "Signing in…"
            : secondsRemaining > 0
              ? `Try again in ${secondsRemaining}s`
              : "Sign in"}
        </Button>
      </form>

      <p className="mt-5 text-center text-[11px] leading-5 text-muted-foreground">
        Authorized access only. Sign-in attempts and privileged activity may be monitored and audited.
      </p>
    </AuthCard>
  );
}
