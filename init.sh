#!/bin/bash

MANIFEST="./controller.yml"
ENVFILE="./controller.env"

function ctrl-start() {
    docker compose --env-file ${ENVFILE} --file ${MANIFEST} up --detach
}

function ctrl-start-fg() {
    docker compose --env-file ${ENVFILE} --file ${MANIFEST} up
}

function ctrl-stop() {
    docker compose --env-file ${ENVFILE} --file ${MANIFEST} down
}

function ctrl-stop-clean() {
    docker compose --env-file ${ENVFILE} --file ${MANIFEST} down -v
}
