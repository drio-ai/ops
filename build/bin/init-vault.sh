#!/bin/sh

VAULT_CONFIG=/vault/config
VAULT_TOKENS=/vault/tokens
VAULT_POLICIES=/vault/policies

# Initialize vault
echo "Initializing vault"
init_output=$(curl --request POST --data "{\"secret_shares\":${VAULT_SECRET_SHARES},\"secret_threshold\":${VAULT_SECRET_THRESHOLD}}" http://127.0.0.1:8200/v1/sys/init)

# Get secrets and unseal vault
echo "Fetching secrets to unseal vault"
SECRET_INDICES=$(($VAULT_SECRET_SHARES-1))
for i in `seq 0 ${SECRET_INDICES}`; do
    secret=$(echo $init_output | jq -r ".keys[$i]")

    if [[ $i -lt ${VAULT_SECRET_THRESHOLD} ]]; then
        echo "Unsealing vault with secret $i"
        curl --request POST --data "{\"key\": \"${secret}\"}" http://127.0.0.1:8200/v1/sys/unseal
    fi
done

sealstatus=$(curl http://127.0.0.1:8200/v1/sys/seal-status)
initialized=$(echo $sealstatus | jq -r ".initialized")
sealed=$(echo $sealstatus | jq -r ".sealed")
echo "Vault initialized status ${initialized} and seal status ${sealed}"

echo "Saving root secrets"
echo ${init_output} >${VAULT_TOKENS}/root/secrets

VAULT_TOKEN=$(echo $init_output | jq -r ".root_token")
export VAULT_TOKEN

echo "Enabling secrets"
vault secrets enable -version=2 -path=drio-controller kv

echo "Setting password"
vault kv put drio-controller/postgres password=$(openssl rand -hex 12)

echo "Attaching policy"
vault policy write drio-controller-policy ${VAULT_POLICIES}/drio-controller-policy.json

echo "Enabling approle"
curl --header "X-Vault-Token: ${VAULT_TOKEN}" --request POST --data '{"type": "approle"}' http://127.0.0.1:8200/v1/sys/auth/approle

echo "Creating drio-controller-role approle role and attaching drio-controller-policy to it"
curl --header "X-Vault-Token: ${VAULT_TOKEN}" --request POST --data '{"policies": "drio-controller-policy"}' http://127.0.0.1:8200/v1/auth/approle/role/drio-controller-role

echo "Extracting approle role id for drio-controller-role"
approle_id_info=$(curl --header "X-Vault-Token: ${VAULT_TOKEN}" http://127.0.0.1:8200/v1/auth/approle/role/drio-controller-role/role-id)
approle_id=$(echo ${approle_id_info} | jq -r ".data .role_id")

echo "Extracting approle secret id for drio-controller-role"
approle_secret_id_info=$(curl --header "X-Vault-Token: ${VAULT_TOKEN}"  --request POST http://127.0.0.1:8200/v1/auth/approle/role/drio-controller-role/secret-id)
approle_secret_id=$(echo ${approle_secret_id_info} | jq -r ".data .secret_id")

echo "role_id: ${approle_id}" >${VAULT_TOKENS}/drio-controller/drio-controller-role.ids
echo "secret_id: ${approle_secret_id}" >>${VAULT_TOKENS}/drio-controller/drio-controller-role.ids
