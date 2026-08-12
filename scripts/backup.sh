#!/bin/bash

set -euo pipefail

CONTAINER="emailshieldai"
BACKUP_ROOT="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_ROOT}/emailshield_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/reports"

echo "[+] Creating backup: $BACKUP_DIR"

# Create a consistent SQLite backup using Python's sqlite3 backup API
docker exec "$CONTAINER" python -c '
import sqlite3

source = sqlite3.connect("/app/data/emailshield.db")
backup = sqlite3.connect("/app/data/emailshield_backup.db")

with backup:
    source.backup(backup)

backup.close()
source.close()

print("[+] SQLite backup created")
'

echo "[+] Copying database backup..."

docker cp \
    "$CONTAINER:/app/data/emailshield_backup.db" \
    "$BACKUP_DIR/emailshield.db"

# Remove temporary backup from Docker volume
docker exec "$CONTAINER" \
    rm -f /app/data/emailshield_backup.db

echo "[+] Copying PDF reports..."

docker cp \
    "$CONTAINER:/app/reports/." \
    "$BACKUP_DIR/reports/"

echo "[+] Creating SHA256 checksums..."

(
    cd "$BACKUP_DIR"

    sha256sum emailshield.db > SHA256SUMS

    find reports -type f -name "*.pdf" -print0 |
        xargs -0 -r sha256sum >> SHA256SUMS
)

echo
echo "========================================"
echo " Backup completed successfully"
echo "========================================"
echo
echo "Backup directory:"
echo "  $BACKUP_DIR"
echo

du -sh "$BACKUP_DIR"

echo
echo "Backup contents:"
find "$BACKUP_DIR" -type f -printf "  %p\n"
