# CyVerse STAC Catalog

This repository contains STAC (SpatioTemporal Asset Catalog) collections that are automatically ingested into the CyVerse STAC API at [https://stac.cyverse.org](https://stac.cyverse.org).

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Directory Structure](#directory-structure)
- [Adding New Collections](#adding-new-collections)
- [File Format Requirements](#file-format-requirements)
- [How the Automation Works](#how-the-automation-works)
- [Monitoring and Logs](#monitoring-and-logs)
- [Troubleshooting](#troubleshooting)
- [API Access](#api-access)
- [Contributing](#contributing)

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

## ➕ Adding New Collections

### **Step-by-Step Guide**

#### **1. Create Collection Directory**

```bash
cd catalogs/
mkdir my-new-dataset
cd my-new-dataset
```

#### **2. Create `collection.json`**

This file contains metadata about your collection. Follow the [STAC Collection specification](https://github.com/radiantearth/stac-spec/tree/master/collection-spec).

**Minimal Example:**

```json
{
  "id": "my-new-dataset",
  "type": "Collection",
  "stac_version": "1.0.0",
  "description": "Description of your dataset",
  "license": "CC-BY-4.0",
  "extent": {
    "spatial": {
      "bbox": [[-180, -90, 180, 90]]
    },
    "temporal": {
      "interval": [["2020-01-01T00:00:00Z", "2020-12-31T23:59:59Z"]]
    }
  },
  "links": []
}
```

**Required Fields:**
- `id` - Unique identifier (alphanumeric, hyphens, underscores only)
- `type` - Must be "Collection"
- `stac_version` - STAC version (use "1.0.0")
- `description` - Human-readable description
- `license` - License identifier or "proprietary"
- `extent` - Spatial and temporal extent

**Optional but Recommended:**
- `title` - Display name
- `keywords` - Array of keywords
- `providers` - Organizations involved
- `summaries` - Property summaries
- `links` - Related resources

#### **3. Create `index.geojson`**

This file contains the STAC Items (individual assets) in your collection.

**Structure:**

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "stac_version": "1.0.0",
      "id": "item-001",
      "collection": "my-new-dataset",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-94.6, 37.0], [-94.5, 37.0], [-94.5, 37.1], [-94.6, 37.1], [-94.6, 37.0]]]
      },
      "bbox": [-94.6, 37.0, -94.5, 37.1],
      "properties": {
        "datetime": "2020-06-15T12:00:00Z"
      },
      "assets": {
        "image": {
          "href": "https://example.com/path/to/image.tif",
          "type": "image/tiff; application=geotiff; profile=cloud-optimized",
          "title": "COG Image"
        }
      },
      "links": []
    }
  ]
}
```

**Required Fields per Item:**
- `type` - Must be "Feature"
- `stac_version` - STAC version
- `id` - Unique item identifier (CANNOT contain: `: / ? # [ ] @ ! $ & ' ( ) * + , ; =`)
- `collection` - Must match collection `id`
- `geometry` - GeoJSON geometry (or `null`)
- `bbox` - Bounding box [min_lon, min_lat, max_lon, max_lat]
- `properties.datetime` - ISO 8601 datetime or `null`
- `assets` - At least one asset with `href`

#### **4. Commit and Push**

```bash
git add catalogs/my-new-dataset/
git commit -m "Add my-new-dataset collection"
git push origin main
```

#### **5. Wait for Ingestion**

Within 5 minutes, the cronjob will:
1. Detect your changes
2. Pull from GitHub
3. Ingest your collection into the STAC API
4. Log the results

#### **6. Verify Ingestion**

Check that your collection is available:

```bash
# Via curl
curl https://stac.cyverse.org/collections/my-new-dataset

# Via browser
# Open: https://stac.cyverse.org/collections/my-new-dataset
```

Check the logs:

```bash
# On the server
tail -f /home/ubuntu/new-stac-api/cyverse-stac/ingestion.log
```

---

## 📝 File Format Requirements

### **Collection.json Requirements**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier (letters, numbers, hyphens, underscores) |
| `type` | string | ✅ | Must be "Collection" |
| `stac_version` | string | ✅ | STAC specification version (e.g., "1.0.0") |
| `description` | string | ✅ | Detailed description of the collection |
| `license` | string | ✅ | License ID (SPDX) or "proprietary" |
| `extent` | object | ✅ | Spatial and temporal extent |
| `extent.spatial.bbox` | array | ✅ | Array of bounding boxes [[min_lon, min_lat, max_lon, max_lat]] |
| `extent.temporal.interval` | array | ✅ | Array of time intervals [[start, end]] (ISO 8601) |
| `links` | array | ✅ | Array of link objects (can be empty) |
| `title` | string | ⬜ | Human-readable title |
| `keywords` | array | ⬜ | Array of keyword strings |
| `providers` | array | ⬜ | Organizations involved |

### **Index.geojson Requirements**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | Must be "FeatureCollection" |
| `features` | array | ✅ | Array of STAC Item objects |

**Per Item:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | Must be "Feature" |
| `stac_version` | string | ✅ | STAC version (e.g., "1.0.0") |
| `id` | string | ✅ | Unique item ID (no special chars: `, : / ? # [ ] @ ! $ & ' ( ) * + ; =`) |
| `collection` | string | ✅ | Must match parent collection `id` |
| `geometry` | object/null | ✅ | GeoJSON geometry or null |
| `bbox` | array | ✅ | Bounding box [min_lon, min_lat, max_lon, max_lat] |
| `properties` | object | ✅ | Item properties |
| `properties.datetime` | string/null | ✅ | ISO 8601 datetime or null |
| `assets` | object | ✅ | At least one asset with `href` and `type` |
| `links` | array | ✅ | Array of link objects (can be empty) |

### **Asset Format**

```json
{
  "asset-key": {
    "href": "https://example.com/path/to/file.tif",
    "type": "image/tiff; application=geotiff; profile=cloud-optimized",
    "title": "Human-readable title",
    "roles": ["data"]
  }
}
```

**Common Asset Types:**
- Cloud-Optimized GeoTIFF: `image/tiff; application=geotiff; profile=cloud-optimized`
- GeoTIFF: `image/tiff; application=geotiff`
- JPEG: `image/jpeg`
- PNG: `image/png`
- GeoJSON: `application/geo+json`
- JSON: `application/json`

---

## ⚙️ How the Automation Works

### **Cronjob Schedule**

The system runs every 5 minutes:

```bash
*/5 * * * * /home/ubuntu/new-stac-api/cyverse-stac/update_and_restart.sh
```

### **What Happens During Each Run**

1. **Git Fetch** - Check if remote repository has new commits
2. **Compare** - If no changes, exit early (efficient!)
3. **Git Pull** - If changes detected, pull latest code
4. **Scan Catalogs** - Read all `collection.json` and `index.geojson` files
5. **Query API** - Get current state from https://stac.cyverse.org
6. **Determine Operations** - Compare local vs API state
7. **Execute CRUD Operations**:
   - **CREATE** - New collections/items → `POST` to API
   - **UPDATE** - Modified collections/items → `PUT` to API
   - **DELETE** - Removed collections/items → `DELETE` from API (if enabled)
8. **Log Results** - Write detailed logs to files

### **Configuration**

Edit `/home/ubuntu/new-stac-api/stac-fastapi-pgstac/config/ingestion_config.yaml`:

```yaml
# STAC API endpoint
stac_api_url: "https://stac.cyverse.org"

# Path to catalogs directory
catalogs_path: "/home/ubuntu/new-stac-api/cyverse-stac/catalogs"

# Log file location
log_file: "/home/ubuntu/new-stac-api/cyverse-stac/ingestion.log"

# Enable deletion of collections/items not in GitHub
enable_deletes: true

# Number of times to retry failed API requests
retry_attempts: 3

# Delay between retries (seconds)
retry_delay_seconds: 5
```

### **Important Notes**

- **Idempotent** - Safe to run multiple times; won't duplicate data
- **Change Detection** - Only processes when GitHub has new commits
- **Atomic Operations** - Each collection/item processed independently
- **Error Handling** - Continues processing even if some items fail
- **Logging** - All operations logged for audit trail

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

## 🔧 Troubleshooting

### **Common Issues**

#### **Issue: Collection not showing up in API**

**Possible Causes:**
1. Git push didn't complete successfully
2. Cronjob hasn't run yet (wait 5 minutes)
3. Invalid JSON syntax
4. Missing required fields

**Solutions:**
```bash
# Check if changes are on GitHub
git log --oneline -5

# Manually trigger ingestion
/home/ubuntu/new-stac-api/cyverse-stac/update_and_restart.sh

# Check logs for errors
tail -100 /home/ubuntu/new-stac-api/cyverse-stac/ingestion.log | grep ERROR
```

#### **Issue: Items failing with "ID cannot contain" error**

**Cause:** Item IDs contain invalid characters (`: / ? # [ ] @ ! $ & ' ( ) * + , ; =`)

**Solution:**
```bash
# Fix item IDs in index.geojson
# Replace commas and special characters with hyphens or underscores
# Example: "item-001, item-002" → "item-001-item-002"
```

#### **Issue: "Resource already exists (409)" errors**

**Cause:** Item already exists in API with same ID

**Solutions:**
- This is expected if re-running ingestion (idempotent behavior)
- If you want to update, ensure the item actually changed
- Check for duplicate IDs in your `index.geojson`

#### **Issue: Git pull fails**

**Possible Causes:**
1. Local changes conflict with remote
2. Git credentials expired
3. Network connectivity

**Solutions:**
```bash
cd /home/ubuntu/new-stac-api/cyverse-stac
git status
git pull origin main
```

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

## 🤝 Contributing

### **Guidelines**

1. **Validate JSON** before committing:
   ```bash
   # Validate collection.json
   cat catalogs/my-collection/collection.json | jq '.'

   # Validate index.geojson
   cat catalogs/my-collection/index.geojson | jq '.'
   ```

2. **Follow STAC Specification**:
   - Collection Spec: https://github.com/radiantearth/stac-spec/tree/master/collection-spec
   - Item Spec: https://github.com/radiantearth/stac-spec/tree/master/item-spec

3. **Use Descriptive Commit Messages**:
   ```bash
   git commit -m "Add Landsat 8 collection for Arizona"
   git commit -m "Update joplin collection metadata"
   git commit -m "Fix item IDs in OFO collection"
   ```

4. **Test Locally** (if possible):
   - Validate JSON syntax
   - Check required fields
   - Ensure item IDs don't contain special characters

5. **Monitor Logs** after pushing:
   - Wait 5 minutes for cronjob
   - Check ingestion logs for errors
   - Verify data in API

### **Best Practices**

- ✅ Use clear, unique collection IDs
- ✅ Provide descriptive titles and descriptions
- ✅ Include accurate spatial and temporal extents
- ✅ Use Cloud-Optimized GeoTIFFs (COGs) for raster data
- ✅ Keep asset URLs publicly accessible
- ✅ Add keywords for discoverability
- ✅ Document data sources and licenses
- ❌ Don't use special characters in IDs
- ❌ Don't commit large binary files (images, etc.)
- ❌ Don't commit sensitive information

---

## 📚 Additional Resources

- **STAC Specification:** https://stacspec.org
- **STAC Extensions:** https://stac-extensions.github.io
- **STAC Browser:** https://radiantearth.github.io/stac-browser
- **PySTAC:** https://pystac.readthedocs.io (Python library)
- **STAC Best Practices:** https://github.com/radiantearth/stac-spec/blob/master/best-practices.md
- **CyVerse:** https://cyverse.org
- **TiTiler:** https://titiler.cyverse.org

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the logs for error messages
3. Open an issue on GitHub
4. Contact the CyVerse STAC team

---

**Last Updated:** October 21, 2025
**STAC Version:** 1.0.0
**API URL:** https://stac.cyverse.org
