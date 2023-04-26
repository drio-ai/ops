.PHONY: all clean configdb configdb-clean redis redis-clean vault vault-clean

DOCKER_BUILD_CMD = docker build --no-cache

ifeq ($(MAKECMDGOALS),all)
include ../controller.env
include ../vault.env
endif
ifeq ($(MAKECMDGOALS),clean)
include ../controller.env
include ../vault.env
endif

configdb:
	$(DOCKER_BUILD_CMD) -f ./Dockerfile.configdb -t $(CONFIGDB_IMAGE):$(CONFIGDB_VERSION) .

configdb-clean:
	docker rmi $(CONFIGDB_IMAGE):$(CONFIGDB_VERSION)

redis:
	$(DOCKER_BUILD_CMD) -f ./Dockerfile.redis -t $(REDIS_IMAGE):$(REDIS_VERSION) .

redis-clean:
	docker rmi $(REDIS_IMAGE):$(REDIS_VERSION)

vault:
	$(DOCKER_BUILD_CMD) -f ./Dockerfile.vault -t $(VAULT_IMAGE):$(VAULT_VERSION) .

vault-clean:
	docker rmi $(VAULT_IMAGE):$(VAULT_VERSION)

all: configdb redis vault
clean: configdb-clean redis-clean vault-clean
