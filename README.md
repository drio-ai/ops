# How to start controller
1. [Controller components](#controller-components)
1. [Controller docker images](#controller-docker-images)
1. [Setup](#setup)
1. [Controller startup](#controller-startup)

# Controller Components
As of writing this document, these are the components that make up the Drio Controller
1. Hashicorp Vault (Vault service group)
1. Redis Cache (Cache service group)
1. Postgres Database (Controller service group)
1. API Service (Controller service group)

These components further decompose to 3 different service groups with each of these service groups started separately. The Vault and Cache service groups at this point only have the 1 service in them. This will not be the way it will always be. The order in which these service groups are started
1. Vault service group
1. Cache service group
1. Controller service group

# Controller Docker Images
Controller will be distributed as docker images and published to drioinc repository in docker hub. Respective service images can be downloaded as
```
docker pull drioinc/vault:<tag>
docker pull drioinc/redis:<tag>
docker pull drioinc/postgres:<tag>
docker pull drioinc/apiservice:<tag>
```
The current tag we are working with is ```1.0```. This will change as we go further down the development process.
It is highly unlikely you will have to pull these images manually. As you work through the Controller startup steps, these images will be downloaded for you.
## Service Versions
Except apiservice, the other 3 services that make up Drio Controller are built from well known services. Our docker image only has a few init scripts, configuration files and policy documents added on to it. For reference, these are the versions of these well known services our docker image is built from
1. Hashicorp Vault - 1.13
1. Redis Cache - 7.0.11
1. Postgres - 15.2

# Setup
It is recommended to attempt starting Drio-Controller Ubuntu server. There is nothing specific to this flavour but this is the one that has been tested. Once you have the VM or instance ready, 

1. Install docker. Follow steps [here](https://docs.docker.com/engine/install/ubuntu/) Use the ‘Install using the apt repository’ option
1. Add your user to docker group if you are not the root user. ```sudo usermod -aG docker $USER```
1. Install make by running ```sudo apt install make```
1. Clone this repository. ```git clone https://github.com/drio-inc/ops.git``` and ```cd ops```
1. Run ```setup.sh```
1. ```cd vault``` and run ```make start```
    1. Creates vaultnet docker network 
    1. Starts two docker containers, vault and vault-init
    1. vault is the long running container. vault-init will perform init actions and exit
    1. Note: vault-init sleeps for 10 seconds to make sure vault is up and running before doing anything
    1. Run ```docker logs vault-init``` to make sure it completed successfully   
    1. If all is well, vault has been successfully setup with all the secrets Drio Controller needs
1. ```cd ../cache``` and run ```make start```
    1. Creates intnet docker network
    1. Starts two docker containers, cache and cache-init
    1. cache is the long running container, cache-init read cache password from vault to update cache
    1. Note: cache-init sleeps for 10 seconds to make sure cache is up and running before doing anything
    1. Run ```docker logs cache-init``` to make sure it completed successfully
    1. If all is well, cache has been successfully setup
1. ```cd ../controller``` and run ```make start```
    1. Creates extnet docker network. You will not see this network listed in a development setup and that is ok.
    1. Starts three docker containers, configdb, apiservice-init and apiservice
    1. configdb and apiservice are the long running containers. apiservice-init will perform init actions and exit
    1. Note: apiservice-init sleeps for 10 seconds to make sure apiservice is up and running before doing anything
    1. Run ```docker logs apiservice-init``` to make sure it completed successfully
    1. If all is well, Drio Controller is up and running

Drio Controller can be accessed at 127.0.0.1:8080 from the Host it is being run on

To stop the controller, go through the directories in reverse order (controller, cache and then vault) and run ```make stop-clean``` in all of them.
