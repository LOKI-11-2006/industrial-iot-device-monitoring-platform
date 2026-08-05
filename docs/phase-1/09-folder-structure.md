# 9. Folder Structure

The following is the planned repository structure for later phases. Phase 1 contains documentation only; empty implementation folders should not be created merely to imitate progress.

```text
industrial-iot-device-monitoring-platform/
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── Makefile
├── .editorconfig
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .github/
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   ├── pull_request_template.md
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
│       ├── ci.yml
│       ├── security.yml
│       ├── deploy-dev.yml
│       └── deploy-prod.yml
├── docs/
│   ├── phase-1/
│   │   ├── 01-business-requirements.md
│   │   ├── 02-functional-requirements.md
│   │   ├── 03-non-functional-requirements.md
│   │   ├── 04-software-architecture.md
│   │   ├── 05-aws-architecture.md
│   │   ├── 06-module-breakdown.md
│   │   ├── 07-user-roles.md
│   │   ├── 08-database-design.md
│   │   ├── 09-folder-structure.md
│   │   ├── 10-api-list.md
│   │   ├── 11-ui-wireframes.md
│   │   └── 12-development-roadmap.md
│   ├── adr/
│   ├── api/
│   ├── architecture/
│   ├── operations/
│   ├── security/
│   └── testing/
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── public/
│   └── src/
│       ├── app/
│       │   ├── providers/
│       │   ├── router/
│       │   └── styles/
│       ├── features/
│       │   ├── auth/
│       │   ├── dashboard/
│       │   ├── factories/
│       │   ├── devices/
│       │   ├── monitoring/
│       │   ├── analytics/
│       │   ├── alerts/
│       │   ├── reports/
│       │   ├── users/
│       │   ├── audit/
│       │   ├── security/
│       │   ├── settings/
│       │   └── platform-health/
│       ├── shared/
│       │   ├── api/
│       │   ├── components/
│       │   ├── hooks/
│       │   ├── lib/
│       │   ├── schemas/
│       │   ├── types/
│       │   └── utils/
│       ├── test/
│       └── main.tsx
├── backend/
│   ├── pyproject.toml
│   ├── src/iot_platform/
│   │   ├── bootstrap/
│   │   ├── shared/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   ├── infrastructure/
│   │   │   └── observability/
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   ├── users/
│   │   │   ├── factories/
│   │   │   ├── devices/
│   │   │   ├── telemetry/
│   │   │   ├── health/
│   │   │   ├── alerts/
│   │   │   ├── notifications/
│   │   │   ├── analytics/
│   │   │   ├── reports/
│   │   │   ├── audit/
│   │   │   ├── security/
│   │   │   └── settings/
│   │   ├── entrypoints/
│   │   │   ├── api/
│   │   │   ├── telemetry_worker/
│   │   │   ├── rules_worker/
│   │   │   └── jobs/
│   │   └── config.py
│   └── tests/
│       ├── unit/
│       ├── integration/
│       ├── contract/
│       └── security/
├── simulator/
│   ├── pyproject.toml
│   ├── src/iot_simulator/
│   │   ├── cli/
│   │   ├── devices/
│   │   ├── scenarios/
│   │   ├── telemetry/
│   │   ├── mqtt/
│   │   └── observability/
│   ├── config/
│   │   ├── device-catalog.example.yaml
│   │   └── scenarios.example.yaml
│   └── tests/
├── infrastructure/
│   ├── app/
│   ├── stacks/
│   │   ├── edge/
│   │   ├── api/
│   │   ├── iot/
│   │   ├── data/
│   │   ├── observability/
│   │   └── security/
│   ├── environments/
│   ├── policies/
│   └── tests/
├── contracts/
│   ├── openapi/
│   ├── asyncapi/
│   ├── events/
│   └── examples/
├── scripts/
│   ├── bootstrap/
│   ├── development/
│   ├── deployment/
│   └── operations/
└── tests/
    ├── e2e/
    ├── performance/
    └── resilience/
```

## 9.1 Separation rationale

| Boundary | Problem | Solution and reason | Tradeoff |
|---|---|---|---|
| `frontend/` vs `backend/` | Independent toolchains and deployment | Keep builds, dependencies, tests, and ownership explicit | Some shared concepts need generated contracts rather than source imports |
| `modules/` | Feature code can become a tangled layer cake | Co-locate domain/application/adapters by business capability | Requires enforcement to avoid cross-module shortcuts |
| `entrypoints/` | HTTP and event workers have different lifecycles | Compose each deployment separately from reusable use cases | More composition configuration |
| `contracts/` | Browser, API, worker, and simulator must agree | Version OpenAPI/AsyncAPI/event schemas and examples centrally | Contract generation/versioning becomes a maintained build step |
| `infrastructure/` | Console changes are not reproducible | Store deployable cloud design and policy tests beside application | Requires cloud review skills |
| `docs/adr/` | Architecture decisions drift or become folklore | Record accepted/superseded decisions with consequences | Small documentation overhead |

## 9.2 Naming and ownership rules

- Python packages and functions use `snake_case`; types use `PascalCase`.
- TypeScript components/types use `PascalCase`; hooks use `useX`; non-component files use consistent kebab-case or project-approved convention.
- One file has one primary responsibility; generic `utils` files do not become dumping grounds.
- A feature imports through public module exports, not another feature's private folder.
- Tests mirror source ownership and name observable behavior.
- Generated files are identified and never hand-edited.
- Secrets, certificates, `.env` files, reports, build output, and simulator runtime state are ignored.

## 9.3 Documentation ownership

- `docs/architecture`: C4 diagrams and system views;
- `docs/adr`: one decision per record using Problem -> Solution -> Reason -> Advantages -> Tradeoffs;
- `docs/api`: human API guides generated/linked from canonical contracts;
- `docs/security`: threat model, identity, secrets, incident response, hardening;
- `docs/operations`: deployment, rollback, backup/restore, alarms, DLQ, certificate runbooks;
- `docs/testing`: strategy, environments, traceability, performance and security evidence.
