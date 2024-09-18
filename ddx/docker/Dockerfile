# =====================================
#         START OF BASE IMAGE
# =====================================
FROM ubuntu:22.04 AS ddx

# =====================================
#     LABEL CUSTOM IMAGE INFORMATION
# =====================================
LABEL maintainer="Rupamjyoti Sarma Baruah <rbaruah@drio.ai>"
LABEL company="Drio Inc"
LABEL component="DDX"
LABEL version="0.2"
LABEL description="This is a custom Docker Image from Drio Inc for Distributed Data Exchange"

# =====================================
#      SET ENVIRONMENT VARIABLES
# =====================================
ENV BOOTSTRAP_SERVERS=host.docker.internal:9092
ENV SCHEMA_REGISTRY=http://host.docker.internal:8081
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV PYTHON_VERSION=3.12.2

# =====================================
#  INSTALL REQUIRED PACKAGES & PYTHON
# =====================================
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y \
    openjdk-8-jre-headless \ 
    supervisor \ 
    build-essential \ 
    libssl-dev \ 
    zlib1g-dev \ 
    libncurses5-dev \ 
    libncursesw5-dev \ 
    libreadline-dev \ 
    libsqlite3-dev \ 
    libgdbm-dev \ 
    libdb5.3-dev \ 
    libbz2-dev \ 
    libexpat1-dev \ 
    liblzma-dev \ 
    tk-dev \ 
    curl \ 
    nano \ 
    tzdata \ 
    libffi-dev \ 
    gcc \ 
    git \ 
    unzip \ 
    wget && \ 
    curl -O https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \ 
    tar -xvzf Python-${PYTHON_VERSION}.tgz && \ 
    cd Python-${PYTHON_VERSION} && \ 
    ./configure --enable-optimizations && \ 
    make -j $(nproc) && \ 
    make altinstall && \ 
    cd .. && \ 
    rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tgz && \ 
    update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.12 1 && \
    /usr/local/bin/python3.12 -m pip install --upgrade pip && \ 
    rm -rf /var/lib/apt/lists/* 

# =====================================
#     VERIFY PYTHON INSTALLATION
# =====================================
RUN python3 --version

# =====================================
#   CONFIGURE SUPERVISOR & LOGS
# =====================================
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY supervisord.conf /etc/supervisor/supervisord.conf
RUN /usr/local/bin/python3.12 -m pip install supervisor # Install supervisor using Python

# =====================================
#  COPY STREAMING ENGINE & AGENT FILES
# =====================================
RUN mkdir -p /docker-entrypoint-ddx.d
COPY streaming-engine-0.0.1-SNAPSHOT-jar-with-dependencies.jar /docker-entrypoint-ddx.d/streaming-engine-0.0.1-SNAPSHOT-jar-with-dependencies.jar
ADD ddx_agent /docker-entrypoint-ddx.d/ddx_agent

# =====================================
#  INSTALL SPACY & DOWNLOAD MODELS
# =====================================
WORKDIR /docker-entrypoint-ddx.d/ddx_agent/stream_processors
RUN pip3 install spacy
RUN python3 -m spacy download en_core_web_trf

# =====================================
#  RETURN TO MAIN WORKING DIRECTORY
# =====================================
WORKDIR /docker-entrypoint-ddx.d/ddx_agent

# =====================================
# INSTALL DEPENDENCIES FROM requirements.txt
# =====================================
RUN /usr/local/bin/python3.12 -m pip install -r /docker-entrypoint-ddx.d/ddx_agent/requirements.txt

# =====================================
#  INSTALL PyMuPDF FROM GITHUB
# =====================================
RUN /usr/local/bin/python3.12 -m pip install git+https://github.com/drio-inc/PyMuPDF.git#egg=PyMuPDF

# =====================================
#       SET PYTHONPATH VARIABLE
# =====================================
ENV PYTHONPATH=/docker-entrypoint-ddx.d/ddx_agent/resources:$PYTHONPATH

# =====================================
# DOWNLOAD AND EXTRACT CONFIG FILES
# =====================================
WORKDIR /docker-entrypoint-ddx.d/ddx_agent/resources
RUN wget https://spacy-bertopic-config.s3.amazonaws.com/spacy_bertopic_pdfextract_config.tgz -O /docker-entrypoint-ddx.d/ddx_agent/resources/spacy_bertopic_pdfextract_config.tgz && \
    tar -zxvf /docker-entrypoint-ddx.d/ddx_agent/resources/spacy_bertopic_pdfextract_config.tgz -C /docker-entrypoint-ddx.d/ddx_agent/resources/ && \
    rm -f /docker-entrypoint-ddx.d/ddx_agent/resources/spacy_bertopic_pdfextract_config.tgz

# =====================================
# COMMENTED OUT: JOLOKIA & KAFKA SETUP
# =====================================
# Set environment variables for Jolokia (commented out)
# ENV JOLOKIA_VERSION="1.6.2"
# ENV JOLOKIA_HOME="/opt/jolokia"
# ENV JOLOKIA_AGENT="${JOLOKIA_HOME}/jolokia-jvm-${JOLOKIA_VERSION}-agent.jar"

# Download and install Jolokia agent (commented out)
# RUN mkdir -p ${JOLOKIA_HOME} && \
#     curl -L https://search.maven.org/remotecontent?filepath=org/jolokia/jolokia-jvm/${JOLOKIA_VERSION}/jolokia-jvm-${JOLOKIA_VERSION}-agent.jar -o ${JOLOKIA_AGENT}

# Expose Jolokia HTTP endpoint (commented out)
# EXPOSE 8778

# Expose JMX port (commented out)
# EXPOSE 9999

# Expose Kafka port (commented out)
# EXPOSE 9092

# Copy the Kafka configuration (commented out)
# COPY server.properties /etc/kafka/server.properties

# Start Kafka with Jolokia agent (commented out)
# CMD ["bash", "-c", "confluent start kafka; java -javaagent:${JOLOKIA_AGENT}=port=8778,host=0.0.0.0 -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=9999 -Dcom.sun.management.jmxremote.rmi.port=9999 -Dcom.sun.management.jmxremote.local.only=false -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=localhost"]

# =====================================
#   START SUPERVISOR IN FOREGROUND
# =====================================
WORKDIR /docker-entrypoint-ddx.d/
CMD ["bash", "-c", "supervisord -n -c /etc/supervisor/conf.d/supervisord.conf"]
