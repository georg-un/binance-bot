#!/bin/sh

{
  # try to start the container
  docker start postgres-dev
} || {
  # if we're unable to start it, try to create a new container
  docker pull postgres
  docker run --name some-postgres \
    --name postgres-dev \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -p 5432:5432 \
    -d postgres
}
