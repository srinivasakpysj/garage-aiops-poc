# Architecture and implementation boundaries

## First increment
React dashboard shell -> FastAPI -> PostgreSQL. The API validates request payloads, and the frontend displays records from the API. This is a local foundation, not yet an operational monitoring product.

## Target event flow
1. Zabbix 7.2 action/webhook sends a problem or recovery event.
2. API validates shared secret/signature and normalizes event fields.
3. Deduplication uses `(source, external_event_id)`.
4. Durable queue receives accepted events; worker enriches with read-only Zabbix API evidence.
5. AI service returns schema-validated facts, hypotheses, and proposed runbook actions.
6. Routing policy selects team; notification adapters deliver Teams/email with retry state.
7. Engineer acknowledges and updates progress; recovery enters pending verification until an authorized engineer confirms resolution.
8. Audit event records material changes.

## Incident lifecycle
`open -> acknowledged -> in_progress -> pending_verification -> resolved`
A reopened state is supported for recurring symptoms. A Zabbix recovery event should not automatically imply human-verified resolution.

## Main entities
- servers: host inventory and ownership metadata
- incidents: normalized event and operational lifecycle
- ai_analyses: evidence-linked analysis output
- notifications: delivery status and retry attempts
- audit_events: traceability for actions and status changes

## Production hardening required
Alembic migrations, authentication/RBAC, CSRF protection if cookie sessions are used, rate limiting, webhook verification, TLS, secret management, queue/worker, structured logs, metrics, backup/restore test, dependency scanning, and deployment rollback.
