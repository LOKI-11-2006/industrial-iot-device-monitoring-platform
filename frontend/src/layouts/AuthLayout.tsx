import { Activity, LockKeyhole, RadioTower } from "lucide-react";
import { Outlet } from "react-router-dom";

import { ForgeSightBrand } from "@/components/brand/ForgeSightBrand";

export default function AuthLayout() {
  return (
    <main className="relative min-h-screen bg-background lg:grid lg:grid-cols-12">
      <section className="relative hidden border-r border-border/70 bg-[#080D15] p-10 lg:col-span-7 lg:flex lg:flex-col" aria-label="ForgeSight security context">
        <ForgeSightBrand />
        <div className="relative z-10 my-auto max-w-xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Industrial intelligence, clearly governed</p>
          <p className="mt-5 text-balance text-4xl font-semibold leading-tight tracking-tight xl:text-5xl">
            Operational truth for every connected factory.
          </p>
          <p className="mt-5 max-w-lg text-base leading-7 text-muted-foreground">
            Monitor device identity, machine health, telemetry freshness, critical alerts, and accountable response from one secure console.
          </p>
          <div className="mt-10 grid grid-cols-3 gap-3">
            {[
              { icon: RadioTower, label: "Live context" },
              { icon: Activity, label: "Health evidence" },
              { icon: LockKeyhole, label: "Scoped access" },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="rounded-md border border-border/70 bg-card/70 p-4">
                <Icon className="size-5 text-primary" aria-hidden="true" />
                <p className="mt-3 text-xs font-semibold">{label}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="absolute inset-0 opacity-25" aria-hidden="true" style={{ backgroundImage: "radial-gradient(circle at 20% 20%, hsl(var(--primary) / 20%), transparent 32%), radial-gradient(circle at 80% 65%, hsl(var(--secondary) / 14%), transparent 30%)" }} />
        <p className="relative z-10 text-xs text-muted-foreground">Authorized access only · Activity may be monitored and audited</p>
      </section>
      <section className="flex min-h-dvh items-center justify-center px-4 py-8 sm:px-8 sm:py-10 lg:col-span-5">
        <div className="w-full max-w-[440px]">
          <ForgeSightBrand className="mb-8 lg:hidden" />
          <Outlet />
        </div>
      </section>
    </main>
  );
}
