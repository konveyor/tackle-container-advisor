#!/bin/bash

echo "-----------Running the Backend API---------"

if [ "$( docker container inspect -f '{{.State.Status}}' tca_service_api )" == "running" ]; then
    docker stop tca_service_api
    docker rm tca_service_api
    docker rmi tca_service_api
fi

docker-compose  -f 'docker-compose-api.yml' up -d --build
