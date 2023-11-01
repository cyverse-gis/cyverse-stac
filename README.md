# cyverse-stac

This repository contains documentation and scripts related to Cyverse's efforts on SpatioTemporal Assets Catalogs (STAC). Documentation is being served through Github pages at
 [https//cyverse-gis.github.io/cyverse-stac](https://cyverse-gis.github.io/cyverse-stac).

[![pages-build-deployment](https://github.com/cyverse-gis/cyverse-stac/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/cyverse-gis/cyverse-stac/actions/workflows/pages/pages-build-deployment)

Built using [MkDocs](https://www.mkdocs.org/) with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) 

##Build MkDocs locally
To build and edit the MkDocs locally, do the following. 
```
git clone https://github.com/cyverse-gis/cyverse-stac

cd cyverse-stac

pip install -r requirements.txt

python3 -m mkdocs serve
```
Open a browser tab and type `localhost:8000`
:) ;)


## Run Docker
I have created python code in a juypter notbook that will create STAC catalogs from crawling over geospatial assets. You can run this notebook in a Docker container. 

```
Docker run -p 8888:8888 jeffgillan/stac-creation:0.1
```
