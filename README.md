# Industrial IoT Device Management & Predictive Monitoring Platform

A production-oriented AWS platform for securely registering industrial devices, ingesting live telemetry, monitoring factory health, detecting abnormal behavior, managing alerts, and preserving a complete audit trail.

## Project status

**Phase 1 - Requirements and Architecture: complete and awaiting approval.**

No application code has been added. Phase 2 must not begin until the Phase 1 package is explicitly approved.

## Phase 1 design package

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

## Architecture principles

1. Security and tenant isolation are enforced server-side and default to deny.
2. Device identity is separate from human identity.
3. Telemetry ingestion is asynchronous and resilient to downstream failures.
4. Operational data and analytical exports use storage optimized for their access patterns.
5. Every privileged action is attributable, immutable, and observable.
6. Local development and the capstone demonstration preserve the production architecture rather than replacing it with placeholders.

## Phase gate

The next permitted activity is stakeholder review of Phase 1. After explicit approval, Phase 2 may implement the frontend against documented contracts and mock adapters. Architecture changes discovered later must be recorded and reviewed rather than silently changing these baselines.
