# 8. Database Design

## 8.1 Design approach

DynamoDB design begins with access patterns, not entity diagrams. The platform uses a small set of purpose-specific tables so high-volume telemetry, operational aggregates, core configuration, and immutable evidence can scale and retain independently.

Principles:

- no unbounded `Scan` in an API request;
- high-cardinality write traffic is time-bucketed;
- current-state projections avoid repeated raw time-series queries;
- denormalized names/statuses are accepted when they remove joins, with controlled update fan-out;
- conditional writes and transactions enforce invariants;
- soft archival preserves referential history;
- TTL is for expiry/cost management, not an exact deletion scheduler;
- DynamoDB Streams/outbox records feed projections and archives without coupling writes to every consumer.

## 8.2 Tables

| Table | Purpose | Capacity | Protection/retention |
|---|---|---|---|
| `iot-core-{env}` | Users, factories, devices, rules, alerts, settings, sessions, jobs, idempotency, outbox | On-demand initially | PITR, KMS, backups, no TTL except ephemeral items |
| `iot-telemetry-{env}` | Raw validated device telemetry | On-demand; evaluate per-key load | KMS, 30-day TTL baseline, stream as needed |
| `iot-aggregates-{env}` | Latest state plus hourly/daily metrics and KPI projections | On-demand | PITR, KMS, 13-month aggregate retention |
| `iot-events-{env}` | Queryable audit, security, authentication, activity, and device lifecycle events | On-demand | PITR, KMS, hot retention by class; immutable S3 archive |

## 8.3 Common attributes

All records include:

| Attribute | Meaning |
|---|---|
| `pk`, `sk` | Primary key strings with typed prefixes |
| `entityType` | Stable record discriminator |
| `schemaVersion` | Integer schema version |
| `createdAt`, `updatedAt` | ISO 8601 UTC timestamps where applicable |
| `version` | Monotonic integer for optimistic concurrency |
| `factoryId` | Denormalized authorization boundary where applicable |
| `ttl` | Unix epoch seconds only for expiring records |

IDs are server-generated UUIDv7/ULID-style sortable identifiers. Human names and serial numbers are not primary keys because they can change and may contain unsafe characters.

## 8.4 Core table item design

| Entity/item | `pk` | `sk` | Important attributes / indexes |
|---|---|---|---|
| User profile | `USER#{userId}` | `PROFILE` | email, normalizedEmail, role, status, passwordHash, tokenVersion; GSI1 `EMAIL#{normalizedEmail}`/`USER` |
| User factory assignment | `USER#{userId}` | `FACTORY#{factoryId}` | assignedBy, assignedAt; reverse GSI2 `FACTORY#{factoryId}`/`USER#{userId}` |
| Refresh session | `USER#{userId}` | `SESSION#{sessionId}` | tokenHash, familyId, expiry, revokedAt, client metadata; TTL |
| Factory | `FACTORY#{factoryId}` | `PROFILE` | name, location, timeZone, status; GSI1 `FACTORY_STATUS#{status}`/`NAME#{normalizedName}#{factoryId}` |
| Factory settings | `FACTORY#{factoryId}` | `SETTINGS` | freshness window, units, threshold defaults, notification defaults |
| Device profile | `DEVICE#{deviceId}` | `PROFILE` | factoryId, name, type, serial, status, tags, IoT thing, certificate status; GSI1 `FACTORY#{factoryId}`/`DEVICE#{status}#{deviceId}` |
| Device serial uniqueness | `UNIQUE#DEVICE_SERIAL#{normalizedSerial}` | `LOCK` | deviceId; conditionally created |
| Device config version | `DEVICE#{deviceId}` | `CONFIG#{zeroPaddedVersion}` | desired config, changedBy, change reason |
| Device certificate metadata | `DEVICE#{deviceId}` | `CERT#{certificateId}` | ARN, status, issuedAt, expiresAt; private key is never stored |
| Maintenance event | `DEVICE#{deviceId}` | `MAINT#{timestamp}#{eventId}` | eventType, note, actorId |
| Alert | `ALERT#{alertId}` | `PROFILE` | factoryId, deviceId, ruleId, severity, status, assignee, openedAt; GSI1 `FACTORY#{factoryId}`/`ALERT#{status}#{reverseTime}#{alertId}` |
| Alert event | `ALERT#{alertId}` | `EVENT#{timestamp}#{eventId}` | event type, actor, prior/new state, note |
| Active alert dedupe lock | `DEDUPE#ALERT#{dedupeKey}` | `ACTIVE` | alertId, cooldownUntil; conditional create/update |
| Alert rule | `FACTORY#{factoryId}` | `RULE#{ruleId}` | metric, operator, thresholds, duration, hysteresis, cooldown, severity, scope, enabled; GSI2 `RULE#{ruleId}`/`PROFILE` |
| Rule evaluation state | `DEVICE#{deviceId}` | `RULESTATE#{ruleId}` | breachSince, lastValue, activeAlertId, cooldownUntil |
| Report job | `USER#{userId}` | `REPORT#{createdAt}#{reportId}` | type, scope snapshot, filters, status, objectKey, expiry; GSI2 `REPORT#{reportId}`/`PROFILE` |
| Report schedule | `FACTORY#{factoryId}` | `REPORTSCHEDULE#{scheduleId}` | type, cadence, recipients, filters, enabled |
| Idempotency record | `IDEMPOTENCY#{actorId}` | `KEY#{requestKey}` | requestHash, status, responseRef, expiry; TTL |
| Outbox event | `OUTBOX#{shard}` | `EVENT#{createdAt}#{eventId}` | eventType, payload reference, attempts, status; GSI by status/time |
| Platform setting | `PLATFORM` | `SETTING#{settingName}` | value, classification, updatedBy, version |

