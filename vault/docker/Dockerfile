FROM hashicorp/vault:1.13 AS vault

LABEL maintainer="Sudarsan Raghavan <sraghavan@drio.ai>"
LABEL company="Drio Inc"
LABEL component="Drio Key-Vault"

COPY docker/init-vault.sh /init-vault.sh
RUN apk update && \
    apk --no-cache add --update curl jq openssl && \
    rm -rf /var/cache/apk/*
