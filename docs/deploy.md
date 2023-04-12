# Deployments

## Install :simple-docker: Docker

If the image does not have Docker, install it.

```bash
sudo apt update
sudo apt install docker.io
```

Add the `ubuntu` user or your `username` to the Docker group

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

Close your connection and reboot the instance. 

Install `docker-compose`

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
```

## Install :octicons-lock-24: CaddyServer

To secure both instances over `https://` we are runninng [CaddyServer](https://caddyserver.com/) with a reverse proxy to the public IP addresses.

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

Suggest using a `tmux` session for terminal.

| usage  | Apple Keyboard | Linux keyboard |
|--------|----------------|----------------|
| start tmux | `tmux` | `tmux` |
| detach terminal | hold `^ control` + `B`, then `D` | hold `Ctrl` + `B`, then `D` |
| find session | `tmux ls` | same |
| re-attach session | `tmux attach -t <session #>` | same |
| split-screen vertical | hold `^ control` + `B`, then hold `shift` + `%` | hold `Ctrl` + `B`, then hold `shift` + `%` |
| split-screen horizontal | hold `^ control` + `B`, then hold `shift` + `"` | hold `Ctrl` + `B`, then hold `shift` + `"` |
| Switch pane | hold `^ control` + `B`, then arrow key (left or right, up or down) | hold `Ctrl` + `B`, then arrow key (left or right, up or down) |
| Close the session | hold `^ control` + `B`, then `X` | hold `Ctrl` + `B`, then `X` |

Ctrl + b + % to split the current pane vertically.
Ctrl + b + " to split the current pane horizontally.
Ctrl + b + x to close the current pane.

## Run :simple-docker: STAC API

