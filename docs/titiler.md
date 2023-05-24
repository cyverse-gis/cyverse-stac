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

### Start CaddyServer

Start a fresh `tmux` session 

Star the Caddy Server with a reverse proxy, pointing at the same port as Docker

```bash
caddy reverse-proxy --from titler.cyverse.org --to localhost:8000 --change-host-header &
```

Detach the session