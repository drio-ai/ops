.PHONY: ctrl-build ctrl-build-clean ctrl-start ctrl-start-fg ctrl-stop ctrl-stop-clean vault-start vault-start-fg vault-stop vault-stop-clean all clean

CTRL_MANIFEST = "./controller.yml"
CTRL_ENVFILE = "./controller.env"
CTRL_COMPOSE_CMD = docker compose --env-file $(CTRL_ENVFILE) --file $(CTRL_MANIFEST)

ctrl-build:
	$(MAKE) -C build all

ctrl-build-clean:
	$(MAKE) -C build clean

ctrl-start:
	$(CTRL_COMPOSE_CMD) up --detach

ctrl-start-fg:
	$(CTRL_COMPOSE_CMD) up

ctrl-stop:
	$(CTRL_COMPOSE_CMD) down

ctrl-stop-clean:
	$(CTRL_COMPOSE_CMD) down -v

VAULT_MANIFEST = "./vault.yml"
VAULT_ENVFILE  = "./vault.env"
VAULT_COMPOSE_CMD = docker compose --env-file $(VAULT_ENVFILE) --file $(VAULT_MANIFEST)

vault-start:
	$(VAULT_COMPOSE_CMD) up --detach

vault-start-fg:
	$(VAULT_COMPOSE_CMD) up

vault-stop:
	$(VAULT_COMPOSE_CMD) down
	
vault-stop-clean:
	$(VAULT_COMPOSE_CMD) down -v
	rm -rf vault/data/*
	rm -rf vault/logs/*
	

all: ctrl-build ctrl-start
clean: ctrl-stop-clean ctrl-build-clean
