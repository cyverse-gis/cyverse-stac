# CyVerse SpatioTemporal Asset Catalog (STAC) 

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

[Browse Cyverse STAC Catalog](https://radiantearth.github.io/stac-browser/#/external/stac.cyverse.org/?.language=en)

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

### Launch VMs in OpenStack

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



### Install Docker on VM

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

## Nginx

To secure both instances over `https://` we are runninng [Nginx](https://nginx.org/) with a reverse proxy to the public IP addresses. Nginx is installed on the vm (not containerized). A reverse proxy acts as gatekeeper or middleman to handle web requests. A request will come into to port 80 (default http port) or 443 (encrypted port). Nginx listens to these ports for requests and then sends the request on to a back-end server to meet the request. For this system, Nginx is set to send request to localhost:8081 where a containerized Sql Alchemy is waiting to receive. 

Secure Sockets Layer (SSL) Certificate is a file that encrypts data transfer between a browser and a server. stac.cyverse.org has SSL certificates from GoDaddy (managed by Jeremy Frady). An SSL certificate makes your http site secure as https.



#### Useful Info

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

Within directory `stac-fastapi`, there are files `docker-compose.nginx.yml` and `nginx.conf`. This files are NOT in use. 


<br/>
<br/>
<br/>
<br/>
<br/>
<br/>

## `stac-api` vm

The general directory structure on `stac-api` vm is:

```
-ubuntu
  -cyverse-stac
  -stac-fastapi 
```

`cyverse-stac` is the cloned version of [THIS repository](https://github.com/cyverse-gis/cyverse-stac) It contains the json & geojson metadata the descibes the geospatial collections, items, and assets. The repo on Github and the VM should be synced at all time. 

<br/>

`stac-fastapi` is a [repo](https://github.com/stac-utils/stac-fastapi) that contains the files needed to run the API. This version is from 2023 and quite a bit behind the latest development. 

<br/>
<br/>


## stac-fastapi with Docker-compose

Within the directory `stac-fastapi`, the file `docker-compose.yml` is the config file to orchestrate the launching of multiple containers. These containers run the API. 

Note: the GitHub repository for `stac-fastapi` expects containers from GitHub Container Registry, not from DockerHub - update the `docker-compose.yml` to use the specific containers and tag version 


<br/>
<br/>

### docker-compose.yml

Docker-compose.yml launches a series of containerized services.


Container name: **`stac-db`**. This container provides a PostgreSQL database with the PGStac extension. Purpose: Stores the spatiotemporal data for both app-sqlalchemy and app-pgstac.
Key Features: Preconfigured for geospatial data processing (using postgis and PGStac). Exposes the database on port 5439 (mapped to the host's port).

Container name: **`stac-fastapi-sqlalchemy`**. This container runs the stac-fastapi (rest api) and uses [SQL Alchemy](https://www.sqlalchemy.org/), a Python SQL toolkit and object relational mapper mapped to a STAC `.json` Collection and `.geojson` Feature Collection.  This container waits for the postgresql database to start before launching. It uses a `wait-for-it.sh` script to wait for the postgresql database at port 5432. It exposes to port 8081 where is receives requests from nginx reverse proxy.

Container name: **`stac-fastapi-pgstac`**. This container is similar to the 'sql alchecmy' container. It currently does not launch (exit code 127 which means there is problem with `COMMAND`) and is not set up to communcate with the nginx reverse proxy. Perhaps it is redundant or not useful for our purposes????

Container name: **`loadcyverse-sqlalchemy`**. This container's whole purpose to load STAC metadata (`collection.json` & `index.geojson`) into the postgresql database. It runs the `ingest_cyverse.py` script to put the data into the database. The `ingest_cyverse.py` script uses the file `api_collections.txt` as part of the ingest. If successful, the container should run for a short period of time and then exit with code 0. 

Container name: **`loadcyverse-pgstac`**: For loading data using the fastapi-pgstac service. This currently does not work. 

<br/>
<br/>

### Start Docker-Compose

```bash
cd ~/stac-fastapi
```
Start the API

`docker-compose up -d`

Stop the API

`docker-compose down`






<br/>
<br/>
<br/>
<br/>
<br/>


### Editing the API title and description
`/home/ubuntu/stac-fastapi/stac_fastapi/api/stac_fastapi/api/app.py`




<br/>
<br/>
<br/>
<br/>


### Adding or Editing Catalogs

Adding or editing STAC catalogs (json & geojson files) is generally best to do directly in this github repo. 


To add new collections to the API, you would add a new directory under `/catalogs`. Within this new directory you would add a
`collection.json` file and `index.geojson` file that were created by the `STAC_creation_latest.ipynb`. 

Additionally, you will need to edit `api_collections.txt` file found at `/cyverse-stac` within the repo. Add a single line the mimics the previous lines, but has the name of the directory you created in `/catalogs` 


<br/>

Changes that you make to the github repo will be pulled into the vm automatically. This is accomplished by using a cronjob on the vm. There is shell script called `update_and_restart.sh` in the repo that specifies: 1. Look for differences between github repo and repo on vm. 2. If there are differences, then pull the changes from github. 3. Restart the docker-compose that creates the STAC API. On the vm, the shell script has been programmed to run every 5 minutes using the crontab. The cronjob is logged to the file `/home/ubuntu/cyverse-stac/cron_log_file.log`. 

While logged into the `stac-api` vm:
```
# To edit the crontab
crontab -e

#The command to run the shell script every 5 minutes and output results to log file
*/5 * * * * /home/ubuntu/stac-fastapi/update_and_restart.sh 
```
<br/><br/>

If the cronjob is not working, then you can log into the `stac-api` vm and do things manually
```
cd /home/ubuntu/cyverse-stac
git pull
```
<br/>

```
cd /home/ubuntu/stac-fastapi/
docker-compose restart
```

<br/>

If the restart doesn't work, then you can try to stop and start the docker-compose
``` 
cd /home/ubuntu/stac-fastapi/
docker-compose down
docker-compose up -d
```

<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>

## Creating STAC json & geojson files

Within this repo there is a directory called `scripts`. Within it is a jupyter notebook `STAC_creation_latest.ipynb` that has python code for creating STAC json and geojson files from crawling over imagery assets. The code primarily uses the [pystac](https://pystac.readthedocs.io/en/stable/) library to create the STAC metadata. The STAC creation code is in active development.

### Here is what the code currently does:

* Users manually input metadata about the geospatial imagery products. These include: Title of the collection, description of collection and items, provider name and info.

* Users can specify the collection date with a single entry or they can provide a csv file that lists each of the assets and their date of collection. 

* The script crawls over a user defined directory (e.g., in Cyverse DataStore) and looks for geotiff and cloud optimized geotiff (COG) files. 

* It pulls out the projection, ground sampling distance (gsd) and footprint of the imagery asset. If an asset does not have a projection, the gsd will return 0.00 meters. 

* It will assign multiple assets to a single item. This is also based on a user provided csv file that lists which assets should belong to which item. 

* It can output a static STAC with the structure catalog>>collection>>items. These will have relative links. A static catalog can be browsed by the STAC browser but it has limited ability to be queried. 

* It can output a dynamic STAC that can be ingesting into a STAC API. The structure is: collection>>index.geojson. It has absolute links. The STAC API is a lot more powerful compared with the static catalog. STAC APIs can be queried by space or time within the STAC Browser. 


### Additional Functionality that is Needed

* Find point clouds in a directory (laz, copc) and index them in STAC. There is a 'pointcloud' extension in pystac that should make it possible. 

* Link out to [COPC Viewer](https://viewer.copc.io/){target=_blank} for point cloud visualization






### STAC Assets in Cyverse Datastore

CyVerse features a set of public datasets that are curated in the CyVerse DataStore. The assets are primarily available from the DataStore over the public WebDAV.

https://data.cyverse.org/dav-anon/

All assets must be shared as `read-only` with the `anonymous` user in the iRODS environment (accessed via the Discovery Environment, Share Data feature) in order for them to be visible and downloadable.

<br/>
<br/>
<br/>
<br/>
<br/>

## TiTiler

We are running [DevSeed TiTiler](https://developmentseed.org/titiler/){target=_blank} on the Cyverse OpenStack Cloud


[**https://titiler.cyverse.org**](https://titiler.cyverse.org){target=_blank} 

For this we are running a `xl` instance (16-cores, 64 GB RAM, 200 GiB Disk ) with Ubuntu 22.04 and Docker

## Instructions for :simple-docker: DevSeed TiTiler

[TiTiler Documentation](https://developmentseed.org/titiler/)

https://titiler.cyverse.org/

### Start Docker

We are running TiTiler with Docker:

```bash
docker run \
--name titiler \
--env FORWARDED_ALLOW_IPS=*
--env REDIRECT_URL=https://titiler.cyverse.org \
-p 8000:8000 \
--env PORT=8000 \
--env WORKERS_PER_CORE=1 \
--restart always \
-d  \
-it \
ghcr.io/developmentseed/titiler:latest
```

To ensure that the container is always alive and is healthy, we are running a `cron` job every 5 minutes to test it and restart it as necessary 

```bash
*/5 * * * * docker ps -f health=unhealthy --format "docker restart {{.ID}}" | sh
```

### NGINX

Install `nginx`

```
sudo apt install apache2-utils nginx
```

??? Quote "modify `/etc/nginx/sites-enabled/default`"
    
    ```{bash}
    # Default server configuration
    #
    server {
            listen 80 default_server;
            listen [::]:80 default_server;
    
            # SSL configuration
            #
            listen 443 ssl default_server;
            listen [::]:443 ssl default_server;
    
    
            ssl_certificate /etc/ssl/certs/cyverse.org.fullchain.crt;
            ssl_certificate_key /etc/ssl/private/cyverse.org.key;
            #
            # Note: You should disable gzip for SSL traffic.
            # See: https://bugs.debian.org/773332
            #
            # Read up on ssl_ciphers to ensure a secure configuration.
            # See: https://bugs.debian.org/765782
            #
            # Self signed certs generated by the ssl-cert package
            # Don't use them in a production server!
            #
            # include snippets/snakeoil.conf;
    
            root /var/www/html;
    
            # Add index.php to the list if you are using PHP
            index index.html index.htm index.nginx-debian.html;
    
            server_name _;
    
            location / {
                    proxy_pass http://localhost:8000;
                    proxy_set_header Host $http_host;
                    proxy_set_header X-Forwarded-Proto $scheme;
    
                    # First attempt to serve request as file, then
                    # as directory, then fall back to displaying a 404.
                    # try_files $uri $uri/ =404;
            }
    
            # pass PHP scripts to FastCGI server
            #
            #location ~ \.php$ {
            #       include snippets/fastcgi-php.conf;
            #
            #       # With php-fpm (or other unix sockets):
            #       fastcgi_pass unix:/run/php/php7.4-fpm.sock;
            #       # With php-cgi (or other tcp sockets):
            #       fastcgi_pass 127.0.0.1:9000;
            #}
    
            # deny access to .htaccess files, if Apache's document root
            # concurs with nginx's one
            #
            #location ~ /\.ht {
            #       deny all;
            #}
    }
    ```

??? Quote "Add Certs"

    Add `.key` and `.crt` to:
    
    ```{bash}
    $ /etc/ssl/private/
    $ /etc/ssl/certs/
    ```

Start a new `tmux` session.

Check and Restart `nginx`

```{bash}
sudo systemctl status nginx
sudo systemctl restart nginx
```



