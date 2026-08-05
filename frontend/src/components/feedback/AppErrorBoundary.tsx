import { Component, type ErrorInfo, type PropsWithChildren, type ReactNode } from "react";

interface AppErrorBoundaryState {
  readonly hasError: boolean;
}

export class AppErrorBoundary extends Component<PropsWithChildren, AppErrorBoundaryState> {
  state: AppErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): AppErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ForgeSight render boundary captured an error.", error, errorInfo);
  }

  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <main className="grid min-h-screen place-items-center bg-background px-4">
        <section className="w-full max-w-lg rounded-lg border border-border bg-card p-8 text-center shadow-dialog" aria-labelledby="app-error-title">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-status-critical">Application error</p>
          <h1 id="app-error-title" className="mt-3 text-2xl font-semibold tracking-tight">ForgeSight could not render this view</h1>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            No operational action was submitted. Reload the console, or return to the Dashboard if the problem continues.
          </p>
          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <a href="/" className="inline-flex min-h-10 items-center justify-center rounded-sm border border-border bg-card px-4 text-[13px] font-semibold hover:bg-accent">
              Go to Dashboard
            </a>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="inline-flex min-h-10 items-center justify-center rounded-sm bg-primary px-4 text-[13px] font-semibold text-primary-foreground hover:bg-primary-hover"
            >
              Reload application
            </button>
          </div>
        </section>
      </main>
    );
  }
}
