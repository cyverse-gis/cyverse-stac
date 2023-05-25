# CyVerse STAC 

**SpatioTemporal Asset Catalog (STAC)** is a json-based metadata standard to describe geospatial data. It's goal is 
to make geospatial data more easily worked with, indexed, and discovered. 

[Cyverse](https://cyverse.org) is developing STAC capabilities to share out remotely sensed imagery that is stored in the [Cyverse Datastore](https://cyverse.org/data-store)

This documentation will cover: 

1. Creating STAC compliant json/geojson files
2. Differences between static and dynamic STAC catalogs
3. Instructions for how Cyverse is deploying a STAC API
4. How to add new collections to the API
5. STAC browser 
6. TiTiler


## Important Resources
[StacSpec](https://stacspec.org/en) is the official documentation for the STAC standard.

[pystac](https://pystac.readthedocs.io/en/stable/) is a python library for working with STAC data, which thus far has been used for creating STAC compliant json/geojson files  

The [STACIndex](https://stacindex.org/) is a community driven index of STAC catalogs, learning resources, and tools.

The [Radiant Earth Stac Browser](https://radiantearth.github.io/stac-browser/#/) a tool that allows you to graphically browse through static and API STAC catalogs. 




