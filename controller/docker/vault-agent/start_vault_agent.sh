#!/bin/sh

VAULT_DIR=/etc/vault
VAULT_AGENT_DIR=${VAULT_DIR}/agent

# Source the environment variables from the file
. ${VAULT_DIR}/tokens/drio-controller-role.env

# Write the role_id and secret_id to separate files
echo -n "$DRIO_VAULT_ROLE_ID" > ${VAULT_AGENT_DIR}/role_id
echo -n "$DRIO_VAULT_SECRET_ID" > ${VAULT_AGENT_DIR}/secret_id
echo "Role ID and Secret ID have been written to ${VAULT_AGENT_DIR}/role_id and ${VAULT_AGENT_DIR}/secret_id"

# Write out vault agent configuration
cat <<VAULT_AGENT_CONFIG >${VAULT_AGENT_DIR}/config.hcl
pid_file = "/tmp/pidfile"

auto_auth {
  method "approle" {
    config = {
      role_id_file_path = "${VAULT_AGENT_DIR}/role_id"
      secret_id_file_path = "${VAULT_AGENT_DIR}/secret_id"
      remove_secret_id_file_after_reading = false
    }
  }

  sink "file" {
    config = {
      path = "${VAULT_AGENT_DIR}/token"
    }
  }
}

listener "tcp" {
  address = "0.0.0.0:${VAULT_AGENT_LISTEN_PORT}"
  tls_disable = ${VAULT_AGENT_TLS_DISABLE}
}

vault {
  address = "${VAULT_AGENT_VAULT_URL}"
}
VAULT_AGENT_CONFIG

# Start vault agent
exec vault agent -config=${VAULT_AGENT_DIR}/config.hcl
