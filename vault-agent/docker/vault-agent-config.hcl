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
  address = "0.0.0.0:8100"
  tls_disable = true
}

vault {
  address = "http://vault:8200"
}

