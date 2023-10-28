# Download base image
FROM ubuntu:22.04 as ddx

# LABEL about the custom image
LABEL maintainer="Rupamjyoti Sarma Baruah <rbaruah@drio.ai>"
LABEL company="Drio Inc"
LABEL component="DDX"
LABEL version="0.2"
LABEL description="This is a custom Docker Image from Drio Inc for Distributed Data Exchange"

# Copy supervisor configuration
RUN apt-get -y update
RUN apt-get -y install openjdk-8-jre-headless
RUN apt-get -y install supervisor
RUN apt-get -y install python3-pip
RUN apt-get -y install python3.11
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf ${SUPERVISOR_CONF}

# Entry point
RUN mkdir -p /docker-entrypoint-ddx.d
COPY ${STREAM_ENGINE_JAR} /docker-entrypoint-ddx.d/${STREAM_ENGINE_JAR}
ADD ${DDX_AGENT} /docker-entrypoint-ddx.d/${DDX_AGENT}
RUN pip3 install -r /docker-entrypoint-ddx.d/${DDX_AGENT}/requirements.txt
CMD /usr/bin/supervisord -n -c ${SUPERVISOR_CONF}
