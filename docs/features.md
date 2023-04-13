##  Creating new Features for FeatureCollections

### JPEG / DNG / TIF

TODO

### COGs & GEOTiff

Create STAC compliant `Features` .json for COGs (GeoTIFF) using the [https://titiler.cyverse.org/docs#/Cloud%20Optimized%20GeoTIFF/Create_STAC_Item_cog_stac_get](https://titiler.cyverse.org/docs#/Cloud%20Optimized%20GeoTIFF/Create_STAC_Item_cog_stac_get){target=_blank}

Copy / Paste in the URL of an asset which you want to generate a STAC .json for, the request should return `200` with a JSON that can be copied into a FeatureCollection `index.geojson`

```json
{
    "type": "FeatureCollection",
    "features": [
        {
            <paste first JSON Feature here>,
            ..., 
            <paste n JSON Feature here >
        }
}
```

The resulting output should be a STAC compliant Feature JSON

### COPC / LAZ

TODO