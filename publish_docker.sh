#!/bin/bash

# Build images
docker-compose build

# Login to GHCR (User needs to do this once: echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin)
echo "Pushing images to GHCR..."

# Push images
docker-compose push

echo "Successfully pushed images:"
echo " - ghcr.io/jih4855/docbridge-backend:latest"
echo " - ghcr.io/jih4855/docbridge-frontend:latest"
