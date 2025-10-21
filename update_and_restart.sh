#!/bin/bash

# Variables
REPO_URL="https://github.com/cyverse-gis/cyverse-stac.git"
LOCAL_REPO_DIR="/home/ubuntu/new-stac-api/cyverse-stac"
INGESTION_SCRIPT="/home/ubuntu/new-stac-api/stac-fastapi-pgstac/scripts/sync_and_ingest.py"
CONFIG_FILE="/home/ubuntu/new-stac-api/stac-fastapi-pgstac/config/ingestion_config.yaml"
LOG_FILE="/home/ubuntu/new-stac-api/cyverse-stac/cron_log_file.log"

# Function to log with a timestamp
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "${LOG_FILE}"
}

cd "${LOCAL_REPO_DIR}" || { log "ERROR: Could not change to directory ${LOCAL_REPO_DIR}"; exit 1; }

log "INFO: Checking for updates in the repository."

git fetch &>> "${LOG_FILE}"

# Check if there are any changes
if [ -n "$(git diff origin/main)" ]; then
  log "INFO: Changes detected. Pulling updates."

  git pull &>> "${LOG_FILE}"

  if [ $? -eq 0 ]; then
    log "INFO: Successfully pulled updates. Running ingestion script."

    # Run the STAC ingestion script
    python3 "${INGESTION_SCRIPT}" "${CONFIG_FILE}" &>> "${LOG_FILE}"

    if [ $? -eq 0 ]; then
      log "INFO: Ingestion completed successfully."
    else
      log "ERROR: Ingestion script failed. Check ingestion.log for details."
    fi
  else
    log "ERROR: Failed to pull updates."
  fi
else
  log "INFO: No changes detected."
fi
