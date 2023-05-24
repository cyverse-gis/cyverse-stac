#!/bin/bash

# Variables
REPO_URL="https://github.com/cyverse-gis/cyverse-stac.git"
LOCAL_REPO_DIR="/home/ubuntu/cyverse-stac"
DOCKER_COMPOSE_FILE="/home/ubuntu/stac-fastapi/docker-compose.yml"

cd "${LOCAL_REPO_DIR}"
git fetch

# Check if there are any changes
if [ -n "$(git diff origin/main)" ]; then
  # Pull the changes and restart the service
  git pull
  docker-compose -f "${DOCKER_COMPOSE_FILE}" restart
fi

# Add the script to cron