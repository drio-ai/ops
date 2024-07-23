#!/bin/sh

# This script should never be copied into the vault docker image

docker exec -t vault /bin/sh -c "VAULT_TOKEN=\$(jq -r .root_token /vault/tokens/root/secrets) vault kv get -field password -mount drio-controller/ops saas-admin@drio.ai"
