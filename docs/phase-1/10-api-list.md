# 10. API List

## 10.1 Contract conventions

- Base URL: `/api/v1`
- Media type: `application/json`; errors: `application/problem+json`
- Authentication: `Authorization: Bearer <access-token>` except explicitly public authentication/health endpoints
- Time: ISO 8601 UTC; duration/ranges have documented limits
- Pagination: `limit` plus opaque `cursor`; default 25, maximum 100
- Filters: allowlisted per endpoint; unknown filters are rejected
- Concurrency: resource `version` and `If-Match` for sensitive updates
- Idempotency: `Idempotency-Key` for retry-sensitive `POST` operations
- Observability: caller may supply `X-Correlation-ID`; server validates or replaces it and returns the effective ID
- Download endpoints issue short-lived links; they do not stream arbitrary S3 object keys supplied by callers

Common error codes include `AUTHENTICATION_REQUIRED`, `TOKEN_EXPIRED`, `SESSION_REVOKED`, `PERMISSION_DENIED`, `FACTORY_SCOPE_DENIED`, `RESOURCE_NOT_FOUND`, `VALIDATION_FAILED`, `VERSION_CONFLICT`, `IDEMPOTENCY_CONFLICT`, `RATE_LIMITED`, and `DEPENDENCY_UNAVAILABLE`.

## 10.2 Authentication and current user

| Method | Path | Purpose | Access |
|---|---|---|---|
| POST | `/auth/login` | Verify credentials and create token/session family | Public, throttled |
| POST | `/auth/refresh` | Rotate refresh token and issue new access token | Refresh credential |
| POST | `/auth/logout` | Revoke current session | Authenticated |
| POST | `/auth/logout-all` | Revoke all sessions for current user | Authenticated |
| POST | `/auth/password-reset/request` | Start non-enumerating reset flow | Public, throttled |
| POST | `/auth/password-reset/confirm` | Consume one-time reset token | Public token |
| GET | `/me` | Current profile, role, permissions, scopes, preferences | Authenticated |
| PATCH | `/me` | Update permitted profile fields | Authenticated |
| GET | `/me/sessions` | List active/recent sessions | Authenticated |
| DELETE | `/me/sessions/{sessionId}` | Revoke one owned session | Authenticated |
| GET | `/me/notification-preferences` | Read notification preferences | Authenticated |
| PUT | `/me/notification-preferences` | Replace validated preferences | Authenticated |

## 10.3 Users and access assignments

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/users` | Search/filter scoped users | `users:read` |
| POST | `/users` | Create user and initial assignments | `users:create` |
| GET | `/users/{userId}` | Get profile, role, scope, status | `users:read` |
| PATCH | `/users/{userId}` | Update allowed identity/profile fields | `users:update` |
| POST | `/users/{userId}/disable` | Disable user and revoke sessions | `users:disable` |
| POST | `/users/{userId}/restore` | Restore eligible disabled user | `users:update` |
| PUT | `/users/{userId}/role` | Change role subject to grant rules | `users:assign_scope` |
| PUT | `/users/{userId}/factories` | Replace factory assignments within grantor scope | `users:assign_scope` |
| GET | `/users/{userId}/sessions` | View security-relevant sessions | `users:read` plus policy |
| DELETE | `/users/{userId}/sessions/{sessionId}` | Revoke user session | `users:disable` or security policy |
| GET | `/users/{userId}/activity` | Read scoped recent activity | `users:read` plus log policy |
| GET | `/roles` | List role definitions and permissions | Authenticated |

## 10.4 Factories

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/factories` | List authorized factories | `factories:read` |
| POST | `/factories` | Create factory | `factories:create` |
| GET | `/factories/{factoryId}` | Get factory profile and summary | `factories:read` |
| PATCH | `/factories/{factoryId}` | Update metadata | `factories:update` |
| POST | `/factories/{factoryId}/archive` | Archive eligible factory | `factories:archive` |
| POST | `/factories/{factoryId}/restore` | Restore archived factory | `factories:update` |
| GET | `/factories/{factoryId}/settings` | Read factory defaults | `settings:read` |
| PUT | `/factories/{factoryId}/settings` | Update versioned defaults | `settings:manage_factory` |
| GET | `/factories/{factoryId}/summary` | Current device/health/alert/energy KPIs | `factories:read` |
| GET | `/factories/compare` | Compare selected authorized factories | `analytics:read` |

