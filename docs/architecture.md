# AI-Powered SOC Platform (Nigeria-ready) — Architecture

## Objective
Production-grade MVP SOC platform that:
- Ingests endpoint/network logs (HTTP; optional syslog UDP)
- Normalizes logs into a canonical schema
- Stores logs in OpenSearch for search + dashboards
- Scores anomalies via ML + heuristics
- Creates risk-scored Alerts and promotes to Incidents
- Runs basic SOAR playbooks (Block IP, Disable User, Notify)
- Secure-by-default and NDPA-aligned

## Components
- **Ingestion Service (FastAPI):** validates + enriches logs, rate limits, replay protection, Kafka producer → `logs.raw`
- **Normalization Worker:** Kafka consumer `logs.raw` → canonical schema → Kafka producer `logs.normalized` + OpenSearch indexing
- **Scoring Service (FastAPI):** consumes `logs.normalized`, feature extraction + threat intel correlation + ML inference, writes Alerts into Django via internal auth
- **Core API (Django + DRF):** tenants, users, RBAC, alerts/incidents/evidence, playbooks, audit logging
- **Frontend (React + Vite):** SOC dashboard UI (alerts/incidents/playbooks/admin)
- **Mock services:** mock firewall + mock IAM to simulate SOAR actions
- **Infra:** Docker Compose (local), optional K8s manifests (staging)

## Data Flow (End-to-End)
1. Agent sends logs → `POST /ingest`
2. Ingestion validates/enriches → Kafka `logs.raw`
3. Normalization transforms → Kafka `logs.normalized` and indexes into OpenSearch
4. Scoring consumes `logs.normalized` → risk_score 0–100 → creates Alert in Django
5. React dashboard queries Django + OpenSearch to display incidents/alerts/log evidence
6. Playbook runs from UI → executes actions via allowlisted outbound calls → stores PlaybookRun + audit logs

## Canonical Log Schema (Normalized)
- event_id (uuid)
- tenant_id
- source_id
- event_type (auth/network/endpoint/dns/...)
- severity (0-10)
- timestamp (ISO8601 UTC)
- host, user
- ip_src, ip_dst, port
- action, message
- raw (original payload)
- tags (array)
- metadata (object)

## Kafka Topics
- `logs.raw` — validated but not normalized
- `logs.normalized` — canonical schema, ready for search/scoring
(Optional: `logs.dlq` for invalid records)

## Storage
- PostgreSQL: tenants/users/rbac, alerts/incidents/evidence, playbook runs, audit logs, threat intel feed
- OpenSearch: normalized logs indexed per-tenant + time-based indices
- Redis: rate limiting + replay protection nonce cache
- Kafka: log pipeline backbone

## Security Defaults
- TLS everywhere (demo can be internal network; prod uses TLS/mTLS)
- JWT auth + RBAC for UI access
- Internal service auth tokens separate from user auth keys
- Input validation + body size limits + timeouts
- SSRF-safe playbooks (destination allowlist)
- Audit logging for all privileged actions/playbook runs

## NDPA Alignment (MVP)
- Data minimization + configurable retention for OpenSearch indices
- Strong access controls (tenant isolation + RBAC)
- Audit trails for admin + response actions
