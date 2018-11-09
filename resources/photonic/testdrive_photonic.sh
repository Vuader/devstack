#!/bin/bash

curl -L -O https://raw.githubusercontent.com/TachyonicProject/devstack/development/resources/photonic/resources/Dockerfile
curl -L -O https://raw.githubusercontent.com/TachyonicProject/devstack/development/resources/photonic/resources/000-default.conf

docker build -t photonic:dev .
docker run -p 80:80 photonic:dev &

python -m webbrowser "http://localhost/ui"
