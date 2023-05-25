
On the `cyverse-api` vm, the github repo [https://github.com/cyverse-gis/cyverse-stac](https://github.com/cyverse-gis/cyverse-stac){target=_blank} has been cloned to the vm directory `/home/ubuntu/cyverse-stac`. This repo holds the STAC json and geojson files that are ingested by the STAC API

The STAC files are held within the `/cyverse-stac/catalog` directory within the repo.

Within `/cyverse-stac/catalog` are directories that hold `collection.json` files and `index.geojson` files.


When a new collection is added to the `/catalogs` directory, it should be placed into its own directory, e.g., `ofo`, and contain the `colletion.json` file and the `index.geojson` file. 


## New Collections

The `.json` Collections visible in the API must be present inside the container when `docker-compose up -d` is run. 


The `cyverse-stac` repository must be cloned to the same `stac.cyverse.org` virtual machine along side the `stac-fastapi` repository. 




The docker-compose that creates the STAC API is located at `/home/unbuntu/stac-fastapi`.

If you add new catalogs, then you must also add that information to the `home/ubuntu/stac-fastapi/scripts/ingest_cyverse.py`


After I make changes to the `collection.json`, `index.geojson`, or ingest_cyverse.py`, I need to restart the stac-api docker compose. 
```
cd /home/ubuntu/stac-fastapi/
docker-compose restart
```