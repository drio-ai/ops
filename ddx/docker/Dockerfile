# =====================================
#         BUILDER STAGE
# =====================================
FROM ubuntu:22.04 AS builder

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3.12.2
ENV TZ=Etc/UTC

# Install build dependencies and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    git \
    wget \
    tzdata \
    nano \
    libffi-dev \
    gcc \
    unzip \
    ca-certificates && \
    update-ca-certificates && \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz --no-check-certificate && \
    tar -xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make -j "$(nproc)" && \
    make altinstall && \
    cd .. && rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tgz && \
    ln -sf /usr/local/bin/python3.12 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3 && \
    ln -sf /usr/local/bin/pip3.12 /usr/bin/pip && \
    pip3 install --upgrade pip setuptools && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ddx_agent/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    pip3 install --no-cache-dir git+https://github.com/drio-inc/PyMuPDF.git#egg=PyMuPDF spacy && \
    python3 -m spacy download en_core_web_trf

# Copy application files
COPY ddx_agent /docker-entrypoint-ddx.d/ddx_agent

# =====================================
#         FINAL RUNTIME IMAGE
# =====================================
FROM ubuntu:22.04 AS ddx

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV BOOTSTRAP_SERVERS=host.docker.internal:9092
ENV SCHEMA_REGISTRY=http://host.docker.internal:8081
ENV PYTHON_VERSION=3.12.2
ENV TZ=Etc/UTC
ENV PYTHONPATH=/docker-entrypoint-ddx.d/ddx_agent/resources:$PYTHONPATH

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-8-jre-headless \
    libssl-dev \
    zlib1g \
    libbz2-1.0 \
    libreadline8 \
    libffi8 \
    libsqlite3-0 \
    liblzma5 \
    wget \
    curl \
    git \
    tzdata \
    supervisor && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python binaries and dependencies from the builder stage
COPY --from=builder /usr/local/bin/python3.12 /usr/local/bin/python3.12
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin/pip3.12 /usr/local/bin/pip3.12
RUN ln -sf /usr/local/bin/python3.12 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3

# Copy application files
COPY --from=builder /docker-entrypoint-ddx.d /docker-entrypoint-ddx.d

# Copy supervisor configuration
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set the working directory
WORKDIR /docker-entrypoint-ddx.d/ddx_agent

# Install supervisor using Python 3.12
RUN python3.12 -m pip install supervisor

# Start supervisord to manage services
CMD ["bash", "-c", "supervisord -n -c /etc/supervisor/conf.d/supervisord.conf"]