[:simple-github: stac-utils/stac-fastapi](https://github.com/stac-utils/stac-fastapi){target=_blank}

```bash
git clone https://github.com/stac-utils/stac-fastapi.git

cd stac-fastapi
```

There are two configuration files which need to be updated:

`docker-compose.yaml` - provisions the deployment of a [PostgreSQL](https://www.postgresql.org/docs/) database and [SQL lchemy](https://www.sqlalchemy.org/) Python SQL toolkit and object relational mapper mapped to a STAC `.json` Collection and `.geojson` Feature Collection.

`/scripts/ingest_collection.py` - there is a sample `.py` ingestion file called "joplin" which you can make a copy of and edit.

There is one sample STAC catalog directory which can be removed or used for testing:

`/stac_fastapi/testdata/joplin` - is the test dataset which is deployed by default. 

### Create new Collections

The `.json` Collection which will be used in the API must be present on the VM - we're still working out whether to set up a `cron` job or keep the file on GitHub instead.

```bash
cd ~/stac-fastapi/stac_fastapi/

mkdir cyverse-data

cd cyverse-data

mkdir <new-collection-name

```

#### Edit `docker-compose.yml` 

The `stac-fastapi` Docker-Compose will start up multiple containers, including a database which relies on the sample data.

Note: the GitHub repository for `stac-fastapi` expects containers from GitHub Container Registry, not from DockerHub - update the `docker-compose.yml` to use the specific containers and tag version 

??? Abstract "docker-compose.yml"

    Copy/Paste

    ```yaml
    version: '3'
    services:
      app-sqlalchemy:
        container_name: stac-fastapi-sqlalchemy
        image: ghcr.io/stac-utils/stac-fastapi:main-sqlalchemy
        build:
          context: .
          dockerfile: docker/Dockerfile
        platform: linux/amd64
        environment:
          - APP_HOST=0.0.0.0
          - APP_PORT=8081
          - RELOAD=true
          - ENVIRONMENT=local
          - POSTGRES_USER=username
          - POSTGRES_PASS=password
          - POSTGRES_DBNAME=postgis
          - POSTGRES_HOST_READER=database
          - POSTGRES_HOST_WRITER=database
          - POSTGRES_PORT=5432
          - WEB_CONCURRENCY=10
        ports:
          - "8081:8081"
        volumes:
          - ./stac_fastapi:/app/stac_fastapi
          - ./scripts:/app/scripts
        depends_on:
          - database
        command: bash -c "./scripts/wait-for-it.sh database:5432 && python -m stac_fastapi.sqlalchemy.app"

      app-pgstac:
        container_name: stac-fastapi-pgstac
        image: ghcr.io/stac-utils/stac-fastapi:main-pgstac
        platform: linux/amd64
        environment:
          - APP_HOST=0.0.0.0
          - APP_PORT=8082
          - RELOAD=true
          - ENVIRONMENT=local
          - POSTGRES_USER=username
          - POSTGRES_PASS=password
          - POSTGRES_DBNAME=postgis
          - POSTGRES_HOST_READER=database
          - POSTGRES_HOST_WRITER=database
          - POSTGRES_PORT=5432
          - WEB_CONCURRENCY=10
          - VSI_CACHE=TRUE
          - GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES
          - GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR
          - DB_MIN_CONN_SIZE=1
          - DB_MAX_CONN_SIZE=1
          - USE_API_HYDRATE=${USE_API_HYDRATE:-false}
        ports:
          - "8082:8082"
        volumes:
          - ./stac_fastapi:/app/stac_fastapi
          - ./scripts:/app/scripts
        depends_on:
          - database
        command: bash -c "./scripts/wait-for-it.sh database:5432 && python -m stac_fastapi.pgstac.app"

      database:
        container_name: stac-db
        image: ghcr.io/stac-utils/pgstac:v0.6.12
        environment:
          - POSTGRES_USER=username
          - POSTGRES_PASSWORD=password
          - POSTGRES_DB=postgis
          - PGUSER=username
          - PGPASSWORD=password
          - PGHOST=localhost
          - PGDATABASE=postgis
        ports:
          - "5439:5432"
        command: postgres -N 500

    # Load joplin demo dataset into the SQLAlchemy Application
    #  loadjoplin-sqlalchemy:
    #    image: ghcr.io/stac-utils/stac-fastapi:main-sqlalchemy
    #    environment:
    #      - ENVIRONMENT=development
    #      - POSTGRES_USER=username
    #      - POSTGRES_PASS=password
    #      - POSTGRES_DBNAME=postgis
    #      - POSTGRES_HOST=database
    #      - POSTGRES_PORT=5432
    #    volumes:
    #      - ./stac_fastapi:/app/stac_fastapi
    #      - ./scripts:/app/scripts
    #    command: >
    #      bash -c "./scripts/wait-for-it.sh app-sqlalchemy:8081 -t 60 && cd stac_fastapi/sqlalchemy && alembic upgrade head && python /app/scripts/ingest_joplin.py http://app-sqlalchemy:8081"
    #    depends_on:
    #      - database
    #      - app-sqlalchemy
    #
    #  # Load joplin demo dataset into the PGStac Application
    #  loadjoplin-pgstac:
    #    image: ghcr.io/stac-utils/stac-fastapi:main-pgstac
    #    environment:
    #      - ENVIRONMENT=development
    #    volumes:
    #      - ./stac_fastapi:/app/stac_fastapi
    #      - ./scripts:/app/scripts
    #    command:
    #      - "./app/scripts/wait-for-it.sh"
    #      - "-t"
    #      - "60"
    #      - "app-pgstac:8082"
    #      - "--"
    #      - "python"
    #      - "/app/scripts/ingest_joplin.py"
    #      - "http://app-pgstac:8082"
    #    depends_on:
    #      - database
    #      - app-pgstac
    #
    ##################################
    ## CyVerse Testing Stuff
    ##
    ##################################

    # Load cyverse demo dataset into the SQLAlchemy Application
      loadcyverse-sqlalchemy:
        image: ghcr.io/stac-utils/stac-fastapi:main-sqlalchemy
        environment:
          - ENVIRONMENT=development
          - POSTGRES_USER=username
          - POSTGRES_PASS=password
          - POSTGRES_DBNAME=postgis
          - POSTGRES_HOST=database
          - POSTGRES_PORT=5432
        volumes:
          - ./stac_fastapi:/app/stac_fastapi
          - ./scripts:/app/scripts
        command: >
          bash -c "/app/scripts/wait-for-it.sh app-sqlalchemy:8081 -t 60 && cd /app/stac_fastapi/sqlalchemy && alembic upgrade head && python /app/scripts/ingest_cyverse.py http://app-sqlalchemy:8081"
        depends_on:
          - database
          - app-sqlalchemy

      # Load cyverse demo dataset into the PGStac Application
      loadcyverse-pgstac:
        image: ghcr.io/stac-utils/stac-fastapi:main-pgstac
        environment:
          - ENVIRONMENT=development
        volumes:
          - ./stac_fastapi:/app/stac_fastapi
          - ./scripts:/app/scripts
        command:
          - "/app/scripts/wait-for-it.sh"
          - "-t"
          - "60"
          - "app-pgstac:8082"
          - "--"
          - "python"
          - "/app/scripts/ingest_cyverse.py"
          - "http://app-pgstac:8082"
        depends_on:
          - database
          - app-pgstac


    ########################################
    ## End CyVerse Testing Stuff
    ##
    #########################################
    
    networks:
      default:
        name: stac-fastapi-network

    ```

#### Edit `ingest_collections.py`

??? Abstract "`ingest_collections.py`"

    ```python
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

    # Ingest CyVerse Collections 

    cyversedata = workingdir.parent / "stac_fastapi" / "cyverse-data" / "arizona-experiment-station"

    def ingest_cyverse_data(app_host: str = app_host, data_dir: Path = cyversedata):
        """ingest data."""

        with open(data_dir / "collection.json") as f:
            collection = json.load(f)

        post_or_put(urljoin(app_host, "/collections"), collection)

        with open(data_dir / "index.geojson") as f:
            index = json.load(f)

        for feat in index["features"]:
            post_or_put(urljoin(app_host, f"collections/{collection['id']}/items"), feat)

    ## Ingest Joplin Collections

    joplindata = workingdir.parent / "stac_fastapi" / "cyverse-data" / "joplin"

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
    ```

### Start :simple-docker: Docker-Compose

```bash
cd ~/stac-fastapi
```

In the `/stac-fastapi` directory there is a `docker-compose.yml` which is set to point at a demo dataset called `joplin` you will need to modify the `docker-compose.yml` and point it at a new `collection.json` and `index.geojson` 

Note: if you do not modify the `docker-compose.yml` the sample dataset will be shown.

Start Docker-Compose in detached mode. The `-d` flag will start Docker Compose in the background

```bash
docker-compose up -d 
```

### Start CaddyServer

Caddy privileges will need to be escalated before it can use port `:443`

```bash
sudo setcap CAP_NET_BIND_SERVICE=+eip $(which caddy)
```

Start a fresh `tmux` session

```bash
caddy reverse-proxy --from stac.cyverse.org --to localhost:8080 --change-host-header &
```

Detach the session

## Instructions for :simple-docker: DevSeed TiTiler

[TiTiler Documentation](https://developmentseed.org/titiler/)

https://titiler.cyverse.org/

### Start Docker

We are running TiTiler with Docker

```bash
docker run --name titiler \
    -p 8000:8000 \
    --env PORT=8000 \
    --env WORKERS_PER_CORE=1 \
    --rm -it ghcr.io/developmentseed/titiler:latest
```

### Start CaddyServer

Start a fresh `tmux` session 

Star the Caddy Server with a reverse proxy, pointing at the same port as Docker

```bash
caddy reverse-proxy --from titler.cyverse.org --to localhost:8000 --change-host-header &
```

Detach the session