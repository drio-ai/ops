FROM node:lts-bookworm-slim AS drioui

LABEL maintainer="Sudarsan Raghavan <sraghavan@drio.ai>"
LABEL company="Drio Inc"
LABEL component="Drio Controller UI"

WORKDIR /root
RUN apt update -y && \
    apt install git -y && \
    npm install --global concurrently next
    
COPY docker/uistart.sh /
ENTRYPOINT ["/uistart.sh"]
