"""Ingest sample data during docker-compose"""
import json
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests

workingdir = Path(__file__).parent.absolute()

app_host = sys.argv[1]

if not app_host:
    raise Exception("You must include full path/port to stac instance")

def post_or_put(url: str, data: dict):
    """Post or put data to url."""
    r = requests.post(url, json=data)
    if r.status_code == 409:
        new_url = url if data["type"] == "Collection" else url + f"/{data['id']}"
        # Exists, so update
        r = requests.put(new_url, json=data)
        # Unchanged may throw a 404
        if not r.status_code == 404:
            r.raise_for_status()
    else:
        r.raise_for_status()

##################################
#
# Begin Collection Ingestion
#
##################################

## Ingest Open Forest Observatory Collections

ofodata =  Path("/app/cyverse-stac/catalogs/ofo")

def ingest_ofo_data(app_host: str = app_host, data_dir: Path = ofodata):
    """ingest data."""

    with open(data_dir / "collection.json") as f:
        collection = json.load(f)

    post_or_put(urljoin(app_host, "/collections"), collection)

    with open(data_dir / "index.geojson") as f:
        index = json.load(f)

    for feat in index["features"]:
        post_or_put(urljoin(app_host, f"collections/{collection['id']}/items"), feat)


# Ingest Arizona Experiment Station Collections 

srerdata =  Path("/app/cyverse-stac/catalogs/arizona-experiment-station")

def ingest_cyverse_data(app_host: str = app_host, data_dir: Path = srerdata):
    """ingest data."""

    with open(data_dir / "collection.json") as f:
        collection = json.load(f)

    post_or_put(urljoin(app_host, "/collections"), collection)

    with open(data_dir / "index.geojson") as f:
        index = json.load(f)

    for feat in index["features"]:
        post_or_put(urljoin(app_host, f"collections/{collection['id']}/items"), feat)

## Ingest Joplin Collections

joplindata = Path("/app/cyverse-stac/catalogs/joplin")

def ingest_joplin_data(app_host: str = app_host, data_dir: Path = joplindata):
    """ingest data."""

    with open(data_dir / "collection.json") as f:
        collection = json.load(f)

    post_or_put(urljoin(app_host, "/collections"), collection)

    with open(data_dir / "index.geojson") as f:
        index = json.load(f)

    for feat in index["features"]:
        post_or_put(urljoin(app_host, f"collections/{collection['id']}/items"), feat)

if __name__ == "__main__":
    ingest_cyverse_data()
    ingest_joplin_data()
    ingest_ofo_data()
