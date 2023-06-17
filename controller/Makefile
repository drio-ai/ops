.PHONY: all clean image image-clean start-fg start stop stop-clean

include ../make.vars
include environment/controller.env

CONTROLLER_MANIFEST = $(COMPOSE_DIR)/controller.yml
CONTROLLER_ENVFILE = $(ENV_DIR)/controller.env
CONTROLLER_PROJECT_NAME = drio-controller
CONTROLLER_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(CONTROLLER_PROJECT_NAME) --env-file $(CONTROLLER_ENVFILE) --file $(CONTROLLER_MANIFEST)

image:
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile.configdb -t $(CONFIGDB_IMAGE):$(CONFIGDB_VERSION) .

image-clean:
	docker rmi $(CONFIGDB_IMAGE):$(CONFIGDB_VERSION)

all: image start
clean: stop-clean image-clean

start-fg:
	$(CONTROLLER_COMPOSE_CMD) up

start:
	$(CONTROLLER_COMPOSE_CMD) up --detach

stop:
	$(CONTROLLER_COMPOSE_CMD) down

stop-clean:
	$(CONTROLLER_COMPOSE_CMD) down -v
