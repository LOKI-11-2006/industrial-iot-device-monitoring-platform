# 7. User Roles

## 7.1 Authorization model

Authorization is **RBAC plus factory scope plus resource state**:

```text
allowed = authenticated
       AND session_active
       AND permission_in_role
       AND resource.factory_id IN user.factory_scope
       AND contextual_policy_allows_action
```

Super Administrator is the only platform-wide role. All other roles are assigned one or more factories. A role controls capability; factory assignments control where that capability applies. APIs re-evaluate access for every request and never trust role or factory IDs submitted by the browser.

## 7.2 Role definitions

| Role | Intended user | Scope | Key accountability |
|---|---|---|---|
| Super Administrator | Platform owner/security lead | All factories and platform settings | Governance, role assignment, platform security and retention |
| Factory Administrator | Local IT/OT administrator | Assigned factories | Users/scopes within authority, factory and device administration |
| Factory Manager | Operations leader | Assigned factories | Operational oversight, alert ownership, reports, threshold approval |
| Maintenance Engineer | Reliability/maintenance specialist | Assigned factories | Diagnostics, maintenance notes, alert investigation/resolution |
| Operator | Shift/floor operator | Assigned factories | Live monitoring and first-line alert acknowledgement |
| Viewer | Executive, auditor, or read-only observer | Assigned factories | Read-only dashboards, analytics, and approved reports |

## 7.3 Permission matrix

Legend: **A** = full administration, **M** = manage within factory scope, **O** = operational action, **R** = read, **-** = denied.

| Capability | Super Admin | Factory Admin | Factory Manager | Maintenance Engineer | Operator | Viewer |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| View authorized dashboards/analytics | A | R | R | R | R | R |
| Create/update/archive factories | A | M* | - | - | - | - |
| View device inventory/details | A | R | R | R | R | R |
| Register/update/archive devices | A | M | - | - | - | - |
| Provision/rotate/revoke certificates | A | M | - | - | - | - |
| Quarantine/unquarantine device | A | M | O* | O* | - | - |
| Change device desired configuration | A | M | O* | O* | - | - |
| Add maintenance notes | A | M | O | O | O* | - |
| View/acknowledge alerts | A | M | O | O | O | R |
| Assign/resolve alerts | A | M | O | O | - | - |
| Create/update alert rules | A | M | O* | - | - | - |
| Generate operational reports | A | M | O | O | O* | R* |
| Manage users in assigned factories | A | M | - | - | - | - |
| Assign Super Administrator | A | - | - | - | - | - |
| View activity logs | A | R | R | R | R* | R* |
| View security/auth logs | A | R | R* | - | - | - |
| View audit logs | A | R | R* | - | - | R* |
| Manage platform-wide settings/retention | A | - | - | - | - | - |
| Manage factory settings/notifications | A | M | O* | - | - | - |
| View platform health | A | R | R | R* | - | - |

`*` indicates a constrained permission:

- Factory Administrator may edit only their assigned factories and cannot archive the last active factory or expand their own scope.
- Factory Manager/Maintenance quarantine and configuration operations may require an approved policy and reason.
- Operator maintenance notes are observational and cannot close formal maintenance work.
- Operator reports are limited to predefined shift/alert reports; Viewer reports are read-only or predefined.
- Log access is redacted and filtered by factory and event classification.

## 7.4 Permission vocabulary

Representative backend permissions:

```text
factories:read, factories:create, factories:update, factories:archive
devices:read, devices:create, devices:update, devices:transfer, devices:quarantine
devices:configure, devices:provision, certificates:rotate, certificates:revoke
telemetry:read, analytics:read
alerts:read, alerts:acknowledge, alerts:assign, alerts:resolve
alert_rules:read, alert_rules:manage
reports:read, reports:create, reports:schedule
users:read, users:create, users:update, users:disable, users:assign_scope
audit:read, security:read, security:manage
settings:read, settings:manage_factory, settings:manage_platform
platform_health:read
```

The frontend may use these permissions to hide or disable controls, but backend policies remain authoritative.

## 7.5 Separation-of-duty and safety rules

- A user cannot grant a role or factory scope they do not possess.
- A Factory Administrator cannot create or promote a Super Administrator.
- A user cannot disable the last active Super Administrator.
- Self-role reduction, self-disablement, and removal of the user's last scope require explicit warning and policy checks.
- Certificate private material cannot be retrieved by a Viewer, Operator, Manager, or Maintenance Engineer.
- Audit events cannot be edited or deleted through application permissions, including by Super Administrator.
- Report generation applies authorization at execution time as well as request time so queued work cannot outlive access revocation.
- Factory transfer of a device requires access to source and destination, a reason, and a complete audit record.

## 7.6 Authorization test matrix

Every protected operation must include tests for:

1. unauthenticated request;
2. expired/revoked session;
3. role without permission;
4. correct role but wrong factory;
5. correct scope but disallowed resource state;
6. valid permission and scope;
7. attempted privilege escalation through request body or query filter;
8. list/query response containing no cross-factory records.
