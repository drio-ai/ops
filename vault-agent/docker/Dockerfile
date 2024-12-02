FROM hashicorp/vault:1.13

LABEL maintainer="Rajat Gupta <rajat@geminustech.com>"
LABEL company="Drio Inc"
LABEL component="Drio Key-Vault"

COPY docker/vault-agent-config.hcl /etc/vault/
COPY docker/vault-agent-init.sh /vault-agent-init.sh

ENTRYPOINT ["vault", "agent", "-config=/etc/vault/vault-agent-config.hcl"]

