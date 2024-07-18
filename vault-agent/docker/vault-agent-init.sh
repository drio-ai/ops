#!/bin/sh

# Source the environment variables from the file
. /etc/vault/tokens/drio-controller-role.env

# Write the role_id and secret_id to separate files
echo -n "$DRIO_VAULT_ROLE_ID" > /etc/vault/role_id
echo -n "$DRIO_VAULT_SECRET_ID" > /etc/vault/secret_id

# Optionally, print a success message
echo "Role ID and Secret ID have been written to /etc/vault/role_id and /etc/vault/secret_id"

