#!/bin/sh

# Give redis some time to initialize
sleep 10

if [ -z ${VAULT_ADDR} ]; then
    echo "Did not find VAULT_ADDR in environment"
    exit 1
fi

if [ ! -z ${VAULT_ROLE_ID} ] && [ ! -z ${VAULT_SECRET_ID} ]; then
    echo "Vault login attempt..."
    vault_client_token_resp=$(curl --request POST --data "{\"role_id\": \"${VAULT_ROLE_ID}\", \"secret_id\": \"${VAULT_SECRET_ID}\"}" ${VAULT_ADDR}/v1/auth/approle/login)
    vault_client_token=$(echo ${vault_client_token_resp} | jq -r ".auth.client_token")

    if [ -z ${vault_client_token} ]; then
        echo "Vault login failed. Exiting"
        exit 1
    fi

    echo "Vault login was successful. Fetching cache password from vault..."
    vault_cache_password_resp=$(curl --header "X-Vault-Token: ${vault_client_token}" ${VAULT_ADDR}/v1/drio-controller/ops/data/cache)
    vault_cache_password=$(echo ${vault_cache_password_resp} | jq -r ".data.data.password")

    if [ -z ${vault_cache_password} ]; then
        echo "Failed to fetch cache password from vault. Exiting"
        exit 1
    fi

    echo "Updating cache password"
    redis-cli -h ${REDIS_HOST} config set requirepass ${vault_cache_password}
fi
