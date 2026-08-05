# Industrial IoT Device Management & Predictive Monitoring Platform

A production-oriented AWS platform for securely registering industrial devices, ingesting live telemetry, monitoring factory health, detecting abnormal behavior, managing alerts, and preserving a complete audit trail.

## Project status

**Phase 1 - Canonical Software Architecture Document v2.0: approved.**

**Phase 2 - UI/UX Design Specification v1.0: approved.**

**Frontend Phase 1 - project foundation, theme, routing and responsive shell: approved.**

**Frontend Phase 2 - authentication and account recovery: complete and awaiting approval.**

The repository now contains the approved frontend foundation and the Phase 2 authentication implementation. Dashboard implementation remains gated until Frontend Phase 2 is explicitly approved.

## Canonical architecture baseline

[Software Architecture Document v2.0](docs/SOFTWARE_ARCHITECTURE_DOCUMENT.md) is the implementation handoff and source of truth. It contains all 17 required sections: business, functional and non-functional requirements; complete system, AWS and software architecture; database and API designs; folder structure; security and IoT architecture; data flows; user journeys; UI planning; roadmap; risks; and future enhancements.

If a supporting document conflicts with the canonical SAD, the SAD takes precedence until an approved Architecture Decision Record changes the baseline.

## UI/UX design baseline

[UI/UX Design Specification v1.0](docs/UI_UX_DESIGN_SPECIFICATION.md) is the frontend experience blueprint. It defines the enterprise dark design system, role-aware navigation, responsive grid, component and interaction standards, accessibility requirements, complete specifications for 20 routes, analytical visualization choices, and a low-fidelity wireframe for every route. It is a design-only deliverable and contains no application implementation.

## Supporting Phase 1 analysis

| # | Deliverable | Document |
|---:|---|---|
| 1 | Business Requirements Analysis | [01-business-requirements.md](docs/phase-1/01-business-requirements.md) |
| 2 | Functional Requirements | [02-functional-requirements.md](docs/phase-1/02-functional-requirements.md) |
| 3 | Non-Functional Requirements | [03-non-functional-requirements.md](docs/phase-1/03-non-functional-requirements.md) |
| 4 | Complete Software Architecture | [04-software-architecture.md](docs/phase-1/04-software-architecture.md) |
| 5 | AWS Architecture | [05-aws-architecture.md](docs/phase-1/05-aws-architecture.md) |
| 6 | Module Breakdown | [06-module-breakdown.md](docs/phase-1/06-module-breakdown.md) |
| 7 | User Roles | [07-user-roles.md](docs/phase-1/07-user-roles.md) |
| 8 | Database Design | [08-database-design.md](docs/phase-1/08-database-design.md) |
| 9 | Folder Structure | [09-folder-structure.md](docs/phase-1/09-folder-structure.md) |
| 10 | API List | [10-api-list.md](docs/phase-1/10-api-list.md) |
| 11 | UI Wireframes | [11-ui-wireframes.md](docs/phase-1/11-ui-wireframes.md) |
| 12 | Development Roadmap | [12-development-roadmap.md](docs/phase-1/12-development-roadmap.md) |

## Approved technology direction

- Frontend: React, TypeScript, Tailwind CSS, shadcn/ui, React Router, TanStack Query, Recharts
- Backend: Python and FastAPI with clean architecture boundaries
- Data: Amazon DynamoDB, Amazon S3, and CloudWatch Logs
- Identity: JWT access tokens, refresh-token rotation, and role-based access control
- IoT: AWS IoT Core with per-device X.509 certificates and MQTT over TLS
- AWS: API Gateway, Lambda, DynamoDB, IoT Core, S3, SNS, CloudWatch, IAM, KMS, WAF, CloudTrail, and Secrets Manager
- Delivery: infrastructure as code, automated testing, security scanning, and gated deployment pipelines

## Frontend implementation

The [frontend workspace](frontend/README.md) contains the approval-gated React implementation. Frontend Phase 1 established the production toolchain, strict TypeScript boundaries, design tokens, reusable shell primitives, role-aware route metadata, responsive navigation, API/query-provider seams, and explicit error/access states. Frontend Phase 2 adds accessible authentication, session restoration, guarded navigation, safe recovery messaging, throttling feedback, and a backend-ready typed auth adapter.

## Architecture principles

1. Security and tenant isolation are enforced server-side and default to deny.
2. Device identity is separate from human identity.
3. Telemetry ingestion is asynchronous and resilient to downstream failures.
4. Operational data and analytical exports use storage optimized for their access patterns.
5. Every privileged action is attributable, immutable, and observable.
6. Local development and the capstone demonstration preserve the production architecture rather than replacing it with placeholders.

## Phase gate

The next permitted activity is stakeholder review of Frontend Phase 2. Frontend Phase 3 dashboard work may begin only after explicit approval. Architecture or design changes discovered later must be recorded and reviewed rather than silently changing the approved baselines.
