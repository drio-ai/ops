#!/bin/sh

VAULT_AGENT_LISTEN_PORT=$1
VAULT_AGENT_TLS_DISABLE=$2
VAULT_AGENT_VAULT_URL=$3

mkdir -p /etc/vault
cat <<VAULT_AGENT_CONFIG >/etc/vault/config.hcl
pid_file = "/tmp/pidfile"

auto_auth {
  method "approle" {
    config = {
      role_id_file_path = "/etc/vault/role_id"
      secret_id_file_path = "/etc/vault/secret_id"
      remove_secret_id_file_after_reading = false
    }
  }

  sink "file" {
    config = {
      path = "/vault-agent-token"
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
