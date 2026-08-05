# 12. Development Roadmap

## 12.1 Phase-gate policy

Work proceeds through ten sequential phases. Each phase ends with a reviewable evidence package and requires **explicit approval** before the next phase begins. Failed acceptance criteria are resolved in the current phase; they are not silently deferred.

Current state: **Phase 1 complete in documentation and awaiting approval. No implementation code is authorized yet.**

## 12.2 Ten-phase roadmap

| Phase | Objective | Primary deliverables | Exit evidence / gate |
|---:|---|---|---|
| 1 | Requirements and system design | Business/functional/non-functional requirements, software/AWS architecture, modules, roles, DynamoDB design, folder structure, APIs, wireframes, roadmap | Stakeholder reviews all 12 documents; risks and open decisions recorded; explicit approval |
| 2 | Frontend | React/TypeScript application shell, design system, authentication UX, all module screens using typed mock adapters, responsive/accessibility states | Lint/type/tests pass; key workflows and responsive views reviewed; no hard-coded authorization |
| 3 | Backend | FastAPI clean architecture, authentication/session flow, RBAC/factory scope, core modules, OpenAPI, error/audit/observability foundations | Unit/contract/authorization tests pass; OpenAPI reviewed; threat controls demonstrated |
| 4 | Database | DynamoDB repositories, table/index definitions, transactions, TTL, projections, seed/migration tooling | Access-pattern tests, concurrency/idempotency evidence, backup/restore plan, no request-path scans |
| 5 | IoT Simulator | 20+ realistic devices, machine profiles, scenarios, MQTT client, deterministic runs, telemetry contract tests | Normal/warning/critical/disconnect/recovery demo; per-device identity; bounded-rate soak test |
| 6 | AWS Integration | IoT Core, Lambda, API Gateway, SQS/DLQ, DynamoDB, S3, SNS, realtime updates, CloudWatch wiring, IaC | Repeatable dev deployment; end-to-end cloud ingestion and alert demo; cost/limit checks |
| 7 | DevSecOps | CI/CD, IAM hardening, WAF, KMS/secrets, SBOM, SAST/dependency/secret/IaC scanning, alarms/runbooks | Security pipeline gates pass; least-privilege and threat-model review; rollback exercise |
| 8 | Testing | Unit, integration, contract, end-to-end, performance, resilience, accessibility, and security suites | Requirements traceability; target coverage/risk evidence; defect threshold and load SLOs met |
| 9 | Documentation | Final README, API/AsyncAPI, architecture, schema, setup, deployment, operations, security, testing, demo guide | A new reviewer can deploy, operate, troubleshoot, and demonstrate from docs alone |
| 10 | Deployment | Production-like environment, domain/TLS, data/bootstrap, monitoring, smoke tests, demo readiness | Deployment checklist, live smoke test, dashboards/alarms green, recovery/rollback evidence, final sign-off |

## 12.3 Detailed phase outcomes

### Phase 1 - Requirements, architecture, and design

Status: **complete, awaiting explicit approval**.

Review questions:

- Do requirements reflect the intended capstone boundary and six roles?
- Are measurable targets credible for the budget and demo?
- Are the modular API, asynchronous ingestion, DynamoDB access patterns, and AWS services accepted?
- Are the UI hierarchy, permissions, and phase order acceptable?

Any requested correction updates the Phase 1 baseline before approval.

### Phase 2 - Frontend

Build sequence:

1. Vite/React/TypeScript quality baseline and application providers.
2. Design tokens, accessible primitives, shell, route/permission metadata.
3. Authentication/session UX and typed mock API layer.
4. Dashboard, factories, devices, monitoring, analytics, alerts.
5. Reports, logs, security, users, settings, platform health.
6. Responsive, accessibility, visual regression, and component tests.

The frontend uses realistic contract fixtures, never UI-only business logic pretending to be the backend.

### Phase 3 - Backend

Build the vertical skeleton first: health -> configuration -> structured errors/logs -> auth -> authorization -> one complete factory/device workflow. Then extend by module while preserving clean boundaries. Generate and validate OpenAPI continuously. Authentication and factory isolation tests precede broad feature implementation.

### Phase 4 - Database

Implement repositories from documented access patterns. Prove keys with representative load and negative cases. Add conditional writes, transactions, TTL, stream/outbox projection handling, reconciliation, backup, and schema migration tooling before connecting every endpoint.

### Phase 5 - IoT simulator

Implement machine-specific baselines and correlated behavior for CNC, boiler, hydraulic press, compressor, packaging machine, cooling unit, generator, conveyor, robotic arm, and additional devices. Scenarios specify onset, slope, noise, duration, recovery, and expected alert outcome. Credentials remain outside the repository.

