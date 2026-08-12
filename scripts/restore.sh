#!/bin/bash

set -euo pipefail

CONTAINER="emailshieldai"
BACKUP_ROOT="./backups"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup-directory>"
    echo
    echo "Example:"
    echo "  $0 backups/emailshield_20260811_174639"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "[!] Backup directory not found: $BACKUP_DIR"
    exit 1
fi

if [ ! -f "$BACKUP_DIR/emailshield.db" ]; then
    echo "[!] Database backup not found"
    exit 1
fi

if [ ! -f "$BACKUP_DIR/SHA256SUMS" ]; then
    echo "[!] SHA256SUMS not found"
    exit 1
fi

echo "[+] Verifying backup integrity..."

(
    cd "$BACKUP_DIR"
    sha256sum -c SHA256SUMS
)

echo
echo "[+] Backup integrity verified."

echo "[+] Stopping EmailShieldAI..."

docker compose down

echo "[+] Starting temporary container..."

docker compose up -d

echo "[+] Restoring database..."

docker cp \
    "$BACKUP_DIR/emailshield.db" \
    "$CONTAINER:/app/data/emailshield.db"

echo "[+] Restoring PDF reports..."

docker exec "$CONTAINER" sh -c \
    'rm -f /app/reports/*.pdf'

docker cp \
    "$BACKUP_DIR/reports/." \
    "$CONTAINER:/app/reports/"

echo "[+] Fixing ownership..."

docker exec "$CONTAINER" sh -c \
    'chown -R appuser:appuser /app/data /app/reports'

echo "[+] Restarting application..."

docker compose restart

echo "[+] Waiting for application health..."

MAX_WAIT=60
WAITED=0

while true; do
    STATUS=$(docker inspect \
        --format='{{.State.Health.Status}}' \
        "$CONTAINER" 2>/dev/null || echo "unknown")

    echo "    Health status: $STATUS"

    if [ "$STATUS" = "healthy" ]; then
        break
    fi

    if [ "$STATUS" = "unhealthy" ]; then
        echo "[!] Application became unhealthy."
        docker compose logs --tail 50
        exit 1
    fi

    if [ "$WAITED" -ge "$MAX_WAIT" ]; then
        echo "[!] Health check timed out after ${MAX_WAIT}s."
        docker compose logs --tail 50
        exit 1
    fi

    sleep 2
    WAITED=$((WAITED + 2))
done

echo
echo "[+] Application is healthy."

echo
echo "========================================"
echo " Restore completed successfully"
echo "========================================"

echo
echo "[+] Database:"
docker exec "$CONTAINER" ls -lh /app/data/emailshield.db

echo
echo "[+] PDF reports:"
docker exec "$CONTAINER" ls -lh /app/reports/

echo
echo "[+] Health endpoint:"

curl -fsS http://127.0.0.1:8000/health

echo
echo
echo "[+] Restore verification complete."
