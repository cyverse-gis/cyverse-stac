#!/bin/bash

# Variables
REPO_URL="https://github.com/cyverse-gis/cyverse-stac.git"
LOCAL_REPO_DIR="/home/ubuntu/cyverse-stac"
DOCKER_COMPOSE_FILE="/home/ubuntu/stac-fastapi/docker-compose.yml"
LOG_FILE="/home/ubuntu/cyverse-stac/cron_log_file.log"

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
    log "INFO: Successfully pulled updates. Restarting the service."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" restart &>> "${LOG_FILE}"
    
    if [ $? -eq 0 ]; then
      log "INFO: Service restarted successfully."
    else
      log "ERROR: Failed to restart the service."
    fi
  else
    log "ERROR: Failed to pull updates."
  fi
else
  log "INFO: No changes detected."
fi
