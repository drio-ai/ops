FROM apache/kafka:3.7.1 AS driopubsub

LABEL maintainer="Sudarsan Raghavan <sraghavan@drio.ai>"
LABEL company="Drio Inc"
LABEL component="Drio Controller"

USER root
RUN apk add curl jq
USER appuser
COPY docker/init-pubsub.sh /
ENTRYPOINT [ "/init-pubsub.sh" ]
CMD [ "/etc/kafka/docker/run" ]