### Phase 6 - AWS integration

Deploy lowest-cost safe development infrastructure first. Validate one device end to end, then 20 devices, then burst/backlog behavior. Add notification and report delivery after canonical telemetry/alerts are stable. Capture costs and service quotas during each scale step.

### Phase 7 - DevSecOps

Formalize threat model and trust boundaries; harden IAM, IoT policies, edge controls, encryption, secrets, artifacts, provenance, CI federation, dependency policies, incident playbooks, and alarms. Security controls must be exercised, not merely configured.

### Phase 8 - Testing

Execute the test pyramid plus production-risk tests:

- unit: domain rules, health, thresholds, authorization policies;
- contract: OpenAPI, event schemas, simulator messages;
- integration: DynamoDB, IoT routing, SQS retries/DLQ, S3/SNS adapters;
- end-to-end: role workflows and critical alert scenarios;
- performance: API percentiles, sustained telemetry, bursts, dashboard freshness;
- resilience: worker failure, duplicate/out-of-order events, reconnect, DLQ/redrive;
- security: OWASP API/web cases, cross-factory access, token/session misuse, IoT policy negatives;
- accessibility: automated checks plus keyboard and screen-reader workflow review.

### Phase 9 - Documentation

Reconcile documentation with actual behavior. Generate reference material from canonical contracts, then add human explanations, diagrams, setup/deployment paths, operational runbooks, security guidance, troubleshooting, screenshots, and a concise portfolio/demo narrative.

### Phase 10 - Deployment

Promote an immutable reviewed build to the production-like environment. Run smoke tests, simulator scenarios, alarms, report generation, backup/restore checks, and rollback rehearsal. Record final versions, URLs, known limitations, budget state, and ownership.

## 12.4 Suggested milestone schedule

This is a planning baseline, not a promise; quality gates determine completion.

| Milestone | Indicative duration | Dependencies |
|---|---:|---|
| Phase 1 | 1 week review cycle | Stakeholder availability |
| Phase 2 | 2-3 weeks | Approved contracts/wireframes |
| Phase 3 | 3-4 weeks | Approved frontend contracts and auth design |
| Phase 4 | 1-2 weeks | Backend ports/access patterns |
| Phase 5 | 1-2 weeks | MQTT/event contract |
| Phase 6 | 2-3 weeks | AWS account/budget and stable components |
| Phase 7 | 1-2 weeks | Cloud deployment and CI identity |
| Phase 8 | 2 weeks | Integrated product |
| Phase 9 | 1 week | Stable behavior and evidence |
| Phase 10 | 1 week | Deployment approval/domain/environment |

Parallel work may occur *inside* an approved phase when it does not bypass dependencies or the next phase gate.

## 12.5 Release quality gates

Every implementation phase must meet applicable gates:

- formatting, lint, type checking, and unit tests;
- contract and schema compatibility;
- role/factory authorization negatives;
- secret, dependency, static code, and IaC scanning;
- accessible UI states and responsive review;
- infrastructure drift/security policy tests;
- observability, alarm, and runbook coverage;
- documentation updated in the same change;
- no unresolved critical/high security finding without written, time-bound disposition.

## 12.6 Requirements traceability

Before Phase 8 completion, each P0 functional and non-functional requirement receives:

- implementation module/commit reference;
- unit/integration/e2e test identifier;
- environment and test data/scenario;
- pass/fail evidence and date;
- owner and accepted deviation, if any.

This prevents a visually impressive demo from masking missing security, reliability, or audit requirements.

## 12.7 Initial decision backlog

These decisions are intentionally deferred to the named phase but must not be forgotten:

| Decision | Due | Selection criteria |
|---|---:|---|
| AWS SAM vs CDK | Before Phase 6 | Team fluency, testability, deployment ergonomics, portfolio clarity |
| JWT signing algorithm/key custody | Phase 3 | Rotation, verification performance, key exposure, operational simplicity |
| WebSocket push implementation | Phase 2/6 | authorization, reconnect semantics, cost, API Gateway fit |
| Aggregate bucket intervals | Phase 4 | query ranges, device rate, cost, chart fidelity |
| Notification channels beyond SNS email | Phase 6 | budget, regional availability, delivery evidence |
| Long-term telemetry export format | Phase 6 | query need, Athena compatibility, lifecycle cost |

## 12.8 Stop condition

The repository must remain at the Phase 1 gate until the user explicitly approves Phase 1 and requests Phase 2. Approval should reference any accepted changes or open risks so the design baseline is unambiguous.