Exact GSI names may be refined from load tests, but the access patterns and authorization boundaries are fixed.

## 8.5 Telemetry table

### Primary key

```text
pk = DEVICE#{deviceId}#DAY#{yyyyMMdd}
sk = TS#{eventTimeIso}#EVENT#{eventId}
```

This supports device/time queries while distributing a device's long-term history across daily partitions. If a future high-frequency device exceeds a daily partition's safe write profile, the bucket can include an hour or stable shard without changing the public API.

### Attributes

```json
{
  "deviceId": "dev_...",
  "factoryId": "fac_...",
  "eventId": "evt_...",
  "sequence": 1052,
  "eventTime": "2026-08-05T09:30:00.000Z",
  "ingestedAt": "2026-08-05T09:30:00.417Z",
  "schemaVersion": 1,
  "metrics": {
    "temperatureC": 72.4,
    "humidityPct": 46.1,
    "pressureKpa": 510.2,
    "vibrationMmS": 3.2,
    "voltageV": 415.0,
    "currentA": 12.7,
    "rpm": 1480,
    "powerKw": 8.9
  },
  "machineHealthPct": 91,
  "machineState": "RUNNING",
  "quality": "GOOD",
  "ttl": 1788500000
}
```

The example defines the contract shape, not production fixture data.

### Secondary index

For factory/time operational exports:

```text
gsi1pk = FACTORY#{factoryId}#DAY#{yyyyMMdd}#SHARD#{00..N}
gsi1sk = TS#{eventTimeIso}#DEVICE#{deviceId}#EVENT#{eventId}
```

Factory-wide dashboards use aggregates rather than this raw index. The index exists for bounded exports/investigation and uses stable sharding to avoid a hot factory partition.

### Idempotency

The primary key includes `eventId`, and ingestion also conditionally advances the latest projection using sequence/event time. A repeated identical event becomes a no-op. A reused event ID with different payload hash is rejected and logged as a security/data-quality event.

## 8.6 Aggregate and latest-state table

| Projection | `pk` | `sk` | Use |
|---|---|---|---|
| Device latest | `DEVICE#{deviceId}` | `LATEST` | Current metrics, last event/ingestion, online, health, active-alert counts |
| Device hourly metric | `DEVICE#{deviceId}` | `HOUR#{yyyyMMddHH}#METRIC#{metric}` | count, min, max, sum, average, quality counts |
| Device daily metric | `DEVICE#{deviceId}` | `DAY#{yyyyMMdd}#METRIC#{metric}` | Long-range trends |
| Factory latest KPI | `FACTORY#{factoryId}` | `LATEST` | device/health/alert counts and current averages |
| Factory hourly KPI | `FACTORY#{factoryId}` | `HOUR#{yyyyMMddHH}` | energy, utilization, health and alert aggregates |
| Organization dashboard | `PLATFORM` | `DASHBOARD#LATEST` | bounded cross-factory summary for super administrators |

Aggregation workers use idempotent bucket updates and reconciliation checks. Counts that must remain exact use transactional state transitions or periodic rebuilds; approximate near-real-time metrics are labeled with last-updated timestamps.

## 8.7 Events table

```text
pk = SCOPE#{factoryId-or-PLATFORM}#MONTH#{yyyyMM}#SHARD#{0..N}
sk = TS#{eventTimeIso}#EVENT#{eventId}
```

Event attributes include:

- `eventClass`: `AUDIT`, `SECURITY`, `AUTHENTICATION`, `ACTIVITY`, `DEVICE`;
- `actorType`, `actorId`, `sessionId`;
- `action`, `resourceType`, `resourceId`, `factoryId`;
- `result`, `reasonCode`, safe before/after summaries;
- `sourceIpHash` or controlled source metadata, user agent category;
- `correlationId`, `requestId`, event timestamp, ingestion timestamp;
- classification and archive status.

