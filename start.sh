#!/bin/sh

function start_service() {
    cwd=$(pwd)
    service_name=$1
    inspect_name=$2
    inspect_status=$3
    description=$4

    echo "Starting ${description}"
    cd ${service_name}
    make start
    status=$(docker inspect -f {{.State.Status}} ${inspect_name})
    until [ ${status} == ${inspect_status} ]; do
        sleep 1
        status=$(docker inspect -f {{.State.Status}} ${inspect_name})
    done
    echo "Started ${description}"
    cd ${cwd}
}

start_service vault vault-init exited Vault
start_service cache cache-init exited Cache
start_service pubsub pubsub running PubSub
start_service controller apiservice-init exited "Configuration Database and API Service"

apiservice_health_status=$(docker inspect -f {{.State.Health.Status}} apiservice)
until [ ${apiservice_health_status} == "healthy" ]; do
    sleep 1
    apiservice_health_status=$(docker inspect -f {{.State.Health.Status}} apiservice)
done
echo "Controller is ready"
