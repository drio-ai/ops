.PHONY: all clean image image-clean start-fg start stop stop-clean

include ../make.vars
include environment/pubsub.env

PUBSUB_MANIFEST = $(COMPOSE_DIR)/pubsub.yml
PUBSUB_ENVFILE = $(ENV_DIR)/pubsub.env
PUBSUB_PROJECT_NAME = drio-pubsub
PUBSUB_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(PUBSUB_PROJECT_NAME) --env-file $(PUBSUB_ENVFILE) --file $(PUBSUB_MANIFEST)

image:
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile -t $(PUBSUB_IMAGE):$(PUBSUB_VERSION) .

image-clean:
	docker rmi $(PUBSUB_IMAGE):$(PUBSUB_VERSION)

all: image start

start-fg:
	$(PUBSUB_COMPOSE_CMD) up

start:
	$(PUBSUB_COMPOSE_CMD) up --detach

stop:
	$(PUBSUB_COMPOSE_CMD) down

stop-clean:
	$(PUBSUB_COMPOSE_CMD) down -v

clean: stop-clean image-clean
