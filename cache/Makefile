.PHONY: all clean image image-clean start-fg start stop stop-clean

include ../make.vars
include environment/cache.env

CACHE_MANIFEST = $(COMPOSE_DIR)/cache.yml
CACHE_ENVFILE = $(ENV_DIR)/cache.env
CACHE_PROJECT_NAME = drio-cache
CACHE_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(CACHE_PROJECT_NAME) --env-file $(CACHE_ENVFILE) --file $(CACHE_MANIFEST)

image:
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile -t $(CACHE_IMAGE):$(CACHE_VERSION) .

image-clean:
	docker rmi $(CACHE_IMAGE):$(CACHE_VERSION)

all: image start

start-fg:
	$(CACHE_COMPOSE_CMD) up

start:
	$(CACHE_COMPOSE_CMD) up --detach

stop:
	$(CACHE_COMPOSE_CMD) down

stop-clean:
	$(CACHE_COMPOSE_CMD) down -v
	rm -rf $(COMPOSE_DIR)/data/*
	rm -rf $(COMPOSE_DIR)/logs/*
	rm -rf $(COMPOSE_DIR)/tokens/drio-controller/*
	rm -rf $(COMPOSE_DIR)/tokens/root/*

clean: stop-clean image-clean
