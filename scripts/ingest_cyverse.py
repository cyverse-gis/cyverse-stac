"""Ingest data during docker-compose"""
import os
import json
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests

APP_HOST = sys.argv[1]

collection_list_file = Path('/app/cyverse-stac/api_collections.txt')

if not APP_HOST:
    raise Exception("You must include full path/port to stac instance")

def post_or_put(url: str, data: dict):
    """Post or put data to url."""
    res = requests.post(url, json=data, timeout=500)
    if res.status_code == 409:
        new_url = url if data["type"] == "Collection" else url + f"/{data['id']}"
        # Exists, so update
        res = requests.put(new_url, json=data, timeout=500)
        # Unchanged may throw a 404
        if not res.status_code == 404:
            res.raise_for_status()
    else:
        res.raise_for_status()

##################################
#
# Begin Collection Ingestion
#
##################################

def ingest_data(data_dir: Path, app_host: str = APP_HOST) -> None:
    """ingest data."""

    with open(os.path.join(data_dir, "collection.json"), encoding='utf-8') as infile:
        collection = json.load(infile)

    post_or_put(urljoin(app_host, "/collections"), collection)

    with open(os.path.join(data_dir, "index.geojson"), encoding='utf-8') as infile:
        index = json.load(infile)

    for feat in index["features"]:
        post_or_put(urljoin(app_host, f"collections/{collection['id']}/items"), feat)


if __name__ == "__main__":

    # Loop through the list of paths stored in the file and ingest them
    with open(collection_list_file, 'r', encoding='utf-8') as coll_list_in:
        for cur_coll_path in coll_list_in:
            # Make sure we have a valid line and that the file exists
            if cur_coll_path.strip():
                ingest_data(Path(cur_coll_path))
