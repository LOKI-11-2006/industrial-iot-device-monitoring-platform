# ForgeSight frontend

Production-oriented React and TypeScript frontend for the ForgeSight Industrial IoT Device Management and Predictive Monitoring Platform.

## Current delivery gate

Frontend Phase 1 establishes the project foundation only:

- React 18, TypeScript and Vite initialization
- approved dependency stack and strict compiler/lint configuration
- mandatory modular source folders
- enterprise dark-theme tokens and self-hosted product typography
- shadcn-compatible component configuration and accessible foundational primitives
- lazy, typed route registry for every required page
- permission-filtered responsive sidebar, top navigation, breadcrumbs and global destination search
- isolated API client, React Query provider and mock session adapter
- loading, network-error, unauthorized, forbidden and 404 boundaries

Authentication forms and behavior are intentionally reserved for Frontend Phase 2. Feature routes display an explicit phase-boundary canvas rather than presenting temporary data or placeholder widgets as finished functionality.

## Requirements

- Node.js 20.19 or newer
- npm 10 or newer

## Local setup

1. Copy `.env.example` to `.env.local`.
2. Install dependencies with `npm install`.
3. Start the development server with `npm run dev`.
4. Open `http://localhost:4173`.

Mock mode is enabled by default and is isolated behind the session API adapter. Set `VITE_ENABLE_MOCK_API=false` only when a compatible backend session endpoint is available.

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
