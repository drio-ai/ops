.PHONY: build build-clean start start-fg stop stop-clean all clean

MANIFEST = "./controller.yml"
ENVFILE = "./controller.env"
COMPOSE_CMD = docker compose --env-file $(ENVFILE) --file $(MANIFEST)

build:
	$(MAKE) -C build all

build-clean:
	$(MAKE) -C build clean

start:
	$(COMPOSE_CMD) up --detach

start-fg:
	$(COMPOSE_CMD) up

stop:
	$(COMPOSE_CMD) down

stop-clean:
	$(COMPOSE_CMD) down -v

all: build start
clean: stop-clean build-clean