## 10.5 Devices, certificates, configuration, and maintenance

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/devices` | List/filter authorized devices | `devices:read` |
| POST | `/devices` | Register a device | `devices:create` |
| GET | `/devices/{deviceId}` | Device profile and current posture | `devices:read` |
| PATCH | `/devices/{deviceId}` | Update metadata/tags | `devices:update` |
| POST | `/devices/{deviceId}/archive` | Archive eligible device | `devices:update` |
| POST | `/devices/{deviceId}/restore` | Restore device | `devices:update` |
| POST | `/devices/{deviceId}/transfer` | Transfer to another authorized factory | `devices:transfer` |
| POST | `/devices/{deviceId}/quarantine` | Quarantine and restrict device | `devices:quarantine` |
| POST | `/devices/{deviceId}/unquarantine` | Remove quarantine after validation | `devices:quarantine` |
| POST | `/devices/{deviceId}/provision` | Create IoT identity and one-time credential package | `devices:provision` |
| GET | `/devices/{deviceId}/certificates` | List certificate metadata/status | `devices:read` plus security policy |
| POST | `/devices/{deviceId}/certificates/rotate` | Begin bounded certificate rotation | `certificates:rotate` |
| POST | `/devices/{deviceId}/certificates/{certificateId}/revoke` | Revoke certificate | `certificates:revoke` |
| GET | `/devices/{deviceId}/configuration` | Read desired/reported/current configuration | `devices:read` |
| PUT | `/devices/{deviceId}/configuration/desired` | Create next desired configuration version | `devices:configure` |
| GET | `/devices/{deviceId}/configuration/history` | Read version history | `devices:read` |
| GET | `/devices/{deviceId}/maintenance` | List maintenance events | `devices:read` |
| POST | `/devices/{deviceId}/maintenance` | Add maintenance event/note | maintenance policy |
| POST | `/devices/imports` | Submit validated bulk-registration job | `devices:create` |
| GET | `/devices/imports/{jobId}` | Get import validation/results | `devices:create` |

## 10.6 Telemetry and live monitoring

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/devices/{deviceId}/telemetry/latest` | Latest canonical metrics and freshness | `telemetry:read` |
| GET | `/devices/{deviceId}/telemetry` | Raw or aggregated metric series for bounded range | `telemetry:read` |
| GET | `/devices/{deviceId}/telemetry/quality` | Missing/replay/skew/schema quality summary | `telemetry:read` |
| GET | `/factories/{factoryId}/monitoring` | Current state grid for factory devices | `telemetry:read` |
| GET | `/monitoring/critical` | Critical/offline devices across authorized scope | `telemetry:read` |
| POST | `/realtime/tickets` | Mint short-lived scoped WebSocket connection ticket | Authenticated |
| GET | `/realtime/connection-info` | Return authorized WebSocket URL and heartbeat policy | Authenticated |

Devices do not publish telemetry through these human APIs. MQTT topics and payloads are documented separately in the future AsyncAPI contract.

## 10.7 Dashboard and analytics

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/dashboard` | Role/scope-aware dashboard composition | `analytics:read` |
| GET | `/analytics/metric-trends` | Temperature/humidity/pressure trends | `analytics:read` |
| GET | `/analytics/power` | Power and energy time series | `analytics:read` |
| GET | `/analytics/utilization` | Device utilization by time/factory/type | `analytics:read` |
| GET | `/analytics/factory-performance` | Normalized factory KPI series/ranking | `analytics:read` |
| GET | `/analytics/alerts-timeline` | Alert occurrence/status trends | `analytics:read` |
| GET | `/analytics/faulty-devices` | Ranked degraded/faulty devices | `analytics:read` |
| GET | `/analytics/health-distribution` | Health bands by scope and time | `analytics:read` |
| GET | `/analytics/connectivity` | Online/offline duration and transitions | `analytics:read` |

Required query parameters vary by endpoint but use `factoryId`, `deviceId`, `from`, `to`, `interval`, `metric`, `compare`, and `timeZone` only when defined. Servers enforce maximum time ranges and permitted scopes.

## 10.8 Alerts and rules

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/alerts` | Filtered alert inbox | `alerts:read` |
| GET | `/alerts/{alertId}` | Alert details, rule context, and current state | `alerts:read` |
| GET | `/alerts/{alertId}/events` | Immutable alert timeline | `alerts:read` |
| POST | `/alerts/{alertId}/acknowledge` | Acknowledge with note | `alerts:acknowledge` |
| POST | `/alerts/{alertId}/assign` | Assign/unassign an eligible user | `alerts:assign` |
| POST | `/alerts/{alertId}/resolve` | Resolve with reason and note | `alerts:resolve` |
| POST | `/alerts/{alertId}/comments` | Add investigation comment | operational alert permission |
| POST | `/alerts/{alertId}/suppress` | Time-bound maintenance suppression | elevated alert policy |
| GET | `/alert-rules` | List rules in authorized scope | `alert_rules:read` |
| POST | `/alert-rules` | Create validated rule | `alert_rules:manage` |
| GET | `/alert-rules/{ruleId}` | Rule and recent evaluation summary | `alert_rules:read` |
| PATCH | `/alert-rules/{ruleId}` | Update rule with version check | `alert_rules:manage` |
| POST | `/alert-rules/{ruleId}/enable` | Enable rule | `alert_rules:manage` |
| POST | `/alert-rules/{ruleId}/disable` | Disable rule | `alert_rules:manage` |
| POST | `/alert-rules/{ruleId}/test` | Evaluate sample/current values without opening alert | `alert_rules:manage` |

