# 1. Business Requirements Analysis

## 1.1 Executive summary

The manufacturing organization lacks a trusted, centralized view of factory equipment. Device identity, telemetry, machine condition, energy use, alerts, operator actions, and security events are fragmented or unavailable. The platform will establish a secure digital operations layer across factories, enabling authorized teams to understand current conditions, detect risk early, investigate events, and act with accountability.

The initial capstone deployment simulates at least 20 machines, but the design must remain credible for multiple factories and thousands of devices. The product is an operational monitoring and decision-support platform; it does not directly control safety-critical machinery.

## 1.2 Business problem

Current operations cannot reliably answer:

- Which factories and devices are healthy, degraded, offline, or critical?
- Whether a telemetry message came from an authenticated, authorized device?
- Which machines are trending toward failure or excessive energy use?
- Which alerts require action, who owns them, and whether they were resolved?
- Who changed a device, threshold, user, or security configuration?
- Whether the application and ingestion pipeline are healthy enough to trust?

This creates avoidable downtime, delayed maintenance, energy waste, weak security assurance, and poor incident traceability.

## 1.3 Stakeholders and needs

| Stakeholder | Primary need | Evidence of value |
|---|---|---|
| Plant leadership | Cross-factory health, risk, and energy visibility | Executive dashboard and scheduled reports |
| Factory administrators | Safe local administration | Factory-scoped users, devices, policies, and audit records |
| Factory managers | Operational overview and prioritization | Health scores, alert backlog, utilization, trends |
| Maintenance engineers | Early warning and diagnostic context | Anomaly signals, correlated telemetry, maintenance notes |
| Operators | Clear live status and actionable alerts | Low-latency monitoring, acknowledgement workflow |
| Security and compliance | Identity, least privilege, and evidence | Certificate inventory, security events, immutable audit trail |
| Platform/DevOps team | Reliable, observable service | SLOs, dashboards, alarms, deployment evidence |
| University reviewers and recruiters | Engineering rigor and explainability | Traceable requirements, architecture, tests, and documentation |

## 1.4 Business objectives and target outcomes

| ID | Objective | Phase-appropriate success measure |
|---|---|---|
| BO-01 | Create one trusted operational view | 100% of registered demo devices appear with current status and factory ownership |
| BO-02 | Reduce time to detect abnormal conditions | Threshold or disconnect alert created within 60 seconds of qualifying data |
| BO-03 | Support proactive maintenance | Degradation and anomaly context shown before simulated failure scenarios |
| BO-04 | Protect device and user access | All protected operations require authenticated identity and server-side authorization |
| BO-05 | Establish accountability | 100% of privileged mutations create attributable audit events |
| BO-06 | Improve energy visibility | Power and energy trends available by device and factory |
| BO-07 | Demonstrate production engineering | Repeatable deployment, automated checks, observability, threat controls, and operational guides |

## 1.5 Scope

### In scope

- Multi-factory hierarchy and factory-scoped access
- User identity, session management, and six-role RBAC
- Device registry, provisioning lifecycle, metadata, configuration, and certificates
- Python simulator for at least 20 realistic industrial machines
- Secure MQTT telemetry ingestion through AWS IoT Core
- Live status, telemetry exploration, dashboards, and analytics
- Rule-based anomaly and threshold detection with extensible health scoring
- Alert lifecycle, notification preferences, and SNS-based delivery
- Report generation and controlled export
- Separate application, device, audit, security, and authentication logs
- Security center, application health, metrics, alarms, and audit evidence
- AWS infrastructure, CI/CD, testing, and deployment documentation

### Explicitly out of scope for the initial release

- Direct actuation or closed-loop control of physical machinery
- Safety instrumented system functions or emergency-stop decisions
- Physical sensor firmware and hardware manufacturing
- Full machine-learning model training and MLOps; the first release uses explainable rules and health scoring
- ERP/CMMS/SCADA write integrations, billing, procurement, or spare-parts management
- Native mobile applications; responsive web access is included
- Cross-customer SaaS billing and commercial tenancy management

## 1.6 Business capabilities

