#!/bin/sh

function stop_service() {
    cwd=$(pwd)
    service_name=$1
    description=$2

    echo "Stopping ${description}"
    cd ${service_name}
    make stop-clean
    echo "Stopped ${description}"
    cd ${cwd}
    sleep 2
}

stop_service controller "Configuration Database and API Service"
stop_service pubsub "PubSub"
stop_service cache "Cache"
stop_service vault "Vault"
