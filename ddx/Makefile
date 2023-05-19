.PHONY: all clean image image-clean start-fg start stop stop-clean

include ../make.vars
include environment/ddx.env

DDX_MANIFEST = $(COMPOSE_DIR)/ddx.yml
DDX_ENVFILE = $(ENV_DIR)/ddx.env
DDX_PROJECT_NAME = drio-ddx
DDX_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(DDX_PROJECT_NAME) --env-file $(DDX_ENVFILE) --file $(DDX_MANIFEST)

image:
        $(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile -t $(DDX_IMAGE):$(DDX_VERSION) .

image-clean:
        docker rmi $(DDX_IMAGE):$(DDX_VERSION)

all: image start

start-fg:
        $(DDX_COMPOSE_CMD) up

start:
        $(DDX_COMPOSE_CMD) up --detach

stop:
        $(DDX_COMPOSE_CMD) down

stop-clean:
        $(DDX_COMPOSE_CMD) down -v
        rm -rf $(COMPOSE_DIR)/data/*
        rm -rf $(COMPOSE_DIR)/logs/*

clean: stop-clean image-clean
