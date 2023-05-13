# Download base image
FROM ubuntu:22.04 as ddx

# LABEL about the custom image
LABEL maintainer="Rupamjyoti Sarma Baruah <rbaruah@drio.ai>"
LABEL company="Drio Inc"
LABEL component="DDX"
LABEL version="0.1"
LABEL description="This is a custom Docker Image from Drio Inc for Distributed Data Exchange"

# Copy supervisor configuration
RUN apt-get -y update
RUN apt-get -y install openjdk-8-jdk-headless
RUN apt-get -y install supervisor
RUN mkdir -p /var/log/supervisor
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Entry point
RUN mkdir -p /docker-entrypoint-ddx.d
COPY ${DDX_COMPILED_JAR} /docker-entrypoint-ddx.d/streaming-engine-0.0.1-SNAPSHOT-jar-with-dependencies.jar
CMD /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
