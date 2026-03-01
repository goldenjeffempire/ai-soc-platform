#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP="${BOOTSTRAP:-kafka:9092}"

echo "Creating topics on ${BOOTSTRAP}..."
kafka-topics.sh --bootstrap-server "$BOOTSTRAP" --create --if-not-exists --topic logs.raw --partitions 3 --replication-factor 1
kafka-topics.sh --bootstrap-server "$BOOTSTRAP" --create --if-not-exists --topic logs.normalized --partitions 3 --replication-factor 1
echo "Done."
kafka-topics.sh --bootstrap-server "$BOOTSTRAP" --list
