from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None)

    service_name: str = "ingestion-fastapi"
    log_level: str = "INFO"

    # Auth
    ingest_jwt_secret: str = "dev_only_change_me"
    ingest_jwt_issuer: str = "ai-soc-platform"
    ingest_jwt_audience: str = "log-agent"

    # Kafka / Redis
    kafka_bootstrap: str = "kafka:9092"
    kafka_topic_raw: str = "logs.raw"
    redis_url: str = "redis://redis:6379/0"

    # Security controls
    replay_window_sec: int = 300  # +/- 5 minutes allowed
    rate_limit_per_minute: int = 600  # per tenant_id+source_id

    # Request limits
    max_body_bytes: int = 256_000  # 256 KB

    # Optional enrichment
    geoip_enabled: bool = False


settings = Settings()
