# Zabbix 7.2 integration plan (not enabled in increment 1)

## Before connecting
Confirm whether the Zabbix server is on-premises or in AWS, how the POC application can securely reach it, and which non-critical hosts are approved for pilot monitoring. Never expose the Zabbix API or database publicly.

## Event ingestion
- Configure a dedicated Zabbix webhook media type/action for problem and recovery events.
- Send only required fields: event ID, event value/recovery state, host ID/name, trigger ID/name, severity, event timestamp, and a link to the Zabbix event if appropriate.
- Authenticate requests with a rotated secret or a stronger approved verification mechanism. Do not place secrets in source control or event payloads.
- Validate payloads, cap request size, log event IDs without leaking secrets, and make processing idempotent.
- Return quickly after durable acceptance; use a queue/worker for enrichment and notifications.

## Evidence enrichment
Use a dedicated, least-privilege Zabbix API account to retrieve relevant host/item/event data. Restrict scope to the approved pilot hosts. Store evidence snapshots needed for incident history, not a full copy of time-series data.

## Recovery and verification
On recovery, set the incident to `pending_verification`; ask the assigned engineer to confirm recovery. If metrics regress or the problem event returns, reopen or create a linked incident according to the deduplication policy.

## Test cases
- New problem event
- Duplicate delivery of the same event ID
- Recovery event
- Unknown host
- Invalid/missing authentication
- Zabbix API timeout
- Queue or notification-provider outage
- Event with unexpected fields or oversized payload
