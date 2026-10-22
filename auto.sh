#!/bin/bash

docker build -t dashboard_image .

docker rm dashboard_app -f

./start-app.sh
