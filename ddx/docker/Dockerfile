# Download base image
FROM ubuntu:22.04 as ddx

# LABEL about the custom image
LABEL maintainer="Rupamjyoti Sarma Baruah <rbaruah@drio.ai>"
LABEL company="Drio Inc"
LABEL component="DDX"
LABEL version="0.2"
LABEL description="This is a custom Docker Image from Drio Inc for Distributed Data Exchange"

# Define the ENV variable
ENV BOOTSTRAP_SERVERS localhost:9092
ENV SCHEMA_REGISTRY http://localhost:8081

# Copy supervisor configuration
RUN apt-get -y update
RUN apt-get -y install openjdk-8-jre-headless
RUN apt-get -y install supervisor
RUN apt-get -y install python3-pip
RUN apt-get -y install python3.11
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Entry point
RUN mkdir -p /docker-entrypoint-ddx.d
COPY streaming-engine-0.0.1-SNAPSHOT-jar-with-dependencies.jar /docker-entrypoint-ddx.d/streaming-engine-0.0.1-SNAPSHOT-jar-with-dependencies.jar
ADD ddx_agent /docker-entrypoint-ddx.d/ddx_agent
RUN pip3 install -r /docker-entrypoint-ddx.d/ddx_agent/requirements.txt
CMD  ["bash", "-c", "supervisord -n -c /etc/supervisor/conf.d/supervisord.conf"]

