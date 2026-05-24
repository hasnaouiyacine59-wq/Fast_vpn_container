#!/bin/bash
set -e

IMAGE_NAME="quay.io/mylastres0rt05_redhat/fast_bollete:latest"
QUAY_USER="mylastres0rt05_redhat"
QUAY_PASS="wOjrrx2UuxdPURIqbHFZlD2ZJifbBII7Xtpw40/o44iIWDvitL+rSs2kcR+8007p"

echo "Building image..."
docker build -f Dockerfile -t $IMAGE_NAME .

echo "Logging in to quay.io..."
echo $QUAY_PASS | docker login -u $QUAY_USER --password-stdin quay.io

echo "Pushing image to quay.io..."
docker push $IMAGE_NAME

echo "✅ Done! Image pushed to $IMAGE_NAME"