## 10.9 Notifications

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/notification-channels` | List configured safe channel metadata | `settings:read` |
| POST | `/notification-channels` | Create/verify an allowed channel | `settings:manage_factory` |
| PATCH | `/notification-channels/{channelId}` | Update enabled routing metadata | `settings:manage_factory` |
| DELETE | `/notification-channels/{channelId}` | Disable/remove eligible channel | `settings:manage_factory` |
| POST | `/notification-channels/{channelId}/test` | Send marked test message | `settings:manage_factory` |
| GET | `/notifications` | In-app notification inbox | Authenticated |
| POST | `/notifications/{notificationId}/read` | Mark owned in-app notification read | Authenticated |

## 10.10 Reports

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/reports` | List report jobs in authorized scope | `reports:read` |
| POST | `/reports` | Request asynchronous report | `reports:create` |
| GET | `/reports/{reportId}` | Job metadata/status | `reports:read` |
| POST | `/reports/{reportId}/retry` | Retry eligible failed job idempotently | `reports:create` |
| DELETE | `/reports/{reportId}` | Expire/delete eligible report object, retaining audit metadata | owner/admin policy |
| POST | `/reports/{reportId}/download-ticket` | Create short-lived authorized download | `reports:read` |
| GET | `/report-schedules` | List schedules | `reports:read` |
| POST | `/report-schedules` | Create schedule | `reports:schedule` |
| PATCH | `/report-schedules/{scheduleId}` | Update/enable/disable schedule | `reports:schedule` |
| DELETE | `/report-schedules/{scheduleId}` | Remove schedule | `reports:schedule` |

## 10.11 Audit, activity, security, and settings

| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/audit-events` | Query immutable scoped audit evidence | `audit:read` |
| GET | `/audit-events/{eventId}` | Read one audit event with safe detail | `audit:read` |
| GET | `/activity-events` | Read user-facing scoped activity timeline | activity policy |
| GET | `/security/overview` | Security posture summary | `security:read` |
| GET | `/security/events` | Query security/authentication events | `security:read` |
| GET | `/security/certificates` | Filter certificate inventory/expiry | `security:read` |
| GET | `/security/quarantined-devices` | List quarantined devices | `security:read` |
| POST | `/security/events/{eventId}/review` | Record investigation disposition | `security:manage` |
| GET | `/settings/platform` | Read safe platform settings | `settings:read` plus platform policy |
| PUT | `/settings/platform` | Update versioned platform settings | `settings:manage_platform` |
| GET | `/settings/catalog` | Allowed units, machine types, severities, and enums | Authenticated |

## 10.12 Platform health and metadata

| Method | Path | Purpose | Access |
|---|---|---|---|
| GET | `/health/live` | Process liveness only | Public, minimal |
| GET | `/health/ready` | Dependency-aware readiness without sensitive details | Restricted edge/operations |
| GET | `/version` | Safe build/version metadata | Authenticated or operations policy |
| GET | `/platform-health` | Operational dashboard projection | `platform_health:read` |
| GET | `/platform-health/incidents` | Recent platform incidents/degradations | `platform_health:read` |

## 10.13 Representative response shapes

List response:

```json
{
  "items": [],
  "page": {
    "nextCursor": null,
    "limit": 25
  },
  "meta": {
    "correlationId": "corr_...",
    "generatedAt": "2026-08-05T10:00:00Z"
  }
}
```

Problem response:

```json
{
  "type": "https://docs.example.invalid/problems/factory-scope-denied",
  "title": "Factory access denied",
  "status": 403,
  "code": "FACTORY_SCOPE_DENIED",
  "detail": "You do not have access to the requested resource.",
  "instance": "/api/v1/devices/dev_...",
  "correlationId": "corr_..."
}
```

The final OpenAPI specification in the backend phase is the executable source of truth and must remain consistent with this inventory.
