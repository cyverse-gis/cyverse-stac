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

`collection.json` - contains the relevant metadata which you want to be visible in a STAC Browser

??? Abstract "collection.json"

    ```json
    {
        "id": "Open-Forest-Observatory",
        "description": "The [Open Forest Observatory](https://openforestobservatory.org) Project",
        "stac_version": "1.0.0",
        "license": "public-domain",
        "links": [
            {
                "rel": "license",
                "href": "https://creativecommons.org/licenses/publicdomain/",
                "title": "public domain"
            }
        ],
        "type": "Collection",
        "extent": {
            "spatial": {
                "bbox": [
                    [
                        -106.79191589355467,
                        35.648927129774336,
                        -106.49803161621092,
                        35.95744398067361
                    ]
                ]
            },
            "temporal": {
                "interval": [
                    [
                    "2022-01-01T12:00:00Z",
                    "2023-02-25T12:00:00Z"
                    ]
                ]
            }
        }
    }
    ```

`index.geojson` - list of `Features` in a `FeatureCollection` that corresponds to the `Collection`

??? Abstract "`index.geojson`"

    ```json
     {
        "type": "FeatureCollection",
        "features": [
            {
              "type": "Feature",
              "collection": "Open-Forest-Observatory",
              "stac_version": "1.0.0",
              "stac_extensions": [
                "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
                "https://stac-extensions.github.io/raster/v1.1.0/schema.json",
                "https://stac-extensions.github.io/eo/v1.0.0/schema.json"
              ],
              "id": "chm_cog.tif",
              "geometry": {
                "type": "Polygon",
                "coordinates": [
                  [
                    [
                      -106.79191589355467,
                      35.648927129774336
                    ],
                    [
                      -106.49803161621092,
                      35.648927129774336
                    ],
                    [
                      -106.49803161621092,
                      35.95744398067361
                    ],
                    [
                      -106.79191589355467,
                      35.95744398067361
                    ],
                    [
                      -106.79191589355467,
                      35.648927129774336
                    ]
                  ]
                ]
              },
              "bbox": [
                -106.79191589355467,
                35.648927129774336,
                -106.49803161621092,
                35.95744398067361
              ],
              "properties": {
                "proj:epsg": 3857,
                "proj:geometry": {
                  "type": "Polygon",
                  "coordinates": [
                    [
                      [
                        -11888021.698108606,
                        4252421.194589211
                      ],
                      [
                        -11855306.65000255,
                        4252421.194589211
                      ],
                      [
                        -11855306.65000255,
                        4294767.308259198
                      ],
                      [
                        -11888021.698108606,
                        4294767.308259198
                      ],
                      [
                        -11888021.698108606,
                        4252421.194589211
                      ]
                    ]
                  ]
                },
                "proj:bbox": [
                  -11888021.698108606,
                  4252421.194589211,
                  -11855306.65000255,
                  4294767.308259198
                ],
                "proj:shape": [
                  141824,
                  109568
                ],
                "proj:transform": [
                  0.29858214173896974,
                  0,
                  -11888021.698108606,
                  0,
                  -0.29858214173896974,
                  4294767.308259198,
                  0,
                  0,
                  1
                ],
                "proj:projjson": {
                  "$schema": "https://proj.org/schemas/v0.4/projjson.schema.json",
                  "type": "ProjectedCRS",
                  "name": "WGS 84 / Pseudo-Mercator",
                  "base_crs": {
                    "name": "WGS 84",
                    "datum": {
                      "type": "GeodeticReferenceFrame",
                      "name": "World Geodetic System 1984",
                      "ellipsoid": {
                        "name": "WGS 84",
                        "semi_major_axis": 6378137,
                        "inverse_flattening": 298.257223563
                      }
                    },
                    "coordinate_system": {
                      "subtype": "ellipsoidal",
                      "axis": [
                        {
                          "name": "Latitude",
                          "abbreviation": "lat",
                          "direction": "north",
                          "unit": "degree"
                        },
                        {
                          "name": "Longitude",
                          "abbreviation": "lon",
                          "direction": "east",
                          "unit": "degree"
                        }
                      ]
                    },
                    "id": {
                      "authority": "EPSG",
                      "code": 4326
                    }
                  },
                  "conversion": {
                    "name": "unnamed",
                    "method": {
                      "name": "Popular Visualisation Pseudo Mercator",
                      "id": {
                        "authority": "EPSG",
                        "code": 1024
                      }
                    },
                    "parameters": [
                      {
                        "name": "Latitude of natural origin",
                        "value": 0,
                        "unit": "degree",
                        "id": {
                          "authority": "EPSG",
                          "code": 8801
                        }
                      },
                      {
                        "name": "Longitude of natural origin",
                        "value": 0,
                        "unit": "degree",
                        "id": {
                          "authority": "EPSG",
                          "code": 8802
                        }
                      },
                      {
                        "name": "False easting",
                        "value": 0,
                        "unit": "metre",
                        "id": {
                          "authority": "EPSG",
                          "code": 8806
                        }
                      },
                      {
                        "name": "False northing",
                        "value": 0,
                        "unit": "metre",
                        "id": {
                          "authority": "EPSG",
                          "code": 8807
                        }
                      }
                    ]
                  },
                  "coordinate_system": {
                    "subtype": "Cartesian",
                    "axis": [
                      {
                        "name": "Easting",
                        "abbreviation": "",
                        "direction": "east",
                        "unit": "metre"
                      },
                      {
                        "name": "Northing",
                        "abbreviation": "",
                        "direction": "north",
                        "unit": "metre"
                      }
                    ]
                  },
                  "id": {
                    "authority": "EPSG",
                    "code": 3857
                  }
                },
                "datetime": "2023-04-12T20:19:05.989194Z"
              },
              "links": [],
              "assets": {
                "data": {
                  "href": "https://data.cyverse.org/dav-anon/iplant/home/tswetnam/jemez/chm_cog.tif",
                  "type": "image/tiff; application=geotiff",
                  "raster:bands": [
                    {
                      "data_type": "uint8",
                      "scale": 1,
                      "offset": 0,
                      "sampling": "area",
                      "statistics": {
                        "mean": 37.61441723935138,
                        "minimum": 0,
                        "maximum": 255,
                        "stddev": 57.379448784450744,
                        "valid_percent": 96.65515013415404
                      },
                      "histogram": {
                        "count": 11,
                        "min": 0,
                        "max": 255,
                        "buckets": [
                          517158,
                          39168,
                          41201,
                          44410,
                          48328,
                          41809,
                          31172,
                          15240,
                          4904,
                          491
                        ]
                      }
                    },
                    {
                      "data_type": "uint8",
                      "scale": 1,
                      "offset": 0,
                      "sampling": "area",
                      "statistics": {
                        "mean": 46.35795866974706,
                        "minimum": 0,
                        "maximum": 255,
                        "stddev": 64.61711636383107,
                        "valid_percent": 96.65515013415404
                      },
                      "histogram": {
                        "count": 11,
                        "min": 0,
                        "max": 255,
                        "buckets": [
                          478873,
                          42203,
                          35378,
                          38875,
                          49278,
                          53347,
                          50634,
                          27259,
                          7593,
                          441
                        ]
                      }
                    },
                    {
                      "data_type": "uint8",
                      "scale": 1,
                      "offset": 0,
                      "sampling": "area",
                      "statistics": {
                        "mean": 40.6277738585321,
                        "minimum": 0,
                        "maximum": 212,
                        "stddev": 54.02405921611601,
                        "valid_percent": 96.65515013415404
                      },
                      "histogram": {
                        "count": 11,
                        "min": 0,
                        "max": 212,
                        "buckets": [
                          461045,
                          39961,
                          37265,
                          41672,
                          52391,
                          65596,
                          55782,
                          26377,
                          3671,
                          121
                        ]
                      }
                    }
                  ],
                  "eo:bands": [
                    {
                      "name": "b1",
                      "description": "red"
                    },
                    {
                      "name": "b2",
                      "description": "green"
                    },
                    {
                      "name": "b3",
                      "description": "blue"
                    }
                  ]
                }
              }
            }
        ]
    }   
    ```
