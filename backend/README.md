# ForgeSight backend

Production-oriented Python 3.12 and FastAPI control plane for the ForgeSight Industrial IoT Device Management and Predictive Monitoring Platform.

## Current delivery gate

Backend Phase 1 establishes the application foundation only:

- mandatory modular package and test structure
- reproducible runtime and development dependency baselines
- typed, environment-driven configuration with production safety invariants
- FastAPI application factory and AWS Lambda/Mangum entry point
- versioned API router with the canonical minimal liveness contract
- restricted CORS, trusted-host enforcement, security headers, correlation IDs, and structured JSON logging
- RFC 9457-style problem responses for HTTP, validation, and unexpected failures
- strict linting, typing, test, coverage, and dependency-audit commands

Authentication, JWT, RBAC, repositories, DynamoDB models, and business feature APIs are intentionally excluded until their corresponding backend phases are approved.

## Requirements

- Python 3.12 or newer (Python 3.13 is supported; Python 3.14 is not yet targeted)
- pip 25 or newer
- AWS credentials are not required for Phase 1

## Local setup

From `backend/`:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.venv\Scripts\python.exe -m scripts.validate_environment
.venv\Scripts\python.exe -m scripts.run_local
```

The API is available at `http://127.0.0.1:8000`, Swagger UI at `/docs`, ReDoc at `/redoc`, and liveness at `/api/v1/health/live` when local documentation is enabled.

## Configuration and secrets

Configuration is read from process environment variables prefixed with `IOT_API_`; a local `.env` file is optional. List settings accept JSON arrays or comma-separated values. Unknown configuration keys are rejected so misspellings cannot silently weaken runtime behavior.

Production configuration enforces HTTPS CORS origins, disables debug and public API documentation, disallows local AWS endpoints and wildcard hosts/origins, and requires a Secrets Manager ARN for the future JWT signing key. Key material and AWS credentials must never be stored in `.env`, source control, logs, or frontend code.

## Quality commands

| Command | Purpose |
|---|---|
| `python -m ruff check .` | Static lint and security-oriented rules |
| `python -m ruff format --check .` | Deterministic formatting |
| `python -m mypy app scripts` | Strict type checking |
| `python -m pytest` | Tests with branch coverage and a 90% minimum |
| `python -m pip_audit -r requirements.txt` | Published dependency vulnerability audit |
| `python -m scripts.check` | Run the local quality gate |

## Source architecture

```text
backend/
  app/
    api/routers/     FastAPI transport boundaries
    controllers/     transport-to-use-case coordination
    services/        application services and ports
    repositories/    persistence interfaces and adapters
    models/          domain and persistence models
    schemas/         validated transport contracts
    middleware/      HTTP cross-cutting controls
    core/            application composition and failure mapping
    config/          typed environment configuration
    security/        authentication/authorization adapters (Phase 2)
    database/        DynamoDB composition (Phase 3)
    logs/            structured, redacted observability
    utils/           small framework-independent helpers
  tests/
    unit/ integration/ contract/ security/
  scripts/
```

Domain and application code must not import FastAPI request types, boto3 clients, DynamoDB documents, or environment settings. Infrastructure is composed at the application boundary and all feature modules remain independently testable.

## AWS entry point

`app.main.handler` is the Lambda handler exported through Mangum. API Gateway, Lambda, DynamoDB, IAM, KMS, Secrets Manager, WAF, and CloudWatch resources will be composed in their approved infrastructure phase; local defaults do not substitute for those production controls.