1. **Govern the estate:** model organizations, factories, users, devices, and ownership boundaries.
2. **Trust identities:** authenticate humans with JWT sessions and devices with X.509 certificates.
3. **Observe operations:** ingest, validate, store, and visualize live and historical telemetry.
4. **Detect risk:** evaluate thresholds, disconnections, authentication failures, certificate expiry, and health degradation.
5. **Coordinate response:** assign, acknowledge, comment on, and resolve alerts with notification delivery.
6. **Explain performance:** provide factory, device, energy, utilization, and alert analytics.
7. **Prove accountability:** preserve tamper-resistant audit and security evidence.
8. **Operate the platform:** expose service health, metrics, alarms, and diagnostic logs.

## 1.7 Business rules

| ID | Rule |
|---|---|
| BR-01 | Every device belongs to exactly one factory at a time. Transfers are privileged and audited. |
| BR-02 | Every non-super-administrator is restricted to explicitly assigned factories. |
| BR-03 | Device credentials are unique per device and are never shared or returned after initial secure provisioning. |
| BR-04 | A device is online only when its last accepted heartbeat is within the configured freshness window. |
| BR-05 | Alert severity derives from rule configuration and observed condition; users cannot silently downgrade history. |
| BR-06 | Alert acknowledgement and resolution require an authorized user, timestamp, and optional/required note by policy. |
| BR-07 | Privileged mutations and authorization failures create audit or security events independent of application logs. |
| BR-08 | Raw telemetry is append-only; corrections create derived records without rewriting the original event. |
| BR-09 | Report exports inherit the requester's factory scope and are time-limited when downloaded. |
| BR-10 | Disabled users and revoked certificates lose access immediately after revocation propagation. |

## 1.8 Assumptions and constraints

- AWS is the target cloud and a single primary region is used initially.
- The demo has no physical hardware; simulated devices must obey the same MQTT topics and certificate rules as real devices.
- DynamoDB is the primary operational database; access patterns must be designed before table keys.
- The student budget favors serverless, pay-per-use services and short retention for high-volume demo telemetry.
- JWT and custom RBAC are required. Production guidance may recommend federation/MFA as a future hardening option without replacing the stated stack.
- Internet connectivity is required for cloud ingestion; devices may buffer briefly and replay with original timestamps.
- All timestamps are stored in UTC and displayed in the user's selected time zone.

## 1.9 Success criteria

Phase 10 acceptance requires all of the following:

- At least 20 heterogeneous simulated devices publish realistic data continuously and independently.
- Dashboards reconcile with registered device and alert records under documented freshness rules.
- Factory isolation, role restrictions, and negative authorization tests pass.
- Alert scenarios for threshold breach, health degradation, disconnect, authentication failure, and certificate expiry are demonstrable.
- Audit records identify actor, action, target, result, timestamp, source context, and correlation ID.
- Infrastructure can be reproduced from version-controlled templates without console-only dependencies.
- Automated unit, integration, security, and end-to-end test evidence is available.
- Operational, security, setup, API, architecture, and deployment documentation is complete.

## 1.10 Principal risks and responses

| Risk | Business impact | Response |
|---|---|---|
| Telemetry volume exceeds cost assumptions | Budget overrun | TTL, aggregation, sampling, budgets, and per-environment limits |
| Over-broad factory access | Confidentiality breach | Server-side scope filters, deny-by-default policy, authorization tests |
| Shared or leaked device credentials | Device impersonation | Per-device certificates, revocation, rotation, IoT policies, secrets hygiene |
| Noisy alerts reduce trust | Missed incidents | Hysteresis, deduplication, cooldowns, severity policy, acknowledgement metrics |
| Dashboard data appears inconsistent | Low user confidence | Explicit freshness semantics, correlation IDs, reconciliation tests |
| Capstone scope expands uncontrollably | Incomplete product | Ten phase gates, definition of done, formal change log |
| Serverless cold starts or throttling | Delayed response | load tests, provisioned concurrency only where justified, quotas and alarms |

## 1.11 Decision standard

Every material implementation decision will be recorded as **Problem -> Solution -> Reason -> Advantages -> Tradeoffs**. This prevents unexplained technology choices and gives reviewers a clear basis for evaluating production readiness.
