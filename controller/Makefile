.PHONY: all clean image start-fg start stop stop-clean

include ../make.vars
include environment/controller.env

CONTROLLER_MANIFEST = $(COMPOSE_DIR)/controller.yml
CONTROLLER_ENVFILE = $(ENV_DIR)/controller.env
CONTROLLER_PROJECT_NAME = drio-controller
CONTROLLER_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(CONTROLLER_PROJECT_NAME) --env-file $(CONTROLLER_ENVFILE) --file $(CONTROLLER_MANIFEST)

image:
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile.configdb -t $(CONFIGDB_IMAGE):$(CONFIGDB_VERSION) .
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile.redis -t $(REDIS_IMAGE):$(REDIS_VERSION) .

clean:
	docker rmi $(CONFIGDB_IMAGE):$(CONFIGDB_VERSION)
	docker rmi $(REDIS_IMAGE):$(REDIS_VERSION)

all: image

start-fg:
	$(CONTROLLER_COMPOSE_CMD) up

start:
	$(CONTROLLER_COMPOSE_CMD) up --detach

stop:
	$(CONTROLLER_COMPOSE_CMD) down

stop-clean:
	$(CONTROLLER_COMPOSE_CMD) down -v
