#!/usr/bin/env sh

exec /__cacert_entrypoint.sh "$@"

if [ -z ${VAULT_ADDR} ]; then
    echo "Did not find VAULT_ADDR in environment"
    exit 1
fi

if [ ! -z ${DRIO_VAULT_ROLE_ID} ] && [ ! -z ${DRIO_VAULT_SECRET_ID} ]; then
    echo "Vault login attempt..."
    vault_client_token_resp=$(curl --request POST --data "{\"role_id\": \"${DRIO_VAULT_ROLE_ID}\", \"secret_id\": \"${DRIO_VAULT_SECRET_ID}\"}" ${VAULT_ADDR}/v1/auth/approle/login)
    vault_client_token=$(echo ${vault_client_token_resp} | jq -r ".auth.client_token")

    if [ -z ${vault_client_token} ]; then
        echo "Vault login failed. Exiting"
        exit 1
    fi

    echo "Vault login was successful. Fetching pubsub password from vault..."
    vault_pubsub_password_resp=$(curl --header "X-Vault-Token: ${vault_client_token}" ${VAULT_ADDR}/v1/drio-controller/ops/data/pubsub)
    vault_pubsub_password=$(echo ${vault_pubsub_password_resp} | jq -r ".data.data.password")

    if [ -z ${vault_pubsub_password} ]; then
        echo "Failed to fetch cache password from vault. Exiting"
        exit 1
    fi

    echo "Updating pubsub password"
fi

exec /__cacert_entrypoint.sh "$@"
