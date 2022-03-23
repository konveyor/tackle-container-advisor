#!/bin/bash

echo "-----------Running the Backend API---------"

if [ "$( docker container inspect -f '{{.State.Status}}' aca_backend_api )" == "running" ]; then
    docker stop aca_backend_api
    docker rm aca_backend_api
    docker rmi aca_backend_api
fi

docker-compose  -f 'docker-compose-api.yml' up -d --build
