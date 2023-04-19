#!/bin/bash

MANIFEST=./docker-compose.yml

function ctrl-start() {
    docker compose -f ${MANIFEST} up --detach
}

function ctrl-start-fg() {
    docker compose -f ${MANIFEST} up
}

function ctrl-stop() {
    docker compose -f ${MANIFEST} down
}
