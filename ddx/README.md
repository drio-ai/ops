To build a ddx image:

  1. Edit the environtment/ddx.env file and populate appropriate values for the ENV vars.

  2. Run `make` cmd inside the ddx directory.


To publish a image to Docker Hub:

  1. Run `docker login` with user drioinc and cli access token as password.

  2. Run `docker push drioinc/ddx:latest`


To deploy a container using docker-compose:

  1. Edit the environtment/ddx.env file and populate appropriate values for the ENV vars.

  2. Run `docker-compose -f ddx.yml --env-file ../environment/ddx.env up -d`


To deploy a container using docker run:

  1. `docker run -ti --rm -d -e BOOTSTRAP_SERVERS='{kafka-host}:9092' -e SCHEMA_REGISTRY='http://{schema-registry-host}:8081' --name stream-processing-engine drioinc/ddx:latest

