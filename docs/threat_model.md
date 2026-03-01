# Threat Model — AI-Powered SOC Platform (MVP)

## Assets
- Tenant logs, alerts/incidents, evidence
- Secrets (JWT signing keys, internal service tokens)
- Threat intel feeds (integrity)
- Playbook execution channel
- Audit logs (must be tamper-resistant)

## Trust Boundaries
1) Agent/Internet → Ingestion API
2) Ingestion → Kafka
3) Workers/Services → Postgres/OpenSearch/Redis
4) Frontend → Django API
5) Playbooks → external action services

## Threats & Mitigations (STRIDE)

### Spoofing
- Fake agent impersonates tenant/source  
Mitigate: scoped tokens, per-tenant rate limiting, replay protection (nonce+timestamp), strict schema validation.

### Tampering
- Message modification in transit or pipeline  
Mitigate: TLS, Kafka network isolation/ACLs in prod, optional message signatures, evidence hashing.

### Repudiation
- Deny running playbooks/changing incidents  
Mitigate: mandatory AuditLog with actor, action, request_id, timestamp; PlaybookRun step recording.

### Information Disclosure
- Cross-tenant data exposure via API or OpenSearch  
Mitigate: enforced tenant filter everywhere, tenant-aware index naming, RBAC, log redaction, least privilege.

### Denial of Service
- Flood ingestion/scoring/OpenSearch  
Mitigate: rate limiting, timeouts, size limits, backpressure, consumer batching, sensible partition strategy.

### Elevation of Privilege
- Analyst becomes admin or runs privileged playbooks  
Mitigate: RBAC server-side enforcement, internal auth separation, SSRF protections + allowlists.

## Playbook Risks
- SSRF, unsafe blocks, credential leakage  
Mitigate: destination allowlists, redact sensitive headers, require role checks, record all executions.

## NDPA Controls (MVP)
- Retention policies for logs
- Access controls + audit trails
- Tenant offboarding deletion workflow
