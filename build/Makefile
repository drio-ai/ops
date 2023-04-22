.PHONY: all clean configdb configdb-clean redis redis-clean

ifeq ($(strip $(VER)),)
    VER = 0.1
endif

TAG = $(VER)
REPO = drioinc
DOCKER_BUILD_CMD = docker build --no-cache
CONFIGDB_IMGNAME = postgres
REDIS_IMGNAME = redis

configdb:
	$(DOCKER_BUILD_CMD) -f ./Dockerfile.configdb -t $(REPO)/$(CONFIGDB_IMGNAME):$(VER) .	

configdb-clean:
	docker rmi $(REPO)/$(CONFIGDB_IMGNAME):$(VER)

redis:
	$(DOCKER_BUILD_CMD) -f ./Dockerfile.redis -t $(REPO)/$(REDIS_IMGNAME):$(VER) .

redis-clean:
	docker rmi $(REPO)/$(REDIS_IMGNAME):$(VER)

all: configdb redis
clean: configdb-clean redis-clean
