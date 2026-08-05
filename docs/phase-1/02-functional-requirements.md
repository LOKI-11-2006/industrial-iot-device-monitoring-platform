# 2. Functional Requirements

Priority meanings: **P0** is required for the first production-like release, **P1** is important but may follow core acceptance, and **P2** is an approved extension.

## 2.1 Authentication and sessions

| ID | Pri | Requirement |
|---|---:|---|
| FR-AUTH-01 | P0 | The system shall authenticate active users using verified credentials and issue short-lived JWT access tokens. |
| FR-AUTH-02 | P0 | The system shall rotate refresh tokens and detect reuse of a previously rotated token. |
| FR-AUTH-03 | P0 | The system shall terminate sessions on logout, password reset, user disablement, or security revocation. |
| FR-AUTH-04 | P0 | The system shall enforce configurable login throttling and temporary lockout without revealing whether an account exists. |
| FR-AUTH-05 | P0 | The system shall record successful and failed authentication events separately from general application logs. |
| FR-AUTH-06 | P0 | The system shall return the current user's profile, permissions, factory scopes, and active sessions. |
| FR-AUTH-07 | P1 | The system shall support secure password-reset initiation and single-use expiration-controlled reset tokens. |
| FR-AUTH-08 | P1 | The system shall allow a user or administrator to revoke selected sessions. |

## 2.2 Users, roles, and factory scope

| ID | Pri | Requirement |
|---|---:|---|
| FR-USR-01 | P0 | A super administrator shall create, read, update, disable, and restore user accounts. |
| FR-USR-02 | P0 | Authorized administrators shall assign exactly one platform role and one or more permitted factories to a user. |
| FR-USR-03 | P0 | Every protected request shall enforce both permission and factory scope on the server. |
| FR-USR-04 | P0 | The system shall prevent an administrator from granting permissions or factory scope beyond their own authority. |
| FR-USR-05 | P0 | User lists shall support server-side search, role/status filters, sorting, and cursor pagination. |
| FR-USR-06 | P1 | Users shall manage their profile, time zone, display preferences, and notification preferences. |
| FR-USR-07 | P1 | Administrators shall review a user's role, factory assignments, session state, and recent audited activity. |

## 2.3 Factory management

| ID | Pri | Requirement |
|---|---:|---|
| FR-FAC-01 | P0 | Authorized users shall create and maintain factory identity, location, time zone, status, and operating metadata. |
| FR-FAC-02 | P0 | Factory lists and details shall be restricted to the requester's scope. |
| FR-FAC-03 | P0 | A factory detail shall summarize devices, online state, health, alerts, energy use, and recent activity. |
| FR-FAC-04 | P0 | A factory with active devices shall not be hard-deleted; archival must preserve history. |
| FR-FAC-05 | P1 | Administrators shall configure factory-level telemetry thresholds and offline freshness defaults. |
| FR-FAC-06 | P1 | The system shall compare authorized factories using normalized operational KPIs. |

## 2.4 Device lifecycle and identity

| ID | Pri | Requirement |
|---|---:|---|
| FR-DEV-01 | P0 | Authorized users shall register a device with factory, machine type, unique name, serial number, tags, and metadata. |
| FR-DEV-02 | P0 | Device provisioning shall create or associate a unique IoT identity and least-privilege policy. |
| FR-DEV-03 | P0 | The system shall expose credential material only through an explicit secure provisioning workflow and never in later reads. |
| FR-DEV-04 | P0 | Authorized users shall activate, deactivate, quarantine, archive, and transfer devices according to policy. |
| FR-DEV-05 | P0 | The system shall show last accepted telemetry, connection state, health score, certificate state, and open alerts per device. |
| FR-DEV-06 | P0 | Device lists shall support factory, type, status, health, tag, and certificate filters with cursor pagination. |
| FR-DEV-07 | P0 | Configuration changes shall be versioned and audited, with the desired and reported state distinguished. |
| FR-DEV-08 | P0 | Certificate expiry, rotation, revocation, and provisioning status shall be visible in the security center. |
| FR-DEV-09 | P1 | Authorized users shall create and apply reusable device configuration profiles. |
| FR-DEV-10 | P1 | Bulk import shall validate every row and report partial failures without silently skipping records. |
| FR-DEV-11 | P1 | Maintenance engineers shall record maintenance notes and lifecycle events against a device. |

## 2.5 Telemetry ingestion and live monitoring

| ID | Pri | Requirement |
|---|---:|---|
| FR-TEL-01 | P0 | Devices shall publish temperature, humidity, pressure, vibration, voltage, current, RPM, power, health, status, and event timestamp over MQTT/TLS. |
| FR-TEL-02 | P0 | The ingestion path shall authenticate the certificate, authorize the topic, validate schema, and reject malformed or unauthorized messages. |
| FR-TEL-03 | P0 | Accepted events shall receive an ingestion timestamp, schema version, quality state, and correlation identifier. |
| FR-TEL-04 | P0 | Duplicate events shall be idempotently handled using device and event identifiers. |
| FR-TEL-05 | P0 | The platform shall retain raw operational telemetry for the configured period and create coarser rollups for longer-range queries. |
| FR-TEL-06 | P0 | The UI shall display the latest values and connection state without requiring a full page reload. |
| FR-TEL-07 | P0 | Historical telemetry queries shall support metric selection, time range, aggregation interval, and cursor pagination. |
| FR-TEL-08 | P0 | A freshness evaluator shall mark stale devices offline and emit a deduplicated disconnect alert. |
| FR-TEL-09 | P1 | Devices shall support bounded store-and-forward replay using original timestamps and sequence numbers. |
| FR-TEL-10 | P1 | The platform shall expose rejected-message counts and reasons without leaking sensitive payloads. |

