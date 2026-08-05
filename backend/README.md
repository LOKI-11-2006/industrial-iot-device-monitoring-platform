# ForgeSight backend

Production-oriented Python 3.12 and FastAPI control plane for the ForgeSight Industrial IoT Device Management and Predictive Monitoring Platform.

## Current delivery gate

Backend Phase 2 adds the complete human authentication and base authorization boundary:

- Argon2id password hashing with adaptive rehash support and unknown-user timing work
- asymmetric 15-minute access JWTs with issuer, audience, key ID, session, role and version claims
- opaque HTTP-only refresh credentials, hashed storage, rotation and family-wide reuse revocation
- live server-side session and user-state verification for every protected request
- login throttling, temporary lockout and non-enumerating credential/reset responses
- single-use expiring password resets that revoke all existing sessions
- logout, logout-all, owned-session listing/revocation and current-user identity endpoints
- six approved roles, centralized permission vocabulary and default-deny factory-scope dependencies
- separate structured authentication/security evidence with credential-safe redaction
- strict request schemas, canonical problem responses and executable OpenAPI security contracts

DynamoDB data models and durable repository adapters are intentionally excluded until Backend Phase 3 is approved. The Phase 2 in-memory adapter exists only for local composition and tests; production composition requires an explicitly injected durable adapter.

## Requirements

- Python 3.12 or newer (Python 3.13 is supported; Python 3.14 is not yet targeted)
- pip 25 or newer
- AWS credentials are not required for local Phase 2 tests

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

Local composition uses one process-local asymmetric signing key and an empty in-memory identity store. Tests seed identities through the repository port; no demo credentials or passwords are embedded in the application. Backend Phase 3 supplies the durable DynamoDB identity/session adapter and Backend Phase 4 supplies user-management workflows.

## Authentication API

| Method | Path | Access |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Public, throttled and lockout protected |
| `POST` | `/api/v1/auth/refresh` | Rotating HTTP-only refresh cookie |
| `POST` | `/api/v1/auth/logout` | Authenticated current session |
| `POST` | `/api/v1/auth/logout-all` | Authenticated current user |
| `POST` | `/api/v1/auth/password-reset/request` | Public, non-enumerating and throttled |
| `POST` | `/api/v1/auth/password-reset/confirm` | Single-use reset credential |
| `GET` | `/api/v1/me` | Authenticated live identity/permissions/scopes |
| `GET` | `/api/v1/me/sessions` | Authenticated owned sessions |
| `DELETE` | `/api/v1/me/sessions/{session_id}` | Authenticated session owner |
| `GET` | `/api/v1/roles` | Authenticated safe role catalog |

## Configuration and secrets

Configuration is read from process environment variables prefixed with `IOT_API_`; a local `.env` file is optional. List settings accept JSON arrays or comma-separated values. Unknown configuration keys are rejected so misspellings cannot silently weaken runtime behavior.

Production configuration enforces HTTPS CORS origins and refresh cookies, disables debug and public API documentation, disallows local AWS endpoints and wildcard hosts/origins, and requires a Secrets Manager ARN for JWT signing material. Key material and AWS credentials must never be stored in `.env`, source control, logs, or frontend code.

The referenced Secrets Manager value is a JSON object with `activeKid`, `algorithm` (`ES256` or `RS256`), `privateKeyPem`, a rotation-aware `publicKeys` object keyed by `kid`, and a base64url `tokenHashPepper` of at least 32 bytes. Startup verifies algorithm/key type, minimum strength, active public/private matching and rotation-key availability before accepting traffic.

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
    security/        password, JWT, opaque token and authorization policy adapters
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

## Phase gate

Backend Phase 2 stops here for review. Database models, DynamoDB repositories and migrations belong to Backend Phase 3 and must not begin until explicit approval.
