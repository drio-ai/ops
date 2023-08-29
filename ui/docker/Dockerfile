FROM node:lts AS drioui

LABEL maintainer="Sudarsan Raghavan <sraghavan@drio.ai>"
LABEL company="Drio Inc"
LABEL component="Drio Controller UI"

WORKDIR /root
RUN apt update -y && \
    npm install --global concurrently next
    
COPY docker/uistart.sh /
ENTRYPOINT ["/uistart.sh"]
