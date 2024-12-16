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

<br/>
<br/>


## Important Resources
[StacSpec](https://stacspec.org/en) is the official documentation for the STAC standard.

[pystac](https://pystac.readthedocs.io/en/stable/) is a python library for creating STAC compliant json/geojson files  

[pystac-client](https://pystac-client.readthedocs.io/en/stable/index.html) is a python library for accessing and querying STAC catalogs

The [STACIndex](https://stacindex.org/) is a community driven index of STAC catalogs, learning resources, and tools.

The [Radiant Earth Stac Browser](https://radiantearth.github.io/stac-browser/#/) a tool that allows you to graphically browse through static and API STAC catalogs. 

<br/>
<br/>

## Cyverse STAC API

We are currently running two virtual machines (vm) on CyVerse OpenStack Cloud 

[https://tombstone-cloud.cyverse.org/](https://tombstone-cloud.cyverse.org/)

<br/>

One vm is called `stac-api` and is served to the domain [**https://stac.cyverse.org**](https://stac.cyverse.org). This vm is running a Radiant Earth `stac-fastapi` [STAC API](https://stac-utils.github.io/stac-fastapi/). It is currently running through docker-compose.

It is a `small` instance (2 virtual CPUs, 16 GB RAM) with Ubuntu 22.04, Docker, and Docker-Compose.

<br/>

The other vm is running [DevSeed TiTiler](https://developmentseed.org/titiler/)

This vm is called `titiler` and is served at [**https://titiler.cyverse.org**](https://titiler.cyverse.org)

For this we are running a `xl` instance (16-cores, 64 GB RAM, 200 GiB Disk ) with Ubuntu 22.04 and Docker

<br/>
<br/>

### Launch using OpenStack

Log into OpenStack and provision each instance 

After the instance is active, assign a floating IP address

Make sure that the `default` Security Group includes egress and ingress settings to connect the VM over :443

<br/>

### create and add `ssh` keys

Make sure that the VMs are using your public `ssh` key

Add your other admin keys by `ssh` to the VM

copy their `id_rsa.pub` keys to `~/.ssh/known_hosts`

```
nano ~/.ssh/known_hosts
```
<br/>
<br/>

## Deployments

### Install Docker

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
<br/>

<br/>
<br/>

### :Nginx

To secure both instances over `https://` we are runninng [Nginx](https://nginx.org/) with a reverse proxy to the public IP addresses. Currently, the ssl certicates have expired and need to be updated. I have asked Jeremy Frady to do this. 

Check the expiration date of the certificate

```
openssl s_client -connect stac.cyverse.org:443 -servername stac.cyverse.org < /dev/null | openssl x509 -noout -dates
```
<br/>
<br/>

Is nginx active and running?

`sudo systemctl status nginx`

<br/>

Is nginx listening on port 80 (standard http port)?

`sudo lsof -i :80`

<br/>
<br/>

Some nginx configuration files are located in:

 `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` and `/etc/nginx/nginx.conf`

<br/>
<br/>

### Run STAC API

[:simple-github: stac-utils/stac-fastapi](https://github.com/stac-utils/stac-fastapi)

```bash
git clone https://github.com/stac-utils/stac-fastapi.git

cd stac-fastapi
```
<br/>

There are two configuration files which need to be updated:

`docker-compose.yaml` - provisions the deployment of a [PostgreSQL](https://www.postgresql.org/docs/) database and [SQL lchemy](https://www.sqlalchemy.org/) Python SQL toolkit and object relational mapper mapped to a STAC `.json` Collection and `.geojson` Feature Collection.

`/scripts/ingest_collection.py` - there is a sample `.py` ingestion file called "joplin" which you can make a copy of and edit.

There is one sample STAC catalog directory which can be removed or used for testing:

`/stac_fastapi/testdata/joplin` - is the test dataset which is deployed by default. 
<br/>

<br/>
<br/>


#### Edit `docker-compose.yml` 

The `stac-fastapi` Docker-Compose will start up multiple containers, including a database which relies on the sample data.

Note: the GitHub repository for `stac-fastapi` expects containers from GitHub Container Registry, not from DockerHub - update the `docker-compose.yml` to use the specific containers and tag version 



[:simple-github: cyverse-gis/cyverse-stac](https://github.com/cyverse-gis/cyverse-stac){target=_blank}

Clone the `cyverse-stac` repository to the home directory where you cloned `stac-fastapi`

```bash
git clone https://github.com/cyverse-gis/cyverse-stac
```

Inside the `/cyverse-stac` repo is a directory called `catalogs` - this is where we are maintaining the list of public STAC Collections in CyVerse.

The `catalogs` directory is ingested by the `ingest_cyverse.py` file in the `stac-fastapi/scripts` directory. 

The `docker-compose.yml` is also modified to include the relative path to the `cyverse-stac` directory

<br/><br/>

### Edit `ingest_cyverse.py`


<br/>
<br/>

#### Start Docker-Compose

```bash
cd ~/stac-fastapi
```

In the `/stac-fastapi` directory there is a `docker-compose.yml` which is set to point at a demo dataset called `joplin` you will need to modify the `docker-compose.yml` and point it at a new `collection.json` and `index.geojson` 

Note: if you do not modify the `docker-compose.yml` the sample dataset will be shown.

<br/>

Start Docker-Compose in detached mode. The `-d` flag will start Docker Compose in the background

```bash
docker-compose up -d 
```
<br/>