## 2.6 Analytics and health

| ID | Pri | Requirement |
|---|---:|---|
| FR-ANA-01 | P0 | The dashboard shall show factory count; total, online, offline, and critical devices; today's alerts; health distribution; and average environmental/power metrics. |
| FR-ANA-02 | P0 | Analytics shall provide temperature, humidity, pressure, power, utilization, factory performance, alert timeline, energy, and connectivity views. |
| FR-ANA-03 | P0 | The system shall calculate an explainable device health score from freshness, threshold breaches, anomaly state, and machine status. |
| FR-ANA-04 | P0 | Users shall drill from organization to factory to device while retaining time-range context. |
| FR-ANA-05 | P0 | Aggregations shall declare unit, time zone, interval, population, and last-updated time. |
| FR-ANA-06 | P1 | The system shall identify top faulty and highest-energy devices within authorized scope. |
| FR-ANA-07 | P1 | Authorized users shall compare current metrics with a previous equivalent period. |

## 2.7 Alerts and notifications

| ID | Pri | Requirement |
|---|---:|---|
| FR-ALT-01 | P0 | The rules engine shall create alerts for threshold breach, degraded health, disconnect, authentication failure, and certificate expiry. |
| FR-ALT-02 | P0 | Rules shall support metric/operator/threshold, duration, severity, hysteresis, cooldown, factory/device scope, and enabled state. |
| FR-ALT-03 | P0 | Equivalent active conditions shall be deduplicated into one alert with occurrence tracking. |
| FR-ALT-04 | P0 | Authorized users shall acknowledge, assign, comment on, and resolve alerts. |
| FR-ALT-05 | P0 | Every alert transition shall preserve actor, timestamp, prior state, new state, and note. |
| FR-ALT-06 | P0 | Alert lists shall filter by factory, device, severity, status, rule, assignee, and time range. |
| FR-ALT-07 | P0 | The system shall deliver configured notifications through in-app channels and Amazon SNS. |
| FR-ALT-08 | P0 | Delivery attempts, provider identifiers, and terminal delivery failures shall be traceable. |
| FR-ALT-09 | P1 | Users shall configure channel, severity, factory, and quiet-hour preferences within policy. |
| FR-ALT-10 | P1 | Administrators shall test a notification route without creating a production alert. |

## 2.8 Reports and exports

| ID | Pri | Requirement |
|---|---:|---|
| FR-REP-01 | P0 | Authorized users shall request factory health, device health, telemetry, energy, alert, and audit reports. |
| FR-REP-02 | P0 | Report generation shall run asynchronously and expose queued, processing, completed, expired, and failed states. |
| FR-REP-03 | P0 | Generated files shall be stored encrypted in S3 and downloaded through short-lived authorized URLs. |
| FR-REP-04 | P0 | A report shall record request filters, requesting user, factory scope, creation time, expiry, checksum, and outcome. |
| FR-REP-05 | P1 | Users shall schedule recurring reports within their current authorization scope. |
| FR-REP-06 | P1 | Exported timestamps, units, and filters shall be explicitly labeled. |

## 2.9 Audit, security, and platform operations

| ID | Pri | Requirement |
|---|---:|---|
| FR-OPS-01 | P0 | Audit events shall record actor, action, resource, scope, result, before/after summary, source, time, and correlation ID. |
| FR-OPS-02 | P0 | Audit records shall be queryable but not editable through application APIs. |
| FR-OPS-03 | P0 | Security events shall classify authentication, authorization, certificate, input, and suspicious-activity signals. |
| FR-OPS-04 | P0 | The security center shall summarize certificate expiry, quarantined devices, failed authentication, and unresolved security findings. |
| FR-OPS-05 | P0 | Application health shall expose dependency-aware readiness, liveness, version, and non-sensitive build information. |
| FR-OPS-06 | P0 | CloudWatch dashboards and alarms shall cover API errors/latency, Lambda failures/throttles, IoT rejection, DynamoDB throttling, queue age, and notification failure. |
| FR-OPS-07 | P0 | Administrators shall manage system thresholds, retention settings, and notification defaults subject to validation and audit. |
| FR-OPS-08 | P1 | Authorized users shall export scoped audit records through the controlled report process. |

## 2.10 Simulator requirements

| ID | Pri | Requirement |
|---|---:|---|
| FR-SIM-01 | P0 | The simulator shall model at least 20 independently identified devices across realistic machine types. |
| FR-SIM-02 | P0 | Values shall be correlated and physically plausible rather than uniformly random. |
| FR-SIM-03 | P0 | The simulator shall support normal, warning, critical, disconnect, recovery, and credential-failure scenarios. |
| FR-SIM-04 | P0 | Each simulated device shall use its own identity and publish the production telemetry schema. |
| FR-SIM-05 | P0 | Scenario execution shall be deterministic when a seed is supplied and observable through structured logs. |
| FR-SIM-06 | P1 | Publish rate, jitter, factory assignment, scenario, and duration shall be configurable without source changes. |

## 2.11 Cross-cutting acceptance rules

- Every list API uses server-side authorization, bounded page size, deterministic order, and cursor pagination.
- Every state-changing API supports correlation IDs and appropriate idempotency controls.
- Every user-visible error uses a stable error code and safe message; internal details remain in structured logs.
- Every P0 requirement must map to at least one automated test or documented operational verification before deployment approval.
