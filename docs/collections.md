# STAC Collections

CyVerse features a set of public datasets that are curated in the CyVerse DataStore.

The assets are primarily available from the DataStore over the public WebDAV.

https://data.cyverse.org/dav-anon/

All assets must be shared as `read-only` with the `anonymous` user in the iRODS environment (accessed via the Discovery Environment, Share Data feature) in order for them to be visible and downloadable.


## New Collections

The `.json` Collections visible in the API must be present inside the container when `docker-compose up -d` is run. 

We are maintaining our CyVerse STAC Catalog collection in this GitHub Repository. The `.json` Collections and `.geojson` Feature Collections inside the `/catalogs` directory are organized by project.

The `cyverse-stac` repository must be cloned to the same `stac.cyverse.org` virtual machine along side the `stac-fastapi` repository. 

```bash
git clone https://github.com/tyson-swetnam/cyverse-stac
```

When a new collection is added to the `/catalogs` directory, it should be placed into its own directory, e.g., `ofo`, and contain two files:


