#!/bin/bash

docker build . -t bot

if [ -z "$1" ]
then
    docker compose up
    exit 0
elif [ $1 == "-d" ]
then
    docker compose up -d
    exit 0
fi
