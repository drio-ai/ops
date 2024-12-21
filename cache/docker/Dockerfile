FROM redis:7.4.1 AS drioredis

LABEL maintainer="Sudarsan Raghavan <sraghavan@drio.ai>"
LABEL company="Drio Inc"
LABEL component="Drio Controller"

RUN apt update -y && apt upgrade curl jq -y
COPY docker/redis.conf /usr/local/etc/redis/redis.conf
COPY docker/init-cache.sh /
CMD [ "redis-server", "/usr/local/etc/redis/redis.conf", "--save", "60", "1", "--loglevel", "warning" ]
