import time
import jwt
import os

secret = os.getenv("INGEST_JWT_SECRET", "dev_only_change_me")
tenant_id = os.getenv("TENANT_ID", "tenant_demo")
source_id = os.getenv("SOURCE_ID", "source_demo")

now = int(time.time())
payload = {
  "iss": "ai-soc-platform",
  "aud": "log-agent",
  "iat": now,
  "exp": now + 3600,
  "tenant_id": tenant_id,
  "source_id": source_id,
  "scope": "agent",
}
print(jwt.encode(payload, secret, algorithm="HS256"))
