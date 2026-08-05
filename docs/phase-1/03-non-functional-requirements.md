# 3. Non-Functional Requirements

These requirements are measurable quality gates, not aspirations. Targets apply to the production-like environment unless an environment-specific exception is documented.

## 3.1 Availability, resilience, and continuity

| ID | Requirement / target | Verification |
|---|---|---|
| NFR-AVL-01 | Monthly API availability target: 99.9%, excluding approved maintenance. | CloudWatch SLI and monthly calculation |
| NFR-AVL-02 | Telemetry ingestion shall tolerate transient downstream failure through managed retries and dead-letter handling without silent loss. | Fault-injection integration test |
| NFR-AVL-03 | No single application instance shall be required for availability; compute is stateless and replaceable. | Architecture review and deployment test |
| NFR-AVL-04 | DynamoDB point-in-time recovery shall be enabled for critical operational tables. | Infrastructure policy test |
| NFR-AVL-05 | Target RPO is 5 minutes for configuration/audit data and 15 minutes for derived analytical data; target RTO is 4 hours. | Recovery exercise |
| NFR-AVL-06 | Failed asynchronous events shall be recoverable from a DLQ/redrive path with a documented runbook. | Runbook rehearsal |

## 3.2 Performance and scale

| ID | Requirement / target | Verification |
|---|---|---|
| NFR-PERF-01 | Cached/read API latency: p95 <= 500 ms and p99 <= 1 s under expected load. | Load test and CloudWatch percentile |
| NFR-PERF-02 | Mutation API latency, excluding asynchronous jobs: p95 <= 800 ms. | Load test |
| NFR-PERF-03 | Dashboard usable content shall render within 3 seconds on a representative broadband connection at p75. | Browser performance test |
| NFR-PERF-04 | Live values shall be visible within 5 seconds of accepted cloud ingestion under normal load. | End-to-end timing test |
| NFR-PERF-05 | Initial demo capacity shall sustain 20 devices at one event/5 seconds with 5x burst headroom. | Sustained and burst test |
| NFR-PERF-06 | Architecture and partition keys shall support an evolution target of 10,000 devices without redesigning identity or API contracts. | Partition/load model review |
| NFR-PERF-07 | All query APIs shall enforce page-size limits of 1-100 records and reject unbounded scans. | API contract tests |

## 3.3 Security and privacy

| ID | Requirement / target | Verification |
|---|---|---|
| NFR-SEC-01 | External traffic shall use TLS 1.2 or later; device MQTT shall use mutual TLS with unique X.509 certificates. | Configuration scan and connection tests |
| NFR-SEC-02 | Data shall be encrypted at rest using AWS-managed or customer-managed KMS keys according to data classification. | Infrastructure policy tests |
| NFR-SEC-03 | Authorization shall default deny and enforce permission plus resource/factory scope on every protected operation. | Negative authorization matrix |
| NFR-SEC-04 | Access tokens shall be short lived (target 15 minutes); refresh tokens shall rotate and be revocable. | Authentication tests |
| NFR-SEC-05 | Passwords shall use an adaptive one-way hash (Argon2id preferred) and never appear in logs or tokens. | Code review and secret scan |
| NFR-SEC-06 | Secrets shall use Secrets Manager/parameter services and shall not be committed, baked into images, or exposed to browsers. | CI secret scanning and deployment review |
| NFR-SEC-07 | Input shall be schema validated with explicit bounds; output and logs shall be safely encoded and redacted. | Fuzz/negative tests and log review |
| NFR-SEC-08 | Critical dependency and container vulnerabilities shall block release; high findings require disposition and time-bound remediation. | CI security gates |
| NFR-SEC-09 | Security-sensitive clocks shall use UTC and tolerate no more than five minutes of device skew before flagging quality. | Telemetry validation tests |
| NFR-SEC-10 | Personally identifiable user data shall be minimized to operational identity/contact fields and excluded from telemetry. | Data inventory review |

## 3.4 Reliability and data integrity

| ID | Requirement / target | Verification |
|---|---|---|
| NFR-REL-01 | Telemetry processing shall be idempotent for the same device ID and event ID. | Duplicate-delivery test |
| NFR-REL-02 | All stored events shall preserve device event time and server ingestion time. | Schema tests |
| NFR-REL-03 | State transitions shall use conditional writes or transactions to prevent lost updates. | Concurrency tests |
| NFR-REL-04 | Units, valid ranges, schema version, and quality flags shall accompany telemetry processing. | Contract tests |
| NFR-REL-05 | No alert or audit mutation may erase prior lifecycle history. | Persistence tests |
| NFR-REL-06 | Time-series aggregates shall be reproducible from retained source data within the raw retention window. | Reconciliation job/test |

