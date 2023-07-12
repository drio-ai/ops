# How to start controller
1. [Controller components](#controller-components)
2. [Controller docker images](#controller-docker-images)
3. [Setup](#setup)
4. [Controller startup](#controller-startup)

# Controller Components
As of writing this document, these are the components that make up the Drio Controller
1. Hashicorp Vault (Vault service group)
2. Redis Cache (Cache service group)
3. Postgres Database (Controller service group)
4. API Service (Controller service group)

These components further decompose to 3 different service groups with each of these service groups started separately. The Vault and Cache service groups at this point only have the 1 service in them. This will not be the way it will always be. The order in which these service groups are started
1. Vault service group
2. Cache service group
3. Controller service group

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
2. Redis Cache - 7.0.11
3. Postgres - 15.2

# Setup
It is recommended to attempt starting Drio-Controller Ubuntu server. There is nothing specific to this flavour but this is the one that has been tested. Once you have the VM or instance ready, 

1. Install docker. Follow steps [here](https://docs.docker.com/engine/install/ubuntu/) Use the ‘Install using the apt repository’ option
2. Clone this repository. ```git clone https://github.com/drio-inc/ops.git``` and ```cd ops```
3. Run ```setup.sh```
4. ```cd vault``` and run ```make start```
  1. This will start two docker containers, vault and vault-init
  2. vault is the long running container. vault-init will perform init actions and exit
  3. Run ```docker logs vault-init``` to make sure it completed successfully   
