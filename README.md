# Sortify
This repository contains code to show how machine learning models can be used to solve the problem of identifying different types of 
recyclable materials. It also show different types of plastics like PET 1, PET 2 etc.

This is created using [plotly dash](https://github.com/plotly/dash) for front end and Azure's [custom vision](https://www.customvision.ai/) service to tag and train models and [tensorflow python](https://www.tensorflow.org/learn) to predict.

The source code has been divided on to mainly two parts

    - models
        - plastic_type_classification - Image classification model
        - recycle_type_classification - Image classification model
        - recycle_type_object_detection - Object classification model
    - src
        - app.py - Main entry point and plotly UI components
        - predict_plastic_type_classification.py - Image classification prediction
        - predict_recycle_type_classification.py - Image classification prediction
        - predict_recycle_type_object_detection.py - Object classification prediction
    - Dockerfile

## Prerequisites 

Make sure docker is installed. More info [here](https://docs.docker.com/engine/install/) 

## Build & run locally

```bash
docker build -t sortify .

docker run -it -p 8080:8080 -e PORT=8080 sortify

```

After this app should be availabe on http://localhost:8080

If it doesn't work in one go, please refresh.

## How to build, modify code and run locally

```bash
docker build -t sortify .

docker run -it -v "/path/of/code/:/path/to/mount" -p 8080:8080 -e PORT=8080 sortify bash

cd path/to/mount

gunicorn --bind :8080 --chdir src/ app:server --reload

```

## How to push new image to docker (Make sure you are login to docker)

```bash
docker build -t docker-account-name/sortify .

docker push docker-account-name/sortify:latest

```