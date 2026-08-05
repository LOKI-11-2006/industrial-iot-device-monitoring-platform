import { AppErrorBoundary } from "@/components/feedback/AppErrorBoundary";
import { AppProviders } from "@/providers/AppProviders";
import { AppRouter } from "@/routes/AppRouter";

export function App() {
  return (
    <AppErrorBoundary>
      <AppProviders>
        <AppRouter />
      </AppProviders>
    </AppErrorBoundary>
  );
}
