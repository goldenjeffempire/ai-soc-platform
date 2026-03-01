from prometheus_client import Counter, Histogram

INGEST_REQUESTS = Counter(
    "ingest_requests_total",
    "Total ingest requests",
    ["status", "tenant_id", "source_id"],
)

INGEST_LATENCY = Histogram(
    "ingest_request_latency_seconds",
    "Latency of ingest endpoint",
)

KAFKA_PUBLISH = Counter(
    "kafka_publish_total",
    "Total kafka publish attempts",
    ["status"],
)
