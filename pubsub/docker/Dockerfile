FROM apache/kafka:3.7.2 AS driopubsub

LABEL maintainer="Sudarsan Raghavan <sraghavan@drio.ai>"
LABEL company="Drio Inc"
LABEL component="Drio Controller"

USER root
RUN apk add curl jq
USER appuser
COPY docker/init-pubsub.sh /
COPY docker/kafka_server_jaas.conf /etc/kafka/kafka_server_jaas.conf
ENTRYPOINT [ "/init-pubsub.sh" ]
CMD [ "/etc/kafka/docker/run" ]
