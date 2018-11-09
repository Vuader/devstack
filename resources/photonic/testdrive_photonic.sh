#!/bin/bash

curl -L -O https://github.com/TachyonicProject/devstack/raw/development/resources/photonic/Dockerfile
curl -L -O https://github.com/TachyonicProject/devstack/raw/development/resources/photonic/000-default.conf

docker build -t photonic:dev .
docker run -p 80:80 photonic:dev &

python -m webbrowser "http://localhost/ui"
