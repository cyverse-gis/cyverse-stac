Within this repo there is a directory called `scripts`. Within it is a jupyter notebook `STAC_creation_latest.ipynb` that has python code for creating STAC json and geojson files from crawling over imagery assets. The code primarily uses the [pystac](https://pystac.readthedocs.io/en/stable/) library to create the STAC metadata. The STAC creation code is in active development.

### Here is what the code currently does:

* Users manually input metadata about the geospatial imagery products. These include: Title of the collection, description of collection and items, provider name and info.

* Users can specify the collection date with a single entry or they can provide a csv file that lists each of the assets and their date of collection. 

* The script crawls over a user defined directory (e.g., in Cyverse DataStore) and looks for geotiff and cloud optimized geotiff (COG) files. 

* It pulls out the projection, ground sampling distance (gsd) and footprint of the imagery asset. If an asset does not have a projection, the gsd will return 0.00 meters. 

* It will assign multiple assets to a single item. This is also based on a user provided csv file that lists which assets should belong to which item. 

* It can output a static STAC with the structure catalog>>collection>>items. These will have relative links.

* It can output a dynamic STAC that can be ingesting into a STAC API. The structure is: collection>>index.geojson. It has absolute links. 


### Additional Functionality that is Needed

* Find point clouds in a directory (laz, copc) and index them in STAC. There is a 'pointcloud' extension in pystac that should make it possible. 

* Link out to [COPC Viewer](viewer.copc.io) for point cloud visualization
