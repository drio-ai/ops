.PHONY: all clean image image-clean start-fg start stop stop-clean

include ../make.vars
include environment/ui.env

UI_MANIFEST = $(COMPOSE_DIR)/ui.yml
UI_ENVFILE = $(ENV_DIR)/ui.env
UI_PROJECT_NAME = drio-ui
UI_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(UI_PROJECT_NAME) --env-file $(UI_ENVFILE) --file $(UI_MANIFEST)

all: start
clean: stop-clean

start-fg:
	$(UI_COMPOSE_CMD) up

start:
	$(UI_COMPOSE_CMD) up --detach

stop:
	$(UI_COMPOSE_CMD) down

stop-clean:
	$(UI_COMPOSE_CMD) down -v
