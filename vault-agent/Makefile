.PHONY: all clean image image-clean start-fg start stop stop-clean

include ../make.vars
include environment/vault-agent.env

VAULT_AGENT_MANIFEST = $(COMPOSE_DIR)/vault-agent.yml
VAULT_AGENT_ENVFILE = $(ENV_DIR)/vault-agent.env
VAULT_AGENT_PROJECT_NAME = drio-vault-agent
VAULT_AGENT_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(VAULT_AGENT_PROJECT_NAME) --env-file $(VAULT_AGENT_ENVFILE) --file $(VAULT_AGENT_MANIFEST)

image:
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile -t $(VAULT_AGENT_IMAGE):$(VAULT_AGENT_VERSION) .

image-clean:
	docker rmi $(VAULT_AGENT_IMAGE):$(VAULT_AGENT_VERSION)

all: image start

start-fg:
	touch $(COMPOSE_DIR)/role_id
	touch $(COMPOSE_DIR)/secret_id
	$(VAULT_AGENT_COMPOSE_CMD) up

start:
	touch $(COMPOSE_DIR)/role_id
	touch $(COMPOSE_DIR)/secret_id
	$(VAULT_AGENT_COMPOSE_CMD) up --detach

stop:
	$(VAULT_AGENT_COMPOSE_CMD) down

stop-clean:
	$(VAULT_AGENT_COMPOSE_CMD) down -v
	rm -rf $(COMPOSE_DIR)/secret_id
	rm -rf $(COMPOSE_DIR)/role_id

clean: stop-clean image-clean