## 3.5 Observability and operability

| ID | Requirement / target | Verification |
|---|---|---|
| NFR-OBS-01 | Logs shall be structured JSON and include timestamp, level, service, environment, correlation ID, and safe context. | Log schema checks |
| NFR-OBS-02 | Application, device, audit, security, and authentication logs shall be logically separated with explicit retention. | CloudWatch review |
| NFR-OBS-03 | Distributed request context shall propagate from API Gateway through compute and asynchronous messages. | Trace/correlation test |
| NFR-OBS-04 | Alerts shall exist for error rate, latency, throttles, queue age, DLQ depth, unauthorized IoT traffic, and notification failure. | Alarm policy tests |
| NFR-OBS-05 | Every production alarm shall link to an owner and runbook. | Operational readiness review |
| NFR-OBS-06 | Health endpoints shall not reveal secrets, internal topology, stack traces, or tenant data. | Security test |

## 3.6 Maintainability and delivery quality

| ID | Requirement / target | Verification |
|---|---|---|
| NFR-MNT-01 | Frontend, backend, simulator, infrastructure, and documentation shall have explicit ownership boundaries and one-way dependency rules. | Architecture/static dependency check |
| NFR-MNT-02 | Public functions, APIs, schemas, configuration keys, and infrastructure inputs shall be typed and documented. | Type and documentation checks |
| NFR-MNT-03 | Main branch changes shall pass formatting, linting, type checking, tests, dependency scanning, and secret scanning. | Protected CI workflow |
| NFR-MNT-04 | Domain logic shall be testable without AWS network access by using ports and adapters. | Unit test design review |
| NFR-MNT-05 | Database and API changes shall be backward compatible or versioned with an explicit migration/deprecation plan. | Change review checklist |
| NFR-MNT-06 | Configuration shall be environment-driven and validated at startup; no source changes shall be needed between environments. | Deployment tests |

## 3.7 Usability and accessibility

| ID | Requirement / target | Verification |
|---|---|---|
| NFR-UX-01 | The web experience shall be responsive from 360 px mobile width through large operations displays. | Visual regression matrix |
| NFR-UX-02 | Core workflows shall meet WCAG 2.2 AA for contrast, keyboard access, focus order, names, and error association. | Automated and manual accessibility tests |
| NFR-UX-03 | Status shall never be communicated by color alone; labels/icons and accessible text are required. | Design QA |
| NFR-UX-04 | Loading, empty, stale, partial-error, and permission-denied states shall be intentionally designed for every data view. | Component/story review |
| NFR-UX-05 | Destructive or high-impact actions shall require clear confirmation and show the exact target. | End-to-end tests |
| NFR-UX-06 | Charts shall provide units, legends, tooltips, time range, last update, and accessible summaries/tables. | Accessibility and product review |

## 3.8 Compatibility and portability

- Support the latest two stable versions of Chrome, Edge, and Firefox.
- Use UTC and ISO 8601 at service boundaries; localize only at presentation.
- Use versioned JSON contracts and standard MQTT topics/payloads documented in the API contract.
- Infrastructure must be reproducible in a second AWS account with environment-specific configuration only.
- The simulator must run on current supported Python versions on Windows, macOS, and Linux.

## 3.9 Retention baseline

| Data class | Baseline | Rationale |
|---|---:|---|
| Raw telemetry | 30 days in DynamoDB, lifecycle export as needed | Fast operational query with controlled demo cost |
| Hourly/daily aggregates | 13 months | Seasonal and comparative analytics |
| Audit/security/auth events | 7 years in immutable archive, shorter searchable hot copy | Compliance-quality evidence and cost balance |
| Application/device diagnostic logs | 90 days hot, optional archive | Incident investigation |
| Reports | 30 days unless policy requires less | Minimize stale exported data |
| Refresh-token/session records | Active lifetime plus 30 days security history | Revocation and investigation |

Retention values are configuration baselines and must be reviewed against the final organization's legal and operational requirements before a real deployment.
