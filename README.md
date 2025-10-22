# CyVerse STAC Catalog

This repository contains STAC (SpatioTemporal Asset Catalog) collections that are automatically ingested into the CyVerse STAC API at [https://stac.cyverse.org](https://stac.cyverse.org).

**Key Features:**
- ✅ Automatic synchronization every 5 minutes via cronjob
- ✅ Full CRUD support (Create, Update, Delete)
- ✅ Validates collections and items before ingestion
- ✅ Comprehensive logging of all operations
- ✅ Safe and idempotent (can run multiple times)

### 📚 Additional Resources

- **Radiant Earth STAC Browser:** https://radiantearth.github.io/stac-browser/#/external/stac.cyverse.org
- **STAC Specification:** https://stacspec.org
- **STAC Extensions:** https://stac-extensions.github.io
- **STAC Browser:** https://radiantearth.github.io/stac-browser
- **PySTAC:** https://pystac.readthedocs.io (Python library)
- **STAC Best Practices:** https://github.com/radiantearth/stac-spec/blob/master/best-practices.md

<br/>
<br/>

## Administration
The STAC-API is being served on a VM machine called stac.cyverse.org. It may also be called `aeoulus-stack-api.cyverse.org` (128.196.254.84). 

`ssh ubuntu@stac.cyverse.org` requires public ssh from local computer to access

```
Host stac.cyverse.org
    HostName stac.cyverse.org
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

<br/>
<br/>

On the VM, work in the directory `/home/ubuntu/new-stac-api` 

```
new-stac-api/
├── cyverse-stac/           # This repo holds the STAC catalog file                     
└── stac-fastapi-pgstac/    # contains ingestion py script, dockerfiles, and dockercompose yml to build containerized Stac-fastapi with PG DB
```

---

<br/>
<br/>

## Add STAC Records

Each collection MUST be in its own subdirectory under `catalogs/` and MUST contain:

1. **`collection.json`** - STAC Collection metadata
2. **`index.geojson`** - GeoJSON FeatureCollection containing STAC Items

**Example:**
```bash
catalogs/my-new-dataset/
├── collection.json
└── index.geojson
```

<br/>
<br/>

---

<br/>

### **General Workflow**

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                       │
│                   github.com/cyverse-gis/cyverse-stac           │
│                                                                 │
│  catalogs/                                                      │
│  ├── collection-1/                                              │
│  │   ├── collection.json                                        │
│  │   └── index.geojson                                          │
│  ├── collection-2/                                              │
│  │   ├── collection.json                                        │
│  │   └── index.geojson                                          │
│  └── ...                                                        │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Git Push
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VM Server (stac.cyverse.org)               │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Cronjob (runs every 5 minutes)                        │     │
│  │  */5 * * * * /path/to/update_and_restart.sh            │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  cyverse-stac/update_and_restart.sh                    │     │
│  │  1. git fetch                                          │     │
│  │  2. Check for changes                                  │     │
│  │  3. git pull (if changes detected)                     │     │
│  │  4. Run sync_and_ingest.py                             │     │
|  |  5. Logs to cron_log_file.log
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  stac-fastapi-pgstac/scripts/sync_and_ingest.py        │     │
│  │  - Scans cyverse-stac/catalogs/ directory              │     │
│  │  - Compares with API state                             │     │
│  │  - Creates/Updates/Deletes collections & items         │     │
|  |  - Logs to ingestion.log
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   │ HTTPS API Calls                             │
│                   ▼                                             │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STAC API (Docker)                            │
│                  https://stac.cyverse.org                       │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  FastAPI Application                                   │     │
│  │  - Validates requests                                  │     │
│  │  - Processes collections & items                       │     │
│  │  - Stores in PostgreSQL database                       │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  PostgreSQL + PgSTAC Database                          │     │
│  │  - Stores STAC collections                             │     │
│  │  - Stores STAC items                                   │     │
│  │  - Provides spatial queries                            │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

<br/>
<br/>

---

## 📊 Monitoring and Logs

### **Log Files**

| Log File | Purpose | Location |
|----------|---------|----------|
| `ingestion.log` | Detailed ingestion operations | `/home/ubuntu/new-stac-api/cyverse-stac/ingestion.log` |
| `cron_log_file.log` | Cronjob execution log | `/home/ubuntu/new-stac-api/cyverse-stac/cron_log_file.log` |

### **Checking Logs**

```bash
# View most recent ingestion
tail -100 /home/ubuntu/new-stac-api/cyverse-stac/ingestion.log

# Follow log in real-time
tail -f /home/ubuntu/new-stac-api/cyverse-stac/ingestion.log

# Check cronjob execution
tail -50 /home/ubuntu/new-stac-api/cyverse-stac/cron_log_file.log

# Search for errors
grep ERROR /home/ubuntu/new-stac-api/cyverse-stac/ingestion.log
```

### **Log Format**

```
2025-10-21 21:42:05,637 - INFO - Starting STAC collection sync
2025-10-21 21:42:05,900 - INFO - ✓ Successfully created collection 'my-collection'
2025-10-21 21:42:06,393 - INFO -   ✓ Successfully created item 'item-001'
2025-10-21 21:42:06,586 - ERROR -   ✗ Failed to create item 'item-002': HTTP 400: Invalid ID
```

### **Summary Output**

At the end of each run, you'll see:

```
======================================================================
SYNC SUMMARY
======================================================================
Collections created:  2
Collections updated:  1
Collections deleted:  0
Items created:        219
Items updated:        10
Items deleted:        0
Errors:               3
======================================================================
```

---



### **Manual Ingestion**

To manually trigger ingestion outside the cronjob:

```bash
# Run the bash script
/home/ubuntu/new-stac-api/cyverse-stac/update_and_restart.sh

# Or run Python script directly
python3 /home/ubuntu/new-stac-api/stac-fastapi-pgstac/scripts/sync_and_ingest.py \
  /home/ubuntu/new-stac-api/stac-fastapi-pgstac/config/ingestion_config.yaml
```

### **Verifying Data in API**

```bash
# List all collections
curl https://stac.cyverse.org/collections | jq '.collections[].id'

# Get specific collection
curl https://stac.cyverse.org/collections/my-collection | jq '.'

# List items in collection
curl https://stac.cyverse.org/collections/my-collection/items | jq '.features[].id'

# Get specific item
curl https://stac.cyverse.org/collections/my-collection/items/item-001 | jq '.'
```

### **Checking Cronjob Status**

```bash
# View crontab
crontab -l

# Check if cron service is running
systemctl status cron

# View recent cron execution logs
grep CRON /var/log/syslog | tail -20
```

---

## 🌐 API Access

### **Endpoints**

| Endpoint | Description |
|----------|-------------|
| `GET /` | API landing page |
| `GET /collections` | List all collections |
| `GET /collections/{id}` | Get specific collection |
| `GET /collections/{id}/items` | List items in collection |
| `GET /collections/{id}/items/{item_id}` | Get specific item |
| `GET /search` | Search across all collections |

### **Example Queries**

```bash
# List all collections
curl https://stac.cyverse.org/collections

# Get collection details
curl https://stac.cyverse.org/collections/joplin

# Search for items
curl -X POST https://stac.cyverse.org/search \
  -H "Content-Type: application/json" \
  -d '{
    "collections": ["joplin"],
    "bbox": [-95, 36, -94, 38],
    "limit": 10
  }'
```

## Docker Images and Docker Compose

The STAC API (stac-utils/stac-fastapi-pgstac:latest) and the Postgres DB (ghcr.io/stac-utils/pgstac:v0.0.2) are docker images. They are orchestrated together using docker compose. The orchestration file is `/stac-fastapi-pgstac/docker-compose.yml`. It has a persistent volume that means the stac json and geojson files will be preserved even if the docker compose is restarted of shutdown. 

Check status of docker compose `docker compose ps`

Start docker compose `docker compose up -d`


#### Change STAC API title and description

STAC API title and description are an environmental variable within the `docker-compose.yml`. The compose network may need to be brought down and then back up to take the changes. 

- STAC_FASTAPI_TITLE=CyVerse STAC API
- STAC_FASTAPI_DESCRIPTION=CyVerse SpatioTemporal Asset Catalog API for geospatial data discovery
- STAC_FASTAPI_VERSION=1.0.0


## Nginx 




---






