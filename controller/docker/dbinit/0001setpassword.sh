#!/bin/sh

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

    echo "Vault login was successful. Fetching DB password from vault..."
    vault_db_password_resp=$(curl --header "X-Vault-Token: ${vault_client_token}" ${VAULT_ADDR}/v1/drio-controller/ops/data/configdb)
    vault_db_password=$(echo ${vault_db_password_resp} | jq -r ".data.data.password")

    if [ -z ${vault_db_password} ]; then
        echo "Failed to fetch DB password from vault. Exiting"
        exit 1
    fi

    echo "Updating DB password"
    psql --command "ALTER USER postgres PASSWORD '${vault_db_password}';"
fi
