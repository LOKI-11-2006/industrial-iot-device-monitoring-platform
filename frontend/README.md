# ForgeSight frontend

Production-oriented React and TypeScript frontend for the ForgeSight Industrial IoT Device Management and Predictive Monitoring Platform.

## Current delivery gate

Frontend Phase 1 is approved. Frontend Phase 2 adds the authentication experience:

- accessible login and password-recovery forms with inline validation
- show/hide password control, trusted-device persistence and functional sign-out
- guarded navigation with safe, role-authorized return destinations
- session restoration through a typed real/mock authentication adapter
- generic credential and recovery responses that prevent account enumeration
- explicit network, lockout, rate-limit, session-expired and service-status feedback
- retry countdowns, loading states, keyboard focus management and responsive layouts

Dashboard and feature screens remain intentionally gated. They display an explicit phase-boundary canvas rather than presenting temporary data or placeholder widgets as finished functionality.

## Requirements

- Node.js 20.19 or newer
- npm 10 or newer

## Local setup

1. Copy `.env.example` to `.env.local`.
2. Install dependencies with `npm install`.
3. Start the development server with `npm run dev`.
4. Open `http://localhost:4173`.

Mock mode is enabled by default and is isolated behind the session API adapter. Set `VITE_ENABLE_MOCK_API=false` only when a compatible backend session endpoint is available.

In mock mode, any valid email and password of at least eight characters signs in. The email prefixes `viewer`, `operator`, `engineer`, `manager`, `factoryadmin`, and `superadmin` select each approved role. The documented `invalid@forgesight.demo`, `locked@forgesight.demo`, `rate-limit@forgesight.demo`, and `network@forgesight.demo` fixtures exercise safe failure states; never use production credentials in mock mode.

## Dependency security note

The current React Router release is pinned to `7.18.2`. The package registry reports one high-severity advisory inherited through `react-router`; the advisory concerns React Server Components action processing. This Vite client-side application uses `BrowserRouter` and does not enable React Server Components, server actions, SSR, or framework data actions, so the affected execution path is absent. Older Router releases restore broadly applicable redirect and routing vulnerabilities and are not an acceptable downgrade. The exception must be rechecked when a newer patched release is published.

## Quality commands

| Command | Purpose |
|---|---|
| `npm run build` | Strict TypeScript project build and optimized Vite production bundle |
| `npm run lint` | Type-aware ESLint checks with zero warnings permitted |
| `npm test` | Vitest route and architecture checks |
| `npm run dev` | Local Vite development server on port 4173 |

## Source architecture

```text
src/
  app/          application entry composition
  components/   reusable brand, feedback, navigation and UI primitives
  pages/        route-level presentation boundaries
  layouts/      authenticated and unauthenticated shells
  features/     vertical product modules and their adapters
  hooks/        reusable behavior hooks
  services/     cross-feature infrastructure such as the query client
  api/          typed transport boundary
  types/        shared contracts
  utils/        framework-independent utilities
  assets/       product asset registry
  contexts/     typed React contexts
  providers/    provider composition and runtime preferences
  routes/       paths, metadata, guards and router composition
  constants/    immutable navigation and display options
  config/       validated environment configuration
  styles/       approved global tokens and base styles
```

The frontend treats server data as authoritative, keeps server state in React Query, keeps only ephemeral shell preferences in local state/context, and never relies on hidden controls for authorization.

## Design and accessibility baseline

The visual implementation follows `docs/UI_UX_DESIGN_SPECIFICATION.md`: dark blue-black surfaces, teal primary actions, explicit semantic status colors, 12-column responsive behavior, 44 px touch targets, visible focus, skip navigation, reduced-motion support, semantic route headings, and permission-aware navigation. Any change to data meaning, role visibility, interaction consequence, or responsive priority requires approval rather than silent redesign.
