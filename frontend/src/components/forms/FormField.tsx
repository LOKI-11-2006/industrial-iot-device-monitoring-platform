import type { PropsWithChildren, ReactNode } from "react";

interface FormFieldProps extends PropsWithChildren {
  readonly error?: string;
  readonly hint?: ReactNode;
  readonly inputId: string;
  readonly label: string;
  readonly optional?: boolean;
}

export function FormField({ children, error, hint, inputId, label, optional = false }: FormFieldProps) {
  const hintId = hint ? `${inputId}-hint` : undefined;
  const errorId = error ? `${inputId}-error` : undefined;

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <label htmlFor={inputId} className="text-xs font-semibold text-foreground">{label}</label>
        {optional ? <span className="text-[11px] text-muted-foreground">Optional</span> : null}
      </div>
      {children}
      {hint ? <div id={hintId} className="mt-1.5 text-xs leading-5 text-muted-foreground">{hint}</div> : null}
      {error ? <p id={errorId} className="mt-1.5 text-xs font-medium leading-5 text-destructive">{error}</p> : null}
    </div>
  );
}
