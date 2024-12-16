.PHONY: all clean image image-clean start-fg start stop stop-clean

include ../make.vars
include environment/controller.env

CONTROLLER_MANIFEST = $(COMPOSE_DIR)/controller.yml
CONTROLLER_ENVFILE = $(ENV_DIR)/controller.env
CONTROLLER_PROJECT_NAME = drio-controller
CONTROLLER_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) --project-name $(CONTROLLER_PROJECT_NAME) --env-file $(CONTROLLER_ENVFILE) --file $(CONTROLLER_MANIFEST)

configdb-image:
	$(DOCKER_BUILD_CMD) -f $(DOCKER_DIR)/Dockerfile.configdb -t $(CONFIGDB_IMAGE):$(CONFIGDB_VERSION) .

configdb-image-clean:
	docker rmi $(CONFIGDB_IMAGE):$(CONFIGDB_VERSION)

vault-agent-image:
	$(DOCKER_BUILD_CMD) --build-arg VAULT_AGENT_LISTEN_PORT=$(VAULT_AGENT_LISTEN_PORT) --build-arg VAULT_AGENT_TLS_DISABLE=$(VAULT_AGENT_TLS_DISABLE) --build-arg VAULT_AGENT_VAULT_URL=$(VAULT_AGENT_VAULT_URL) -f $(DOCKER_DIR)/Dockerfile.vault-agent -t $(VAULT_AGENT_IMAGE):$(VAULT_AGENT_VERSION) .

vault-agent-image-clean:
	docker rmi $(VAULT_AGENT_IMAGE):$(VAULT_AGENT_VERSION)

image: configdb-image vault-agent-image

image-clean: configdb-image-clean vault-agent-image-clean

all: image start
clean: stop-clean image-clean

start-fg:
	touch $(COMPOSE_DIR)/vault-agent/role_id
	touch $(COMPOSE_DIR)/vault-agent/secret_id
	$(CONTROLLER_COMPOSE_CMD) up

start:
	touch $(COMPOSE_DIR)/vault-agent/role_id
	touch $(COMPOSE_DIR)/vault-agent/secret_id
	$(CONTROLLER_COMPOSE_CMD) up --detach

vault-agent-start:
	touch $(COMPOSE_DIR)/vault-agent/role_id
	touch $(COMPOSE_DIR)/vault-agent/secret_id
	$(CONTROLLER_COMPOSE_CMD) up vault-agent --detach

vault-agent-stop:
	$(CONTROLLER_COMPOSE_CMD) down vault-agent

configdb-start:
	$(CONTROLLER_COMPOSE_CMD) up configdb --detach

configdb-stop:
	$(CONTROLLER_COMPOSE_CMD) down configdb

api-start:
	$(CONTROLLER_COMPOSE_CMD) up apiservice --detach

api-stop:
	$(CONTROLLER_COMPOSE_CMD) down apiservice

stop:
	$(CONTROLLER_COMPOSE_CMD) down

stop-clean:
	$(CONTROLLER_COMPOSE_CMD) down -v
