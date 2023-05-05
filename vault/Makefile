.PHONY: all clean image start-fg start stop stop-clean

include ../make.vars
include environment/vault.env

VAULT_MANIFEST = $(COMPOSE_DIR)/vault.yml
VAULT_ENVFILE = $(ENV_DIR)/vault.env
VAULT_PROJECT_NAME = drio-vault
VAULT_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(VAULT_PROJECT_NAME) --env-file $(VAULT_ENVFILE) --file $(VAULT_MANIFEST)

image:
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile -t $(VAULT_IMAGE):$(VAULT_VERSION) .

clean:
	docker rmi $(VAULT_IMAGE):$(VAULT_VERSION)

all: image

start-fg:
	$(VAULT_COMPOSE_CMD) up

start:
	$(VAULT_COMPOSE_CMD) up --detach

stop:
	$(VAULT_COMPOSE_CMD) down

stop-clean:
	$(VAULT_COMPOSE_CMD) down -v
	rm -rf $(COMPOSE_DIR)/data/*
	rm -rf $(COMPOSE_DIR)/logs/*
	rm -rf $(COMPOSE_DIR)/tokens/drio-controller/*
	rm -rf $(COMPOSE_DIR)/tokens/root/*
