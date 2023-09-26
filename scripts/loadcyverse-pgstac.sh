#!/bin/bash

pip3 install requests

echo "Running /app/cyverse-scripts/ingest_cyverse.py"

python /app/cyverse-scripts/ingest_cyverse.py http://app-pgstac:8082
