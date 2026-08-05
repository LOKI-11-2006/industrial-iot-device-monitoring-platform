import type { PropsWithChildren, ReactNode } from "react";

interface AuthCardProps extends PropsWithChildren {
  readonly description: string;
  readonly eyebrow?: string;
  readonly footer?: ReactNode;
  readonly title: string;
}

export function AuthCard({ children, description, eyebrow = "Secure access", footer, title }: AuthCardProps) {
  return (
    <section className="overflow-hidden rounded-lg border border-border bg-card shadow-dialog" aria-labelledby="authentication-title">
      <div className="border-b border-border/70 bg-gradient-to-br from-primary/10 via-card to-card px-6 py-6 sm:px-8 sm:py-7">
        <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-primary">{eyebrow}</p>
        <h1 id="authentication-title" className="mt-2 text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
      <div className="px-6 py-6 sm:px-8 sm:py-7">{children}</div>
      {footer ? <div className="border-t border-border/70 bg-surface/55 px-6 py-4 sm:px-8">{footer}</div> : null}
    </section>
  );
}
