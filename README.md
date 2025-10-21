# CyVerse STAC Catalog

This repository contains STAC (SpatioTemporal Asset Catalog) collections that are automatically ingested into the CyVerse STAC API at [https://stac.cyverse.org](https://stac.cyverse.org).

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

On the VM, work in the directory `/home/ubuntu/new-stac-api' 

new-stac-api/
├── cyverse-stac/           # This repo holds the STAC catalog file                     
└── stac-fastapi-pgstac/    # contains ingestion py script, dockerfiles, and dockercompose yml to build containerized Stac-fastapi with PG DB
---

## 🔍 Overview

This repository serves as the source of truth for STAC collections ingested into the CyVerse STAC API. When you add or update collections here and push to GitHub, they are automatically synchronized with the production STAC API within 5 minutes.

**Key Features:**
- ✅ Automatic synchronization every 5 minutes via cronjob
- ✅ Full CRUD support (Create, Update, Delete)
- ✅ Validates collections and items before ingestion
- ✅ Comprehensive logging of all operations
- ✅ Safe and idempotent (can run multiple times)

---

## 🏗️ System Architecture

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                        │
│                   github.com/cyverse-gis/cyverse-stac           │
│                                                                  │
│  catalogs/                                                      │
│  ├── collection-1/                                             │
│  │   ├── collection.json                                       │
│  │   └── index.geojson                                         │
│  ├── collection-2/                                             │
│  │   ├── collection.json                                       │
│  │   └── index.geojson                                         │
│  └── ...                                                        │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Git Push
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VM Server (Ubuntu)                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Cronjob (runs every 5 minutes)                        │   │
│  │  */5 * * * * /path/to/update_and_restart.sh           │   │
│  └────────────────┬───────────────────────────────────────┘   │
│                   │                                            │
│                   ▼                                            │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  update_and_restart.sh                                 │   │
│  │  1. git fetch                                          │   │
│  │  2. Check for changes                                  │   │
│  │  3. git pull (if changes detected)                     │   │
│  │  4. Run sync_and_ingest.py                             │   │
│  └────────────────┬───────────────────────────────────────┘   │
│                   │                                            │
│                   ▼                                            │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  sync_and_ingest.py                                    │   │
│  │  - Scans catalogs/ directory                           │   │
│  │  - Compares with API state                             │   │
│  │  - Creates/Updates/Deletes collections & items         │   │
│  └────────────────┬───────────────────────────────────────┘   │
│                   │                                            │
│                   │ HTTPS API Calls                            │
│                   ▼                                            │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STAC API (Docker)                             │
│                  https://stac.cyverse.org                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  FastAPI Application                                   │   │
│  │  - Validates requests                                  │   │
│  │  - Processes collections & items                       │   │
│  │  - Stores in PostgreSQL database                       │   │
│  └────────────────┬───────────────────────────────────────┘   │
│                   │                                            │
│                   ▼                                            │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL + PgSTAC Database                          │   │
│  │  - Stores STAC collections                             │   │
│  │  - Stores STAC items                                   │   │
│  │  - Provides spatial queries                            │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### **Ingestion Process Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ingestion Workflow                            │
└─────────────────────────────────────────────────────────────────┘

1. TRIGGER (every 5 minutes)
   │
   ├─ Cronjob executes update_and_restart.sh
   │
   ▼

2. CHECK FOR UPDATES
   │
   ├─ git fetch origin
   ├─ Compare local vs remote
   │
   ├─ No changes? ──────> EXIT (log "No changes detected")
   │
   ├─ Changes detected? ──> Continue
   │
   ▼

3. PULL CHANGES
   │
   ├─ git pull origin main
   ├─ Update local repository
   │
   ▼

4. SCAN CATALOGS
   │
   ├─ Read catalogs/ directory
   ├─ For each subdirectory:
   │   ├─ Load collection.json
   │   └─ Load index.geojson
   │
   ▼

5. COMPARE WITH API
   │
   ├─ GET https://stac.cyverse.org/collections
   ├─ GET https://stac.cyverse.org/collections/{id}/items
   │
   ├─ Determine operations needed:
   │   ├─ Collections to CREATE
   │   ├─ Collections to UPDATE
   │   ├─ Collections to DELETE
   │   ├─ Items to CREATE
   │   ├─ Items to UPDATE
   │   └─ Items to DELETE
   │
   ▼

6. EXECUTE OPERATIONS
   │
   ├─ CREATE new collections
   │   └─ POST /collections
   │
   ├─ UPDATE existing collections
   │   └─ PUT /collections/{id}
   │
   ├─ CREATE new items
   │   └─ POST /collections/{id}/items
   │
   ├─ UPDATE existing items
   │   └─ PUT /collections/{id}/items/{item_id}
   │
   ├─ DELETE removed collections (if enabled)
   │   └─ DELETE /collections/{id}
   │
   └─ DELETE removed items (if enabled)
       └─ DELETE /collections/{id}/items/{item_id}
   │
   ▼

7. LOG RESULTS
   │
   ├─ Write to ingestion.log
   ├─ Write to cron_log_file.log
   │
   └─ Summary:
       ├─ Collections created: X
       ├─ Collections updated: Y
       ├─ Items created: Z
       ├─ Items updated: W
       └─ Errors: N
```

---

## 📁 Directory Structure

```
cyverse-stac/
├── README.md                          # This file
├── catalogs/                          # STAC collections directory
│   ├── joplin/                       # Example: Joplin tornado imagery
│   │   ├── collection.json          # Collection metadata
│   │   └── index.geojson            # Collection items (features)
│   ├── ofo/                          # Example: Open Forest Observatory
│   │   ├── collection.json
│   │   └── index.geojson
│   └── arizona-experiment-station/   # Example: Santa Rita mapping
│       ├── collection.json
│       └── index.geojson
├── update_and_restart.sh             # Main automation script
├── cron_log_file.log                 # Cronjob execution log
└── ingestion.log                     # Detailed ingestion log
```

### **Required Files per Collection**

Each collection MUST be in its own subdirectory under `catalogs/` and MUST contain:

1. **`collection.json`** - STAC Collection metadata
2. **`index.geojson`** - GeoJSON FeatureCollection containing STAC Items

**Example:**
```bash
catalogs/my-new-dataset/
├── collection.json
└── index.geojson
```

---






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

### **STAC Browser**

Explore collections visually:
- **Production:** https://stac.cyverse.org
- **Radiant Earth STAC Browser:** https://radiantearth.github.io/stac-browser/#/external/stac.cyverse.org

---



---

## 📚 Additional Resources

- **STAC Specification:** https://stacspec.org
- **STAC Extensions:** https://stac-extensions.github.io
- **STAC Browser:** https://radiantearth.github.io/stac-browser
- **PySTAC:** https://pystac.readthedocs.io (Python library)
- **STAC Best Practices:** https://github.com/radiantearth/stac-spec/blob/master/best-practices.md

---

**Last Updated:** October 21, 2025
**STAC Version:** 1.0.0
**API URL:** https://stac.cyverse.org
