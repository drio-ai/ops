#!/bin/sh

# Sleep to make sure vault is fully up and running
sleep 10

VAULT_CONFIG=/vault/config
VAULT_TOKENS=/vault/tokens
VAULT_POLICIES=/vault/policies

if [ -z ${VAULT_ADDR} ]; then
    echo "Did not find VAULT_ADDR in environment"
    exit 1
fi

# Initialize vault
echo "Initializing vault"
init_output=$(curl --request POST --data "{\"secret_shares\":${VAULT_SECRET_SHARES},\"secret_threshold\":${VAULT_SECRET_THRESHOLD}}" ${VAULT_ADDR}/v1/sys/init)

# Get secrets and unseal vault
echo "Fetching secrets to unseal vault"
SECRET_INDICES=$(($VAULT_SECRET_SHARES-1))
for i in `seq 0 ${SECRET_INDICES}`; do
    secret=$(echo $init_output | jq -r ".keys[$i]")

    if [[ $i -lt ${VAULT_SECRET_THRESHOLD} ]]; then
        echo "Unsealing vault with secret $i"
        curl --request POST --data "{\"key\": \"${secret}\"}" ${VAULT_ADDR}/v1/sys/unseal
    fi
done

sealstatus=$(curl ${VAULT_ADDR}/v1/sys/seal-status)
initialized=$(echo $sealstatus | jq -r ".initialized")
sealed=$(echo $sealstatus | jq -r ".sealed")
echo "Vault initialized status ${initialized} and seal status ${sealed}"

echo "Saving root secrets"
echo ${init_output} >${VAULT_TOKENS}/root/secrets

VAULT_TOKEN=$(echo $init_output | jq -r ".root_token")
export VAULT_TOKEN

echo "Enabling secrets"
vault secrets enable -version=2 -path=drio-controller/ops kv
vault secrets enable -version=2 -path=drio-controller/user kv
vault secrets enable -version=2 -path=drio-controller/ddx kv

echo "Creating configdb password"
vault kv put drio-controller/ops/configdb password=$(openssl rand -hex 12)

echo "Creating pubsub password"
vault kv put drio-controller/ops/pubsub password=$(openssl rand -hex 12)

echo "Creating cache password"
vault kv put drio-controller/ops/cache password=$(openssl rand -hex 12)

echo "Creating controller admin password"
vault kv put drio-controller/ops/saas-admin@drio.ai password=$(openssl rand -hex 12)

echo "Creating controller admin oauth secrets"
vault kv put drio-controller/ops/oauth-client-id key=${SAAS_ADMIN_OAUTH_CLIENT_ID}
vault kv put drio-controller/ops/oauth-tenant-id key=${SAAS_ADMIN_OAUTH_TENANT_ID}
vault kv put drio-controller/ops/oauth-client-secret-id key=${SAAS_ADMIN_OAUTH_CLIENT_SECRET_ID}
vault kv put drio-controller/ops/oauth-client-secret key=${SAAS_ADMIN_OAUTH_CLIENT_SECRET}

echo "Creating secret key to secure JWT tokens"
vault kv put drio-controller/ops/saas-jwtkey key=$(openssl rand -hex 32)

# Add multiple versions of opsuser password. Will be used for testing
echo "Setting test password"
vault kv put drio-controller/ops/opsuser password=$(openssl rand -hex 12)
vault kv put drio-controller/ops/opsuser password=$(openssl rand -hex 12)
vault kv delete -mount drio-controller/ops opsuser
vault kv put drio-controller/ops/opsuser password=$(openssl rand -hex 12)

echo "Attaching policy"
vault policy write drio-controller-policy ${VAULT_POLICIES}/drio-controller-policy.json

echo "Enabling approle"
curl --header "X-Vault-Token: ${VAULT_TOKEN}" --request POST --data '{"type": "approle"}' ${VAULT_ADDR}/v1/sys/auth/approle

echo "Setting auth approle default TTL ${VAULT_AUTH_DEFAULT_TTL} and max TTL ${VAULT_AUTH_MAX_TTL}"
vault auth tune -default-lease-ttl=${VAULT_AUTH_DEFAULT_TTL} approle
vault auth tune -max-lease-ttl=${VAULT_AUTH_MAX_TTL} approle

echo "Creating drio-controller-role approle role and attaching drio-controller-policy to it"
curl --header "X-Vault-Token: ${VAULT_TOKEN}" --request POST --data '{"policies": "drio-controller-policy"}' ${VAULT_ADDR}/v1/auth/approle/role/drio-controller-role

echo "Extracting approle role id for drio-controller-role"
approle_id_info=$(curl --header "X-Vault-Token: ${VAULT_TOKEN}" ${VAULT_ADDR}/v1/auth/approle/role/drio-controller-role/role-id)
approle_id=$(echo ${approle_id_info} | jq -r ".data.role_id")

echo "Extracting approle secret id for drio-controller-role"
approle_secret_id_info=$(curl --header "X-Vault-Token: ${VAULT_TOKEN}"  --request POST ${VAULT_ADDR}/v1/auth/approle/role/drio-controller-role/secret-id)
approle_secret_id=$(echo ${approle_secret_id_info} | jq -r ".data.secret_id")

echo "DRIO_VAULT_ROLE_ID=${approle_id}" >${VAULT_TOKENS}/drio-controller/drio-controller-role.env
echo "DRIO_VAULT_SECRET_ID=${approle_secret_id}" >>${VAULT_TOKENS}/drio-controller/drio-controller-role.env
echo "Vault successfully initialized"
