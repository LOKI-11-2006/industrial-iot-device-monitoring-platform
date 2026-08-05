import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, MailCheck } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import { InlineAlert } from "@/components/feedback/InlineAlert";
import { FormField } from "@/components/forms/FormField";
import { fieldDescriptionIds } from "@/components/forms/form-field-ids";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AuthCard } from "@/features/auth/components/AuthCard";
import { AuthServiceStatus } from "@/features/auth/components/AuthServiceStatus";
import { usePasswordResetRequestMutation } from "@/features/auth/hooks/use-auth-mutations";
import { AuthError } from "@/features/auth/model/auth-error";
import {
  forgotPasswordSchema,
  type ForgotPasswordFormValues,
} from "@/features/auth/validation/auth-schemas";
import { useCountdown } from "@/hooks/use-countdown";
import { paths } from "@/routes/paths";

function resetErrorContent(error: AuthError, secondsRemaining: number) {
  if (error.code === "RATE_LIMITED") {
    return {
      title: "Too many reset requests",
      detail:
        secondsRemaining > 0
          ? `Try again in ${secondsRemaining} seconds.`
          : "You can request another message now.",
    };
  }

  if (error.code === "NETWORK_ERROR") {
    return {
      title: "Reset service unavailable",
      detail: "Check your connection. No account information was disclosed and you can retry safely.",
    };
  }

  return {
    title: "Request could not be completed",
    detail: "No account information was disclosed. Retry, or contact your factory administrator.",
  };
}

export default function ForgotPasswordPage() {
  const resetMutation = usePasswordResetRequestMutation();
  const [submittedEmail, setSubmittedEmail] = useState<string | null>(null);
  const { secondsRemaining, start: startCountdown } = useCountdown();
  const serverErrorRef = useRef<HTMLDivElement>(null);
  const {
    formState: { errors },
    handleSubmit,
    register,
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
    mode: "onBlur",
  });

  const serverError = resetMutation.error instanceof AuthError ? resetMutation.error : null;
  const serverErrorContent = serverError
    ? resetErrorContent(serverError, secondsRemaining)
    : null;

  useEffect(() => {
    if (serverError) {
      serverErrorRef.current?.focus();
      if (serverError.code === "RATE_LIMITED" && serverError.retryAfterSeconds) {
        startCountdown(serverError.retryAfterSeconds);
      }
    }
  }, [serverError, startCountdown]);

  const requestReset = (email: string, isResend = false) => {
    resetMutation.mutate(
      { email },
      {
        onSuccess: () => {
          setSubmittedEmail(email);
          startCountdown(30);
          if (isResend) {
            toast.success("Reset instructions requested again.");
          }
        },
      },
    );
  };

  const onSubmit = handleSubmit(({ email }) => requestReset(email));

  return (
    <AuthCard
      eyebrow="Account recovery"
      title={submittedEmail ? "Check your email" : "Reset your password"}
      description={
        submittedEmail
          ? "For privacy, the same confirmation is shown whether or not the account is eligible."
          : "Enter your work email and we’ll request secure reset instructions."
      }
      footer={
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <AuthServiceStatus />
          <span className="text-[11px] text-muted-foreground">Single-use links expire automatically</span>
        </div>
      }
    >
      <Link to={paths.login} className="mb-5 inline-flex min-h-9 items-center gap-2 rounded-sm text-xs font-semibold text-secondary hover:underline focus-visible:ring-2 focus-visible:ring-ring">
        <ArrowLeft className="size-4" aria-hidden="true" /> Back to sign in
      </Link>

      {serverErrorContent ? (
        <div ref={serverErrorRef} tabIndex={-1} role="alert" className="mb-5 outline-none">
          <InlineAlert title={serverErrorContent.title} variant={serverError?.code === "NETWORK_ERROR" ? "warning" : "danger"}>
            {serverErrorContent.detail}
          </InlineAlert>
        </div>
      ) : null}

      {submittedEmail ? (
        <div aria-live="polite">
          <div className="flex size-12 items-center justify-center rounded-md border border-success/25 bg-success/10 text-success">
            <MailCheck className="size-6" aria-hidden="true" />
          </div>
          <h2 className="mt-5 text-base font-semibold">The request was accepted</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            If the submitted address is eligible, reset instructions will arrive shortly. Check spam or quarantine folders before requesting another message.
          </p>
          <Button
            type="button"
            variant="secondary"
            className="mt-6 w-full"
            disabled={secondsRemaining > 0}
            isLoading={resetMutation.isPending}
            onClick={() => requestReset(submittedEmail, true)}
          >
            {resetMutation.isPending
              ? "Sending again…"
              : secondsRemaining > 0
                ? `Send again in ${secondsRemaining}s`
                : "Send instructions again"}
          </Button>
          <button
            type="button"
            onClick={() => {
              resetMutation.reset();
              setSubmittedEmail(null);
            }}
            className="mt-3 min-h-10 w-full rounded-sm text-xs font-semibold text-muted-foreground hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
          >
            Use a different email
          </button>
        </div>
      ) : (
        <form onSubmit={(event) => void onSubmit(event)} noValidate>
          <FormField
            inputId="recovery-email"
            label="Work email"
            error={errors.email?.message}
            hint="Use the address assigned by your organization."
          >
            <Input
              id="recovery-email"
              type="email"
              autoComplete="email"
              inputMode="email"
              placeholder="name@company.com"
              disabled={resetMutation.isPending}
              hasError={Boolean(errors.email)}
              aria-describedby={fieldDescriptionIds("recovery-email", true, Boolean(errors.email))}
              {...register("email")}
            />
          </FormField>

          <Button
            type="submit"
            size="large"
            className="mt-6 w-full"
            disabled={secondsRemaining > 0}
            isLoading={resetMutation.isPending}
          >
            {resetMutation.isPending
              ? "Sending…"
              : secondsRemaining > 0
                ? `Try again in ${secondsRemaining}s`
                : "Send reset instructions"}
          </Button>

          <p className="mt-5 text-center text-[11px] leading-5 text-muted-foreground">
            For security, this page never confirms whether an account exists.
          </p>
        </form>
      )}
    </AuthCard>
  );
}
