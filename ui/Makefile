.PHONY: all clean image image-clean start-fg start stop stop-clean

include ../make.vars
include environment/ui.env

UI_MANIFEST = $(COMPOSE_DIR)/ui.yml
UI_ENVFILE = $(ENV_DIR)/ui.env
UI_PROJECT_NAME = drio-ui
UI_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(UI_PROJECT_NAME) --env-file $(UI_ENVFILE) --file $(UI_MANIFEST)

image:
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile -t $(UI_IMAGE):$(UI_VERSION) .

image-clean:
	docker rmi $(UI_IMAGE):$(UI_VERSION)

all: image start
clean: stop-clean image-clean

start-fg:
	$(UI_COMPOSE_CMD) up

start:
	$(UI_COMPOSE_CMD) up --detach

noapi-start:
	$(UI_COMPOSE_CMD) up configdb --detach

stop:
	$(UI_COMPOSE_CMD) down

stop-clean:
	$(UI_COMPOSE_CMD) down -v