Indexes:

```text
gsi1pk = ACTOR#{actorId}#MONTH#{yyyyMM}
gsi1sk = TS#{eventTimeIso}#EVENT#{eventId}

gsi2pk = RESOURCE#{resourceType}#{resourceId}
gsi2sk = TS#{eventTimeIso}#EVENT#{eventId}
```

Application APIs expose query-only access. A stream delivers immutable copies to an S3 archive with object lock where the account supports it. CloudTrail remains separate AWS administrative evidence.

## 8.8 Principal access patterns

| # | Access pattern | Table/index |
|---:|---|---|
| 1 | Authenticate by normalized email | Core GSI1 email key |
| 2 | Load user profile, assignments, and sessions | Core user partition |
| 3 | List users assigned to a factory | Core GSI2 factory/user |
| 4 | List factories by status/name | Core factory status GSI |
| 5 | Get device by ID | Core device partition/profile |
| 6 | List devices for factory filtered by status | Core GSI1 factory/device |
| 7 | Load device config and certificate history | Core device partition SK ranges |
| 8 | Query raw telemetry for one device/time range | Telemetry daily partitions |
| 9 | Query bounded factory raw export | Telemetry sharded factory GSI |
| 10 | Read device live state | Aggregates device/latest |
| 11 | Read device or factory trend | Aggregates bucket SK range |
| 12 | List factory alerts by status/newest | Core GSI1 factory/alert |
| 13 | Load alert with full timeline | Core alert partition |
| 14 | Prevent duplicate active alerts | Core conditional dedupe item |
| 15 | List/query audit events by factory/time | Events scope/month shards |
| 16 | Investigate events by actor or resource | Events GSI1/GSI2 |
| 17 | List a user's report jobs | Core user/report SK range |
| 18 | Resume async work/outbox | Core status/time GSI |

## 8.9 Consistency and transactions

- Strongly consistent reads are reserved for security-critical immediate checks such as a just-changed session or uniqueness lock when necessary.
- Eventually consistent reads are acceptable for dashboards and historical analytics with displayed freshness.
- `TransactWriteItems` is used for invariants spanning a small bounded set of items: device registration plus serial lock, alert transition plus timeline event, and critical configuration plus audit/outbox.
- Optimistic concurrency compares the stored `version`; conflicts return HTTP 409 with a stable error code.
- Cross-table telemetry projections are eventually consistent and recoverable from normalized events/reconciliation.

## 8.10 Data validation and units

- Canonical units: Celsius, percent relative humidity, kPa, mm/s RMS vibration, volts, amperes, RPM, kW, and health percent.
- Device-type profiles define plausible and absolute bounds; values outside absolute bounds are rejected, while plausible-bound exceptions are stored with a quality flag.
- Missing metrics, timestamp skew, out-of-order sequence, replay, and schema mismatch are explicit quality states.
- Decimal-compatible values are stored without floating-point ambiguity in DynamoDB adapters.

## 8.11 Retention and archival

| Record | Hot retention | Archive/expiry behavior |
|---|---:|---|
| Raw telemetry | 30 days | TTL; optional Parquet export to S3 before expiry |
| Hourly/daily aggregates | 13 months | TTL/lifecycle after reporting needs |
| Core resources/config | Resource lifetime + policy | Archive status; no destructive user delete |
| Sessions/idempotency | Expiry + investigation window | TTL, with relevant security event retained |
| Audit/security/auth events | Searchable period by class | Immutable S3 archive baseline 7 years |
| Reports | 30 days | S3 lifecycle expiration and expired job state |

## 8.12 Backup, recovery, and migration

- Enable PITR and scheduled backups for core, aggregate, and event tables.
- Restore tests create new tables; production tables are not overwritten in place.
- Schemas evolve through `schemaVersion` and read-time adapters. Backfills are idempotent, rate-limited, observable jobs.
- GSI additions deploy before code depends on them; removals occur only after an observation window.
- Infrastructure documents RPO/RTO and includes restore, rebind, validation, and cutover steps.

## 8.13 Data security checklist

- Every query derives factory scope from trusted identity, never solely from a user-provided filter.
- DynamoDB IAM conditions and separate roles limit tables/actions by deployable.
- Password hashes, refresh-token plaintext, certificate private keys, JWTs, and secrets never enter general records or logs.
- Exports are encrypted, scoped, checksummed, access-logged, short-lived, and audited.
- Audit before/after summaries use allowlisted safe fields and redact sensitive configuration.
