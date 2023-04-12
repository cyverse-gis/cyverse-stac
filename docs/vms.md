# OpenStack Virtual Machines

We are currently running two instances on CyVerse OpenStack Cloud 

[https://tombstone-cloud.cyverse.org/](https://tombstone-cloud.cyverse.org/){target=_blank}

One instance is running a Radiant Earth `stac-fastapi` [STAC API](https://stac-utils.github.io/stac-fastapi/){target=_blank} 

[**https://stac.cyverse.org**](https://stac.cyverse.org){target=_blank}

It is a `small` instance (2 virtual CPUs, 16 GB RAM) with Ubuntu 22.04, Docker, and Docker-Compose.

The other instance is running [DevSeed TiTiler](https://developmentseed.org/titiler/){target=_blank} 

[**https://titiler.cyverse.org**](https://titiler.cyverse.org){target=_blank} 

For this we are running a `xl` instance (16-cores, 64 GB RAM, 200 GiB Disk ) with Ubuntu 22.04 and Docker

## Launch using OpenStack

Log into OpenStack and provision each instance 

After the instance is active, assign a floating IP address

Make sure that the `default` Security Group includes egress and ingress settings to connect the VM over :443

## create and add `ssh` keys

Make sure that the VMs are using your public `ssh` key

Add your other admin keys by `ssh` to the VM

copy their `id_rsa.pub` keys to `~/.ssh/known_hosts`

```
nano ~/.ssh/known_hosts
```