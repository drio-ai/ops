# How to start controller
1. [Controller components](#controller-components)
1. [Controller docker images](#controller-docker-images)
1. [Controller Start](#controller-start)
1. [UI Start](#ui-start)
1. [UI Stop](#ui-stop)
1. [Controller Stop](#controller-stop)
1. [Service Group Directory structure](#service-group-directory-structure)

# Controller Components
As of writing this document, these are the components that make up the Drio Controller
1. Hashicorp Vault (Vault service group)
1. Redis Cache (Cache service group)
1. Apache Kafka (Pubsub service group)
1. Postgres Database (Controller service group)
1. API Service (Controller service group)

These components further decompose to 3 different service groups with each of these service groups started separately. The Vault and Cache service groups at this point only have the 1 service in them. This will not be the way it will always be. The order in which these service groups are started
1. Vault service group
1. Cache service group
1. Pubsub service group
1. Controller service group

# Controller Docker Images
Controller will be distributed as docker images and published to drioinc repository in docker hub. Respective service images can be downloaded as
```
docker pull drioinc/vault:<tag>
docker pull drioinc/redis:<tag>
docker pull drioinc/pubsub:<tag>
docker pull drioinc/postgres:<tag>
docker pull drioinc/apiservice:<tag>
```
The current tag we are working with is ```1.0```. This will change as we go further down the development process.
It is highly unlikely you will have to pull these images manually. As you work through the Controller startup steps, these images will be downloaded for you.
## Service Versions
Except apiservice, the other 3 services that make up Drio Controller are built from well known services. Our docker image only has a few init scripts, configuration files and policy documents added on to it. For reference, these are the versions of these well known services our docker image is built from
1. Hashicorp Vault - 1.13
1. Redis Cache - 7.0.11
1. Apache Kafka - 3.7.1
1. Postgres - 15.2

# Controller Start
It is recommended to attempt starting Drio-Controller Ubuntu server. There is nothing specific to this flavour but this is the one that has been tested. Once you have the VM or instance ready, 

1. Install docker. Follow steps [here](https://docs.docker.com/engine/install/ubuntu/) Use the ‘Install using the apt repository’ option
1. Add your user to docker group if you are not the root user. ```sudo usermod -aG docker $USER```
1. NOTE: You might have to log out and back in again for the change from the previous step to take effect. ```docker images``` should run successfully.
1. Install make by running ```sudo apt install make```
1. Clone this repository. ```git clone https://github.com/drio-ai/ops.git``` and ```cd ops```
1. NOTE: The scripts you will be running expect **bash** shell to be installed.
1. Run ```./setup.sh```
1. Run ```./start.sh```
1. The start script executed in the previous step will start all components in the right order. Every service group is started using docker compose and that means any docker image not available locally will be downloaded from docker hub.
1. Run ```./vault/scripts/get-saas-admin-pass.sh``` to get the SaaS Admin login password. The SaaS Admin username is *saas-admin@drio.ai*.

Drio Controller can be accessed at 127.0.0.1:8080 from the Host it is being run on

# UI Start
1. NOTE: UI Server consumes a fair amount of CPU cycles and memory during initialization phase. Start the UI Server only if neccessary.
1. ```cd ui``` in the ops repository
1. Run ```make start``` to start uiserver
1. UI Server will take a little while to complete initialization. You can run ```docker logs --follow uiserver``` to follow progress
1. Initialization is complete when you see the log line 'Accepting connections at http://localhost:3001' and a similar log for :3000
1. Point your browser to http://localhost:3000 to access SaaS Admin portal
1. Point your browser to http://localhost:3001 to access Root Admin portal

# UI Stop
1. ```cd ui``` in the ops repository
1. Run ```make stop-clean``` to stop uiserver

# Controller Stop
1. Run ```./stop.sh``` inside ops directory to stop the controller.
1. If you wish to only stop *Controller service group* components for e.g., ```cd controller``` and run ```make stop-clean```. A ```make start``` in the same directory will start the *Controller service group* components.

# Service Group Directory structure
All service groups in the ops repository will have these 3 directories in it

1. compose - The docker compose file that is used to start and stop components in the service group
1. environment - Environment that controls how the components of the service group are started
1. docker - Dockerfile(s) that is/are used to build images of components in the service group

Along with the directories listed above, there is also a Makefile that defines the commands to start and stop components.
