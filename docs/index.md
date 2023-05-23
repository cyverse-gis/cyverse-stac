# CyVerse STAC 

**SpatioTemporal Asset Catalog (STAC)** is a json-based metadata standard to describe geospatial data. It's goal is 
to make geospatial data more easily worked with, indexed, and discovered. 

[Cyverse](https://cyverse.org) is developing STAC capabilities to share out remotely sensed imagery that is stored in the [Cyverse Datastore](https://cyverse.org/data-store)

This documentation will cover: 

1. Creating STAC compliant json/geojson files
2. Differences between static and dynamic STAC catalogs
3. Instructions for how Cyverse is deploying a STAC API
4. STAC browser 


## Important Resources
[StacSpec](https://stacspec.org/en) is the official documentation for the STAC standard.

[pystac](https://pystac.readthedocs.io/en/stable/) is a python library for working with STAC data, which thus far has been used for creating STAC compliant json/geojson files  

The [STACIndex](https://stacindex.org/) is a community driven index of STAC catalogs, learning resources, and tools.

The [Radiant Earth Stac Browser](https://radiantearth.github.io/stac-browser/#/) a tool that allows you to graphically browse through static and API STAC catalogs. 




Tyson has the STAC API going. I am trying to manually improve the geojson features. I access it by using VSCode. I ssh remote connect to the 'stac-api' virtual machine. 

We currently have it set up to where `collection.json` and `index.geojson` files are located at `/home/ubuntu/cyverse-stac/catalogs`. You can add new collections by adding a new folder and having 2 files within it: `collection.json` and `index.geojson`. `/home/unbuntu/cyverse-stac/catalogs` is simply holding all of the catalogs. The docker-compose that creates the STAC API is located at `/home/unbuntu/stac-fastapi`.

If you add new catalogs, then you must also add that information to the `home/ubuntu/stac-fastapi/scripts/ingest_cyverse.py`


After I make changes to the `collection.json`, `index.geojson`, or ingest_cyverse.py`, I need to restart the stac-api docker compose. 
```
cd /home/ubuntu/stac-fastapi/
docker-compose restart
```
